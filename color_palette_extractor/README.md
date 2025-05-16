# Color Palette Extractor

**Author:** Amara Auguste  
**Date:** 04/20/2025

---

## Overview

The Color Palette Extractor is a user-friendly web application built with Flask that enables users to upload images and extract their color palettes. It provides two modes of operation:

- **Palette Mode:** Extracts the most dominant colors from the image.
- **Color Mode:** Filters and extracts colors within specific hue ranges based on user-selected colors.

The application displays the extracted colors as hex codes and generates an image palette for visual reference.

---

## Features

- Upload images via a web interface.
- Select between 'palette' and 'color' modes.
- For 'color' mode, choose from predefined hue-based color filters (e.g., red, blue, green).
- Extracts dominant colors using KMeans clustering.
- Filters colors based on saturation and brightness thresholds in 'color' mode.
- Displays color hex codes and generates a visual palette image.
- Saves original resized images and palettes for download.

---

## Requirements

- Python 3.x
- OpenCV (`cv2`)
- scikit-learn
- pandas
- numpy
- Flask

Install dependencies with pip:

```bash
pip install flask opencv-python scikit-learn pandas numpy
```

---

## Folder Structure

```
your_project/
│
├── color_palette_extractor.py (this script)
├── templates/
│   └── color_palette_extractor.html
├── uploads/             # For uploaded images
└── palettes/           # For generated palette images
```

Ensure the `templates/` folder contains `color_palette_extractor.html` for rendering results.

---

## Usage

1. **Run the application:**

```bash
python color_palette_extractor.py
```

2. **Open your browser:**

The app will automatically open at [http://127.0.0.1:5000/](http://127.0.0.1:5000/).

3. **Upload an image:**

- Choose a mode (`palette` or `color`).
- If in `color` mode, select a target color (e.g., red, blue).
- Click **Upload** and wait for processing.

4. **View results:**

- The original image is saved in `uploads/`.
- The generated color palette image appears in `palettes/`.
- Hex codes of the extracted colors are displayed on the page.

---

## Customization & Notes

- **Color Filtering:** Modify `COLOR_HUE_RANGES` in `app.py` to add or adjust color filters.
- **Thresholds:** Adjust saturation (`MIN_SATURATION`) and brightness (`MIN_VALUE`) thresholds as needed.
- **Performance:** Resizing images to a width of 400 pixels speeds up processing.
- **Limitations:** Small or low-contrast images may produce limited results.

---

## License

This project is provided as-is for educational and personal use. Feel free to modify and extend.

---

## Contact

For questions or contributions, please contact the author.

---

**Enjoy extracting beautiful color palettes!**
