'''
Amara Auguste
Delta E Calculator
05/01/2025

This script is a Flask web application that allows users to compare two colors using Delta E calculations.
The user can input two hex color codes, and the application will convert them to RGB, XYZ, and Lab color spaces.
The Delta E values (CIE76, CIE94, and CIE2000) are calculated to quantify the difference between the two colors.
The application also allows users to upload an Excel file containing hex color codes for batch processing.
The results are displayed in a user-friendly format, and the user can download the results as an Excel file.

'''
import numpy as np
from colormath.color_objects import sRGBColor, XYZColor, LabColor
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie1976, delta_e_cie1994, delta_e_cie2000
from flask import Flask, render_template, request, jsonify, send_file
import webbrowser
import threading
import pandas as pd
import os

# Create a Flask application
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Patch np.asscalar to make it compatible with the newer versions of numpy
def _patch_asscalar(a):
    """Alias for np.item(). Patch np.asscalar for colormath.

    :param a: numpy array
    :return: input array as scalar
    """
    return a.item()

# Applying the patch
np.asscalar = _patch_asscalar

# Function to convert hex color to RGB
def hex_to_rgb(hex_color):
    try:
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
    except ValueError:
        return None

# Function to convert RGB to XYZ
def rgb_to_xyz(rgb_value):
    if rgb_value is None:
        return None
    try:
        rgb_color = sRGBColor(rgb_value[0], rgb_value[1], rgb_value[2], is_upscaled=True)
        return convert_color(rgb_color, XYZColor)
    except Exception:
        return None

# Function to convert XYZ to Lab
def xyz_to_lab(xyz_value):
    if xyz_value is None:
        return None
    try:
        return convert_color(xyz_value, LabColor)
    except Exception:
        return None

# Function to calculate Delta E values
def calculate_delta_e(lab1, lab2):
    if lab1 is None or lab2 is None:
        return None, None, None
    try:
        delta_e_76 = round(delta_e_cie1976(lab1, lab2), 2)
        delta_e_94 = round(delta_e_cie1994(lab1, lab2), 2)
        delta_e_00 = round(delta_e_cie2000(lab1, lab2), 2)
        return delta_e_76, delta_e_94, delta_e_00
    except Exception:
        return None, None, None


# Route for the main page
@app.route('/')
def index():
    return render_template('compute_DeltaE.html')

# Route for processing single color pair data from form
@app.route('/process', methods=['POST'])
def process_single():
    hex_color1 = request.form['color1']
    hex_color2 = request.form['color2']

    rgb_value1 = hex_to_rgb(hex_color1)
    rgb_value2 = hex_to_rgb(hex_color2)

    xyz_color1 = rgb_to_xyz(rgb_value1)
    xyz_color2 = rgb_to_xyz(rgb_value2)

    lab_color1 = xyz_to_lab(xyz_color1)
    lab_color2 = xyz_to_lab(xyz_color2)

    delta_e_76, delta_e_94, delta_e_00 = calculate_delta_e(lab_color1, lab_color2)

    # Convert XYZColor to a list for JSON serialization and round the values (4 decimal places for HTML display)
    xyz_color1_serializable = [round(xyz_color1.xyz_x, 4), round(xyz_color1.xyz_y, 4), round(xyz_color1.xyz_z, 4)] if xyz_color1 else None
    xyz_color2_serializable = [round(xyz_color2.xyz_x, 4), round(xyz_color2.xyz_y, 4), round(xyz_color2.xyz_z, 4)] if xyz_color2 else None

    # Convert LabColor to a list for JSON serialization and round the values (2 decimal places for HTML display)
    lab_color1_serializable = [round(lab_color1.lab_l, 2), round(lab_color1.lab_a, 2), round(lab_color1.lab_b, 2)] if lab_color1 else None
    lab_color2_serializable = [round(lab_color2.lab_l, 2), round(lab_color2.lab_a, 2), round(lab_color2.lab_b, 2)] if lab_color2 else None


    return jsonify({
        'rgb1': rgb_value1,
        'xyz1': xyz_color1_serializable,
        'lab1': lab_color1_serializable,
        'rgb2': rgb_value2,
        'xyz2': xyz_color2_serializable,
        'lab2': lab_color2_serializable,
        'deltaE76': delta_e_76,
        'deltaE94': delta_e_94,
        'deltaE00': delta_e_00
    })

# Route for processing uploaded Excel file
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and file.filename.endswith('.xlsx'):
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)

        try:
            df = pd.read_excel(filepath)

            # Ensure the DataFrame has at least two columns
            if df.shape[1] < 2:
                os.remove(filepath)
                return jsonify({'error': 'Excel file must have at least two columns'}), 400

            # Assuming the first two columns contain the hex color codes
            df.columns = ['color1_hex', 'color2_hex']

            results = []
            for index, row in df.iterrows():
                hex_color1 = str(row['color1_hex']).strip()
                hex_color2 = str(row['color2_hex']).strip()

                rgb_value1 = hex_to_rgb(hex_color1)
                rgb_value2 = hex_to_rgb(hex_color2)

                xyz_color1 = rgb_to_xyz(rgb_value1)
                xyz_color2 = rgb_to_xyz(rgb_value2)

                lab_color1 = xyz_to_lab(xyz_color1)
                lab_color2 = xyz_to_lab(xyz_color2) # Corrected line

                delta_e_76, delta_e_94, delta_e_00 = calculate_delta_e(lab_color1, lab_color2)

                # Increase precision for XYZ and Lab values in the Excel output
                xyz1_str = str([round(xyz_color1.xyz_x, 4), round(xyz_color1.xyz_y, 4), round(xyz_color1.xyz_z, 4)]) if xyz_color1 else 'N/A'
                xyz2_str = str([round(xyz_color2.xyz_x, 4), round(xyz_color2.xyz_y, 4), round(xyz_color2.xyz_z, 4)]) if xyz_color2 else 'N/A'
                lab1_str = str([round(lab_color1.lab_l, 4), round(lab_color1.lab_a, 4), round(lab_color1.lab_b, 4)]) if lab_color1 else 'N/A'
                lab2_str = str([round(lab_color2.lab_l, 4), round(lab_color2.lab_a, 4), round(lab_color2.lab_b, 4)]) if lab_color2 else 'N/A'


                results.append({
                    'Color 1 (Hex)': hex_color1,
                    'Color 2 (Hex)': hex_color2,
                    'RGB 1': str(rgb_value1),
                    'RGB 2': str(rgb_value2),
                    'XYZ 1': xyz1_str,
                    'XYZ 2': xyz2_str,
                    'Lab 1': lab1_str,
                    'Lab 2': lab2_str,
                    '∆E 1976': delta_e_76 if delta_e_76 is not None else 'N/A',
                    '∆E 1994': delta_e_94 if delta_e_94 is not None else 'N/A',
                    '∆E 2000': delta_e_00 if delta_e_00 is not None else 'N/A'
                })

            results_df = pd.DataFrame(results)
            results_filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'color_comparison_results.xlsx')
            results_df.to_excel(results_filepath, index=False)

            os.remove(filepath)

            return jsonify({
                'message': 'File processed successfully.',
                'download_url': '/download/color_comparison_results.xlsx'
            })

        except Exception as e:
            os.remove(filepath)
            return jsonify({'error': f'Error processing file: {str(e)}'}), 500

    else:
        return jsonify({'error': 'Invalid file type. Please upload an .xlsx file'}), 400

# Route to download the results file
@app.route('/download/<filename>')
def download_file(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    else:
        return jsonify({'error': 'File not found'}), 404


# Function to open the browser
def open_browser():
    # Give the Flask server a moment to start up
    threading.Timer(1, lambda: webbrowser.open_new("http://127.0.0.1:5000/")).start()

if __name__ == '__main__':
    # Open the browser in a separate thread
    open_browser()
    # Run the Flask application
    app.run(debug=True)