# Image to Prompt Generator using NOVITA API

**Last Updated:** 02/25/2025

## Overview

This **Image to Prompt Generator** is a Flask application that utilizes the NOVITA API to convert images into textual prompts.

This tool is designed to aid users in generating images based on their unique artistic styles by converting their uploaded images into descriptive prompts, which can then be used in text-to-image models.

### Project Link

- **NOVITA API Documentation:** [NOVITA API Documentation](https://novita.ai/docs/api-reference/model-apis-image-to-prompt)

## Features

- Upload an image file.
- Automatically generate a descriptive prompt from the uploaded image.
- View the uploaded image alongside its generated prompt.

## Prerequisites

- Python 3.6 or higher
- Flask
- Requests
- Pillow
- NumPy
- TensorFlow

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/amaraauguste/BC-CISC-7900-SPRING-2025.git
   cd BC-CISC-7900-SPRING-2025/image2prompt_generator
   ```

2. **Install necessary packages:**
   ```bash
   pip install Flask requests Pillow numpy tensorflow
   ```

3. **Set up your NOVITA API Key:**
   - Create a file named `config.txt` in the project root directory.
   - Add the following line to `config.txt`, replacing <your_novita_api_key> with your API key:
     ```
     NOVITA_API_KEY=<your_novita_api_key>
     ```

## Usage

1. **Run the application:**
   ```bash
   python 'image2prompt.py'
   ```
   The application will automatically open in your default web browser after a brief delay.

2. **Upload an image:**
   - Use the web interface to select and upload an image file. 

3. **View the generated prompt:**
   - After uploading, the application will display the uploaded image and the corresponding generated prompt.

## Application Structure

- **image2prompt.py:** The main Flask application file that handles image uploading and interacting with the NOVITA API.
- **templates/image_to_prompt_generator.html:** The HTML template for the web interface.
- **config.txt:** To hold the NOVITA API Key for API authentication.

## Example Flow

1. User uploads an image.
2. The application resizes and processes the image.
3. The image is sent to the NOVITA API for prompt generation.
4. The returned prompt is displayed to the user beneath the uploaded image.
