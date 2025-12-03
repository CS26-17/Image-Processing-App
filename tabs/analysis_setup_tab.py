"""
Analysis Setup Tab - Configure analysis parameters and settings
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QLineEdit, QButtonGroup, QFileDialog)
from PySide6.QtCore import Qt
# import numpy as np
import os
# import torch
# import torchvision.models as models
# import torchvision.transforms as transforms
from PIL import Image
# from sklearn.metrics.pairwise import cosine_similarity
# import seaborn as sns
# import matplotlib.pyplot as plt
# import pandas as pd

class AnalysisSetupTab(QWidget):
    """
    Analysis Setup tab widget for configuring analysis parameters
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_folder = ""
        self.selected_model = None
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the analysis setup tab UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        
        analysis_label = QLabel("Analysis Configuration")
        analysis_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        analysis_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #2c3e50; margin: 20px;")
        layout.addWidget(analysis_label)
        
        # Create main analysis layout
        analysis_widget = QWidget()
        analysis_layout = QVBoxLayout(analysis_widget)
        
        # Model selection section
        model_layout = QHBoxLayout()
        model_label = QLabel("Select Model:")
        model_label.setStyleSheet("font-size: 14px; margin-right: 10px;")
        
        self.vg_button = QPushButton("VGG16")
        self.res_button = QPushButton("ResNet50")
        for btn in (self.vg_button, self.res_button):
            btn.setCheckable(True)
            btn.setStyleSheet("""QPushButton{
                                font-size: 15px; 
                                border: none; 
                                border-radius: 6px;
                                background-color: #52ba59; 
                                padding: 12px 24px;
                                color: white;
                              }
                              QPushButton:hover{
                                background-color: #45a84c;
                              }
                              QPushButton:checked{
                                background-color: #24752a; 
                              }
                              """)
        button_group = QButtonGroup(self)
        button_group.setExclusive(True)
        button_group.addButton(self.vg_button)
        button_group.addButton(self.res_button)
        #Documentation button
        doc1_btn = QPushButton("?")
        doc1_btn.setFixedSize(20, 20)
        doc1_btn.setStyleSheet("""
            QPushButton{
               font-size: 15px;
               border: 2px solid blue;
               border-radius: 10px;
               color: blue;            
            }
            QPushButton:hover{
               border: 2px solid #6971f5;
               color: #6971f5;            
            }                    
        """)
        doc1_btn.setToolTip("Choose which CNN model you want to do the comparisons on your \n images." \
        " Both models are built on PyTorch and are trained on ImageNet data.")
        #adding widget to the page
        model_layout.addWidget(model_label)
        model_layout.addWidget(self.vg_button)
        model_layout.addWidget(self.res_button)
        model_layout.addWidget(doc1_btn)
        model_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        analysis_layout.addLayout(model_layout)

        #choose folder
        folder_layout = QHBoxLayout()
        folder_label = QLabel("Select Image Folder")
        self.folder_button = QPushButton("Browse...")
        self.folder_button.setStyleSheet("""
          QPushButton{
            font-size: 14px;
            background-color: #8888ff;
            padding: 8px 18px;
            color: white;
            border-radius: 6px;                             
          }
          QPushButton:hover{
            background-color: #5555ff;
          }
        """)
        self.folder_button.clicked.connect(self.browse_folder)
        folder_layout.addWidget(folder_label)
        folder_layout.addWidget(self.folder_button)
        folder_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        analysis_layout.addLayout(folder_layout)
        #Setting up user file name choice input field
        name_layout = QHBoxLayout()
        name_label = QLabel("Name for result files: ")
        name_label.setStyleSheet("font-size: 14px; margin-right: 10px;")
        self.name_input = QLineEdit()
        self.name_input.setFixedWidth(200)
        self.name_input.setPlaceholderText("ex: Experiment1")
        self.name_input.setStyleSheet("""
          QLineEdit{
            font-size: 14px;
            border: 2px solid black;
            padding: 3px;
          }""")
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_input)
        name_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        #Documentation button
        doc2_btn = QPushButton("?")
        doc2_btn.setFixedSize(20, 20)
        doc2_btn.setStyleSheet("""
            QPushButton{
               font-size: 15px;
               border: 2px solid blue;
               border-radius: 10px;
               color: blue;            
            }
            QPushButton:hover{
               border: 2px solid #6971f5;
               color: #6971f5;            
            }                   
        """)
        doc2_btn.setToolTip("Enter the name that you want all of your analysis" \
        "result files to use. \n Files will include the raw data as a csv file, a heatmap \n" \
        " image, and more")
        
        name_layout.addWidget(doc2_btn)
        name_widget = QWidget()
        name_widget.setLayout(name_layout)
        analysis_layout.addWidget(name_widget, alignment=Qt.AlignmentFlag.AlignHCenter)

        apply_layout = QHBoxLayout()
        self.apply_button = QPushButton("Apply")
        self.apply_button.setStyleSheet("""QPushButton{
                                font-size: 15px; 
                                border: none; 
                                border-radius: 6px;
                                background-color: #202af5; 
                                padding: 12px 24px;
                                color: white;
                              }
                              QPushButton:hover{
                                background-color: #040ed1;
                              }
                              QPushButton:checked{
                                background-color: #010885; 
                              }
                              """)
        self.apply_button.clicked.connect(self.on_apply)
        apply_layout.addWidget(self.apply_button)
        apply_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
       
        analysis_layout.addLayout(apply_layout)
        analysis_widget.setObjectName("analysis_widget")

        #status label
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.status_label.setStyleSheet("font-size: 14px; color: #333333; margin-top: 15px;")
        analysis_layout.addWidget(self.status_label)
        
        # Add the analysis widget to the main layout
        layout.addWidget(analysis_widget)
        layout.addStretch()
    
    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Image Folder")
        if folder:
            self.selected_folder = folder
            self.status_label.setText(f"Selected folder: {folder}")

    def run_cnn_analysis(self, model_name, folder, result_name):
        images, image_names = self.load_images(folder)
        if len(images) == 0:
           raise ValueError("No .jpg images")
        model = self.load_model(model_name)
        features = self.extract_features(model, images)
        df, sim_matrix = self.compute_pairwise_similarity(features, image_names)
        csv_path = os.path.join(folder, f"{result_name}_similarity.csv")
        heat_path = os.path.join(folder, f"{result_name}_heatmap.png")
        self.save_to_csv(df, csv_path)
        self.generate_heatmap(df, heat_path)
    
    def load_images(self, image_path):
      '''
          goes through all the files in folder, converts them to 
          greyscale and processes them to be used for the models
      '''
      images = []
      image_names = []
      for filename in os.listdir(image_path):
          if filename.lower().endswith(('.jpg')):
              img_path = os.path.join(image_path, filename)
              img = Image.open(img_path).convert("L")#converting image to greyscale
              img = img.convert("L")
              img = np.array(img)#converting from pillow obj to NumPy array
              img_3ch = np.stack([img, img, img], axis=-1)#duplicating channels
              img_3ch = Image.fromarray(img_3ch.astype(np.uint8)) #converting back to pillow obj
              images.append(img_3ch)
              image_names.append(filename)
      return images, image_names
    
    def get_transform(self):
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
    
    def load_model(self, model_name):
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
      

    def extract_features(self, model, images):
      transform = self.get_transform()
      features = []
      for img in images:
          img_t = transform(img).unsqueeze(0)#adding a batch dimension
          with torch.no_grad():#disables gradient computation
              feat = model(img_t)
              feat = feat.view(feat.size(0), -1)#making output a 1D vector
              features.append(feat.numpy()[0]) #changing it into a numpy array and appending to features
      return np.array(features)
    

    def compute_pairwise_similarity(self, features, image_names):
      sim_matrix = cosine_similarity(features)
      df = pd.DataFrame(sim_matrix, index=image_names, columns=image_names)
      return df, sim_matrix
    

    def save_to_csv(self, df, output_path):
      df.to_csv(output_path, index=True)


    def generate_heatmap(self, df, output_path):
      plt.figure(figsize=(10, 8))
      sns.heatmap(df, annot=False, cmap="coolwarm", xticklabels=True, yticklabels=True)
      plt.title("Pairwise Image Similarity Heatmap", fontsize=14)
      plt.tight_layout()
      plt.savefig(output_path, dpi=300)
      plt.close()


    def image_comparison(self, model_name, image_path, heat_name, csv_name):
      images, image_names = self.load_images(image_path)
      model = self.load_model(model_name)
      features = self.extract_features(model, images)
      df, sim_matrix = self.compute_pairwise_similarity(features, image_names)
      self.save_to_csv(df, f'{csv_name}.csv')
      self.generate_heatmap(df, f'{heat_name}.png')
      labels = self.extract_labels(image_names)
      #labels = image_names
      accuracy = self.category_similarity_accuracy(sim_matrix, labels)
      print(f"Category Similarity Accuracy: {accuracy:.3f}")


    def extract_labels(self, image_names):
      return np.array([name.split(".")[1][:4] for name in image_names])
    

    def category_similarity_accuracy(self, sim_matrix, labels):
      same_class_sims = []
      diff_class_sims = []
      n = len(labels)
      for i in range(n):
          for j in range(i+1, n):
              if labels[i] == labels[j]:
                  same_class_sims.append(sim_matrix[i, j])
              else:
                  diff_class_sims.append(sim_matrix[i, j])
      threshold = np.median(diff_class_sims)
      correct = sum(sim > threshold for sim in same_class_sims)
      accuracy = correct / len(same_class_sims)
      return accuracy
    

    def on_apply(self):
        if self.vg_button.isChecked():
            model_name = "vgg16"
        elif self.res_button.isChecked():
            model_name = "resnet50"
        else:
            self.status_label.setText("Please select a model")
            return
        if not self.selected_folder:
            self.status_label.setText("Please select an image folder")
            return
        result_name = self.name_input.text().strip()
        if not result_name:
            self.status_label.setText("Enter name for result files")
            return
        self.status_label.setText("Running analysis...")
        try:
            self.run_cnn_analysis(model_name, self.selected_folder, result_name)
            self.status_label.setText("Analysis Complete")
        except Exception as e:
            self.status_label.setText(f"Error: {e}")

      