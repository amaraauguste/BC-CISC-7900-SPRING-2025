'''
Amara Auguste
Color Palette Extractor
04/20/2025

This script is a Flask web application that allows users to upload an image and extract a color palette from it. 
The user can choose between two modes: 
    - 'palette' mode, which extracts the most dominant colors, and 'color' mode, which filters colors based on predefined hue ranges
     
The extracted colors are displayed as hex codes and saved as an image palette.
The application uses OpenCV for image processing, scikit-learn for KMeans clustering, and Flask for the web interface. 
The user can upload an image, select a mode, and view the resulting color palette.

'''
from flask import Flask, request, render_template, send_from_directory
import webbrowser
import threading
import cv2
import pandas as pd
import numpy as np
import os
from sklearn.cluster import KMeans

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['PALETTE_FOLDER'] = 'palettes/'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['PALETTE_FOLDER'], exist_ok=True)

# Define hue ranges for color filtering
COLOR_HUE_RANGES = {
    'pink': [(150, 170)],
    'red': [(0, 10), (170, 179)],
    'orange': [(11, 25)],
    'yellow': [(26, 34)],
    'green': [(35, 85)],
    'cyan': [(86, 100)],
    'blue': [(101, 130)],
    'purple': [(131, 149)],
}

# Thresholds for excluding black/gray/white in color mode
MIN_SATURATION = 50
MIN_VALUE = 50

def process_image(image_path, mode='palette', target_color=None):
    # Load original image
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError("Invalid image path or corrupted image.")
    
    # Resize for faster processing
    height, width = img.shape[:2]
    aspect_ratio = width / height
    new_width = 400
    new_height = int(new_width / aspect_ratio)
    img_resized = cv2.resize(img, (new_width, new_height))
    
    hsv_img = cv2.cvtColor(img_resized, cv2.COLOR_BGR2HSV)
    mask = np.ones((new_height, new_width), dtype=bool)

    # Filter by hue if in 'color' mode with target_color
    if mode == 'color' and target_color:
        hue_ranges = COLOR_HUE_RANGES.get(target_color.lower())
        if hue_ranges:
            combined_mask = np.zeros((new_height, new_width), dtype=bool)
            for (h_min, h_max) in hue_ranges:
                if h_min <= h_max:
                    current_mask = (hsv_img[:, :, 0] >= h_min) & (hsv_img[:, :, 0] <= h_max)
                else:
                    current_mask = (hsv_img[:, :, 0] >= h_min) | (hsv_img[:, :, 0] <= h_max)
                combined_mask = combined_mask | current_mask
            mask = combined_mask
        else:
            return ["No colors found for the selected mode and color."]

    # Collect pixels based on mask
    pixels = []
    for y in range(new_height):
        for x in range(new_width):
            if mask[y, x]:
                b, g, r = img_resized[y, x]
                pixels.append([b, g, r])

    if not pixels:
        return ["No colors found for the selected mode and color."]

    # Handle very few pixels
    if len(pixels) < 10:
        unique_colors = [list(x) for x in set(tuple(p) for p in pixels)]
        hex_codes = ["#{:02x}{:02x}{:02x}".format(int(c[2]), int(c[1]), int(c[0])) for c in unique_colors]
        save_palette_and_return(hex_codes, img_resized, mode, target_color, image_path)
        return hex_codes

    # Clustering
    n_clusters = min(8, len(pixels))
    df = pd.DataFrame(pixels, columns=['B', 'G', 'R'])
    km = KMeans(n_clusters=n_clusters, init='k-means++', n_init=10)
    km.fit(df.values)
    centers_bgr = np.array(km.cluster_centers_, dtype=np.uint8)

    centers_hsv = cv2.cvtColor(centers_bgr.reshape(-1, 1, 3), cv2.COLOR_BGR2HSV).reshape(-1, 3)

    relevant_centers = []
    relevant_hex_codes = []

    for i, (b, g, r) in enumerate(centers_bgr):
        h, s, v = centers_hsv[i]
        include_center = True

        if mode == 'color':
            # Filter based on saturation and value
            if s < MIN_SATURATION or v < MIN_VALUE:
                include_center = False
            # Check hue range if target_color specified
            if target_color:
                hue_ranges = COLOR_HUE_RANGES.get(target_color.lower())
                hue_match = False
                if hue_ranges:
                    for (h_min, h_max) in hue_ranges:
                        if h_min <= h_max:
                            if h >= h_min and h <= h_max:
                                hue_match = True
                                break
                        else:
                            if h >= h_min or h <= h_max:
                                hue_match = True
                                break
                if not hue_match:
                    include_center = False

        # For 'palette' mode, include all centers
        if include_center:
            relevant_centers.append([b, g, r])
            hex_code = "#{:02x}{:02x}{:02x}".format(int(r), int(g), int(b))
            relevant_hex_codes.append(hex_code)

    if not relevant_centers:
        return ["No relevant colors found in the current mode."]

    # Generate palette image
    n_colors = len(relevant_centers)
    palette_img = np.zeros((60 + 20, n_colors * 100, 3), dtype=np.uint8)
    for i, (b, g, r) in enumerate(relevant_centers):
        # Fill color rectangle
        palette_img[:60, i * 100:(i + 1) * 100, :] = [b, g, r]
        # Add hex code text
        cv2.putText(palette_img, relevant_hex_codes[i], 
                    (i * 100 + 10, 75), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    # Save the original resized image
    cv2.imwrite(os.path.join(app.config['UPLOAD_FOLDER'], 'original_image.png'), img_resized)

    # Save palette image
    filename_without_ext = os.path.splitext(os.path.basename(image_path))[0]
    suffix = "_palette" if mode == 'palette' else f"_{target_color}_palette"
    filename = f"{filename_without_ext}{suffix}.png"
    cv2.imwrite(os.path.join(app.config['PALETTE_FOLDER'], filename), palette_img)

    return relevant_hex_codes

def save_palette_and_return(hex_codes, img, mode, target_color, image_path):
    n_colors = len(hex_codes)
    palette_img = np.zeros((60 + 20, n_colors * 100, 3), dtype=np.uint8)
    for i, hex_code in enumerate(hex_codes):
        r = int(hex_code[1:3], 16)
        g = int(hex_code[3:5], 16)
        b = int(hex_code[5:7], 16)
        palette_img[:60, i * 100:(i + 1) * 100, :] = [b, g, r]
        cv2.putText(palette_img, hex_code, (i * 100 + 10, 75),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    filename_without_ext = os.path.splitext(os.path.basename(image_path))[0]
    suffix = "_palette" if mode == 'palette' else f"_{target_color}_palette"
    filename = f"{filename_without_ext}{suffix}.png"
    cv2.imwrite(os.path.join(app.config['PALETTE_FOLDER'], filename), palette_img)

@app.route('/', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files['file']
        mode = request.form.get('mode', 'palette')
        color_name = request.form.get('color_name', '').lower()
        if file and file.filename != '':
            filename = file.filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            try:
                hex_codes = process_image(filepath, mode=mode, target_color=color_name if mode=='color' else None)
            except Exception as e:
                return f"Error processing image: {e}"
            return render_template('color_palette_extractor.html', original_image='original_image.png', hex_codes=hex_codes)
    return render_template('color_palette_extractor.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/palettes/<filename>')
def palette_file(filename):
    return send_from_directory(app.config['PALETTE_FOLDER'], filename)

# Function to open the browser
def open_browser():
    # Give the Flask server a moment to start up
    threading.Timer(1, lambda: webbrowser.open_new("http://127.0.0.1:5000/")).start()

if __name__ == '__main__':
    # Open the browser in a separate thread
    open_browser()
    # Run the Flask application
    app.run(debug=True)