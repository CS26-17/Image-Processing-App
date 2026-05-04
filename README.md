# Image Processing App

A modern, cross-platform desktop application for image editing and CNN-based image similarity analysis, built with PySide6.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![PySide6](https://img.shields.io/badge/PySide6-6.5+-green.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)

## Features

- **Drag & Drop Support** - Drag images directly onto the application window
- **Multiple Image Formats** - Supports PNG, JPG, JPEG, GIF, BMP, TIFF, WEBP
- **Image Editing** - Filters (blur, sharpen, emboss), brightness/contrast/saturation adjustments, undo/redo
- **CNN-Based Analysis** - Extract visual features using VGG16 or ResNet50 and compute pairwise image similarity
- **Results Visualization** - Similarity heatmaps and interactive CSV export
- **Themes** - Light, Dark, and Forest themes
- **Cross-Platform** - Runs on Windows, macOS, and Linux

## Quick Start

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/CS26-17/Image-Processing-App.git
   cd Image-Processing-App
   ```

2. **Set up the environment**

   On macOS/Linux:
   ```bash
   chmod +x setup_dev_env.sh
   ./setup_dev_env.sh
   ```

   On Windows:
   ```bat
   setup_dev_env.bat
   ```

3. **Run the application**
   ```bash
   source .venv/bin/activate   # On Windows: .venv\Scripts\activate
   python image_processing_app.py
   ```

### One-Command Launch

These scripts create the virtual environment, install dependencies, and launch the app in a single step — no prior setup needed:

On macOS/Linux:
```bash
bash scripts/launch_mac_linux.sh
```

On Windows:
```bat
scripts\launch_windows.bat
```

### Manual Setup

```bash
python3 -m venv .venv
source .venv/bin/activate     # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
python image_processing_app.py
```

## Packaging

### macOS — Build a standalone `.app` bundle

First make sure the virtual environment exists (run `setup_dev_env.sh` if not):

```bash
bash scripts/build_macos.sh
```

This script will:
1. Activate the `.venv` virtual environment
2. Install/upgrade PyInstaller
3. Clean any previous `build/` and `dist/` directories
4. Run PyInstaller using `image_processing_app.spec`
5. Output the app bundle to `dist/Image Processing App.app`

> **Note:** The build takes a few minutes due to the size of the PyTorch dependencies.

**Optional: create a `.dmg` installer**

If [`create-dmg`](https://github.com/create-dmg/create-dmg) is installed, the build script will automatically wrap the `.app` in a distributable DMG:

```bash
brew install create-dmg
bash scripts/build_macos.sh
# Output: dist/ImageProcessingApp.dmg
```

### Windows — Build a standalone executable folder

First make sure the virtual environment exists (run `setup_dev_env.bat` if not):

1. **Activate the environment and install PyInstaller**
   ```bat
   venv\Scripts\activate
   pip install pyinstaller
   ```

2. **Run the build**
   ```bat
   pyinstaller image_processing_app.spec
   ```

This will:
1. Collect all dependencies (PyTorch, PySide6, etc.) into a single folder
2. Output the distributable to `dist\Image Processing App\`

> **Note:** The build takes a few minutes due to the size of the PyTorch dependencies.

**To run the built app:**
```bat
"dist\Image Processing App\Image Processing App.exe"
```

**To distribute:** zip up the entire `dist\Image Processing App\` folder and share it. The recipient does not need Python installed.

> **Optional:** wrap the folder in an installer using a tool like [Inno Setup](https://jrsoftware.org/isinfo.php) or [NSIS](https://nsis.sourceforge.io/) for a polished `.exe` installer.

## How to Use

1. Launch the application
2. **Upload** images via drag-and-drop or the Upload button (Home tab)
3. **Edit** images using filters and adjustments (Edit tab)
4. **Analyze** a folder of images for similarity using VGG16 or ResNet50 (Analyze tab)
5. **View results** as a heatmap and export similarity data as CSV (Results tab)

## Technical Details

### Built With

- **PySide6** - Cross-platform Qt6 GUI framework
- **PyTorch + torchvision** - Pre-trained CNN models (VGG16, ResNet50)
- **Pillow** - Image I/O and processing
- **NumPy / pandas** - Numerical computation and data handling
- **matplotlib / seaborn** - Heatmap visualization
- **scikit-learn** - Cosine similarity for feature vectors
- **PyInstaller** - Standalone app packaging

### Project Structure

```
image-processing-app/
├── image_processing_app.py       # Main application entry point
├── run_models.py                 # CNN feature extraction and similarity computation
├── requirements.txt              # Runtime dependencies
├── requirements-dev.txt          # Development dependencies
├── image_processing_app.spec     # PyInstaller build spec
├── setup_dev_env.sh              # Environment setup (macOS/Linux)
├── setup_dev_env.bat             # Environment setup (Windows)
├── scripts/
│   ├── launch_mac_linux.sh       # One-command launch (macOS/Linux)
│   ├── launch_windows.bat        # One-command launch (Windows)
│   └── build_macos.sh            # Package as macOS .app / .dmg
├── tabs/                         # Tab UI modules
├── hooks/                        # PyInstaller runtime hooks
├── tests/                        # Tests
└── .venv/                        # Virtual environment (not in repo)
```

### Code Architecture

- MVC-inspired pattern with a modular tab-based structure
- Event-driven design using Qt signals/slots
- CNN analysis runs in a subprocess to keep the UI responsive

## Contributing

Pull requests and issues are welcome.

## License

This project is open source and available under the MIT License.
