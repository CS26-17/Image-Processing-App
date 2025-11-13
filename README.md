# Image Processing App

A modern, user-friendly image processing application built with PyQt5, featuring intuitive drag-and-drop functionality and a professional interface.

![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)
![PyQt5](https://img.shields.io/badge/PyQt5-5.15+-green.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)

## ✨ Features

- 🖱️ **Drag & Drop Support** - Simply drag images directly onto the application window
- 📁 **Multiple Image Formats** - Supports PNG, JPG, JPEG, GIF, BMP, TIFF, WEBP
- 🎨 **Modern UI** - Clean, professional interface with tabbed navigation
- ⚡ **Instant Preview** - Real-time image display with auto-scaling
- 🔄 **Easy Upload** - Traditional file dialog upload option
- 🖼️ **Image Processing Ready** - Foundation built for future image analysis features
- 🌐 **Cross-Platform** - Runs seamlessly on Windows, macOS, and Linux

## 🚀 Quick Start

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/CS26-17/Image-Processing-App.git
   cd Image-Processing-App

2. **Set up the environment**

For macOS/Linux:

bash
chmod +x setup_dev_env.sh
./setup_dev_env.sh

For Windows:

bash
setup_dev_env.bat
Run the application

bash
python hello_world_app.py
Manual Setup (Alternative)
If you prefer to set up manually:

bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python hello_world_app.py
🎯 How to Use
Launch the application

Upload an image using either:

Drag & Drop: Drag any supported image file directly onto the application window

Upload Button: Click "Upload Image" to select a file through the file dialog

View your image in the preview area

Use additional features through the tabbed interface:

Home: Main image upload and display

Results: Processing results (future feature)

Documentation: Application guides (future feature)

Modification: Image editing tools (future feature)

Analysis Setup: Configuration settings (future feature)

🛠️ Technical Details
Built With
PyQt5 - Cross-platform GUI toolkit

Python 3 - Backend logic and processing

Pillow - Image processing capabilities

Project Structure
text
Image-Processing-App/
├── hello_world_app.py    # Main application file
├── requirements.txt      # Python dependencies
├── setup_dev_env.sh     # macOS/Linux setup script
├── setup_dev_env.bat    # Windows setup script
├── README.md            # This file
└── venv/                # Virtual environment (local, not in repo)
Dependencies
PyQt5 >= 5.15.0

Pillow >= 10.0.0

(Additional dependencies can be added in requirements.txt)

🎨 Interface Overview
The application features a clean, tabbed interface:

Home Tab: Primary workspace for image upload and display

Visual Feedback: Clear status messages and drag-drop indicators

Responsive Design: Adapts to different screen sizes

Professional Styling: Modern color scheme and intuitive layout

🔧 Development
Adding New Features
The modular code structure makes it easy to extend functionality:

New image processing features can be added to the existing methods

Additional tabs can be implemented following the existing pattern

UI enhancements can be made through the Qt stylesheet system

Code Architecture
MVC-inspired pattern with separation of concerns

Event-driven design for responsive user interactions

Comprehensive error handling for robust operation

🤝 Contributing
We welcome contributions! Please feel free to submit pull requests or open issues for bugs and feature requests.

📝 License
This project is open source and available under the MIT License.

🙏 Acknowledgments
Built with PyQt5 for the GUI framework

Icons and emojis used for enhanced user experience

Inspired by modern image processing applications

