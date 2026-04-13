import argparse
import numpy as np
import os
import torch
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image
from sklearn.metrics.pairwise import cosine_similarity
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
from tqdm import tqdm
import sys

#hard coded output directory for the analysis results
OUTPUT_DIR = os.environ.get("OUTPUT_DIR", os.path.join(os.getcwd(), "results"))

def load_images(image_path):
    '''
        goes through all the files in folder, converts them to 
        greyscale and processes them to be used for the models
    '''
    images = []
    image_names = []
    valid_exts = ('.jpg', '.jpeg', '.png', '.gif')
    for filename in os.listdir(image_path):
        if not filename.lower().endswith(valid_exts):
            continue
        img_path = os.path.join(image_path, filename)
        # Skip subdirectories (e.g. the results/ folder inside the image folder)
        if not os.path.isfile(img_path):
            continue
        try:
            img = Image.open(img_path)
            if getattr(img, "is_animated", False):
                img.seek(0)
            img = img.convert("RGB")
            img = img.convert("L")  # converting image to greyscale
            img = np.array(img)  # converting from pillow obj to NumPy array
            img_3ch = np.stack([img, img, img], axis=-1)  # duplicating channels
            img_3ch = Image.fromarray(img_3ch.astype(np.uint8))  # converting back to pillow obj
            images.append(img_3ch)
            image_names.append(filename)
        except Exception as e:
            print(f"Warning: skipping {filename} - {e}", flush=True)
    return images, image_names

def get_transform():
    '''
        processes image by resizing it to 224x224, converting it 
        to a PyTorch tensor (data structure used in deep learning), and 
        normalizes the image using ImageNet mean and std values

    '''
    return transforms.Compose([transforms.Resize((224, 224)),
                            transforms.ToTensor(),
                            transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                                    std=[0.229, 0.244, 0.225])
    ])

def load_model(model_name):
    '''
        Trains model that has been chosen by the user. Models are trained on Imagenet images.

    '''
    if model_name == 'vgg16':
        model = models.vgg16(weights=models.VGG16_Weights.IMAGENET1K_V1)
        model.eval()#turns off batch normalization updates
        #returning feature vectors
        return torch.nn.Sequential(model.features, torch.nn.AdaptiveAvgPool2d((7, 7)), torch.nn.Flatten(), model.classifier[0] )
    elif model_name == 'resnet50':
        model = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V1)
        model.eval()
        return torch.nn.Sequential(*(list(model.children())[:-1]), torch.nn.Flatten())
    else:
        raise ValueError("Not an available model.")
    
def extract_features(model, images, queue=None):
    transform = get_transform()
    features = []
    total = len(images)
    for i, img in enumerate(tqdm(images, desc="Extracting features"), 1):
        img_t = transform(img).unsqueeze(0)#adding a batch dimension
        with torch.no_grad():#disables gradient computation
            feat = model(img_t)
            feat = feat.view(feat.size(0), -1)#making output a 1D vector
            features.append(feat.numpy()[0]) #changing it into a numpy array and appending to features
        progress = int((i/total) * 100)
        if queue is not None:
            queue.put(("PROGRESS", progress))
        else:
            print(f"PROGRESS:{progress}", flush=True)
    return np.array(features)

def run_cnn_analysis_worker(model_name, folder, result_name, output_dir, queue):
    """
    Multiprocessing-compatible entry point for CNN analysis.
    Reports progress and completion/errors via queue instead of stdout,
    which works correctly in both development and frozen/packaged builds.
    """
    try:
        images, image_names = load_images(folder)
        if len(images) == 0:
            queue.put(("ERROR", "No images found in the selected folder."))
            return
        model = load_model(model_name)
        features = extract_features(model, images, queue=queue)
        sim_matrix = cosine_similarity(features)
        df = pd.DataFrame(sim_matrix, index=image_names, columns=image_names)

        os.makedirs(output_dir, exist_ok=True)
        csv_path = os.path.join(output_dir, f"{result_name}_similarity.csv")
        heat_path = os.path.join(output_dir, f"{result_name}heatmap.png")

        df.to_csv(csv_path)
        plt.figure(figsize=(10, 8))
        sns.heatmap(df, cmap="coolwarm")
        plt.tight_layout()
        plt.savefig(heat_path, dpi=300)
        plt.close()

        queue.put(("DONE", output_dir))
    except Exception as e:
        queue.put(("ERROR", str(e)))


def compute_pairwise_similarity(features, image_names):
    sim_matrix = cosine_similarity(features)
    df = pd.DataFrame(sim_matrix, index=image_names, columns=image_names)
    return df, sim_matrix


#currently only accepts jpg, need to add other file types
def run_cnn_analysis(model_name, folder, result_name):
    images, image_names = load_images(folder)
    if len(images) == 0:
        raise ValueError("No images found")
    #running analysis
    model = load_model(model_name)
    features = extract_features(model, images)
    sim_matrix = cosine_similarity(features)
    #creating dataframe of the results
    df = pd.DataFrame(sim_matrix, index=image_names, columns=image_names)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    #outputting the result files
    csv_path = os.path.join(OUTPUT_DIR, f"{result_name}_similarity.csv")
    heat_path = os.path.join(OUTPUT_DIR, f"{result_name}heatmap.png")

    df.to_csv(csv_path)
    plt.figure(figsize=(10, 8))
    sns.heatmap(df, cmap="coolwarm")
    plt.tight_layout()
    plt.savefig(heat_path, dpi=300)
    plt.close()
    print("Analysis completed successfully")
    # with open(os.path.join(OUTPUT_DIR, "SUCCESS.txt"), "w") as f:
    #     f.write("Analysis completed successfully\n")
def save_to_csv(df, output_path):
    df.to_csv(output_path, index=True)

def generate_heatmap(df, output_path):
    plt.figure(figsize=(10, 8))
    sns.heatmap(df, annot=False, cmap="coolwarm", xticklabels=True, yticklabels=True)
    plt.title("Pairwise Image Similarity Heatmap", fontsize=14)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()


def extract_labels(image_names):
    return np.array([name.split(".")[1][:4] for name in image_names])
    

if __name__ == "__main__":
    #Receiving the arguments from user's input on GUI
    p = argparse.ArgumentParser()
    p.add_argument("--model")
    p.add_argument("--folder")
    p.add_argument("--name")
    args = p.parse_args()
    run_cnn_analysis(args.model, args.folder, args.name)