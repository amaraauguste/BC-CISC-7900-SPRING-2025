# Delta E (ΔE) Calculator Web Application

**Author:** Amara Auguste  
**Date:** May 1, 2025

---

## Overview

The **Delta E (ΔE) Calculator** is a user-friendly web application built with Flask that enables users to compare colors using various Delta E (ΔE) metrics. It supports both individual color comparisons and batch processing through Excel file uploads.

## Features

- Input two hex color codes to compute their color differences.
- Converts colors to RGB, XYZ, and Lab color spaces.
- Calculates Delta E (ΔE) values using CIE76, CIE94, and CIE2000 formulas.
- Uploads an Excel (.xlsx) file containing multiple color pairs for batch processing.
- Displays comparison results in a clear format.
- Allows downloading of results as an Excel file.

## Installation

### Prerequisites

- Python 3.7 or higher
- pip package manager

### Setup

1. Clone or download this repository.

2. Create a virtual environment (optional but recommended):

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

*Note:* Ensure `requirements.txt` includes:

```
flask
numpy
pandas
colormath
```

## Usage

### Running the Application

```bash
python compute_DeltaE.py
```

The app will automatically open in your default web browser.

### Using the Web Interface

- **Single Color Comparison:**
  - Enter two hex color codes (e.g., `#FF5733`, `#33A1FF`).
  - Submit to view color conversions and Delta E metrics.

- **Batch Processing:**
  - Prepare an Excel file with at least two columns containing hex color codes.
  - Upload via the provided form.
  - Download the processed results as an Excel file.

## Application Structure

```
your-project/
│
├── compute_DeltaE.py          # Main Flask application
├── requirements.txt           # Dependencies list
├── templates/
│   └── compute_DeltaE.html    # Front-end HTML template (not included here)
└── uploads/                   # Folder for temporary uploads and results (auto-created)
```

- **`compute_DeltaE.py`:** Contains all the server-side logic, route definitions, and color processing functions.
- **`templates/compute_DeltaE.html`:** The HTML interface (not provided here), which includes forms for input and upload.
- **`uploads/`:** Directory created automatically if it does not exist; used to store uploaded files and generated results.

## Important Notes

- The `uploads/` folder will be automatically created if it does not already exist when the application starts.
- The code uses the `colormath` library for color conversions and Delta E calculations. However, `colormath` is no longer actively maintained, which can lead to compatibility issues with newer versions of NumPy. To address this, the code patches `np.asscalar`, which is deprecated in newer NumPy versions, by aliasing it to `np.item()`—maintaining compatibility.
- Ensure your input hex colors are valid and properly formatted.
- The batch processing expects an Excel file with columns named `'color1_hex'` and `'color2_hex'`.
