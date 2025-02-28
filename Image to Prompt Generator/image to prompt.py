'''
Amara Auguste
Image to Prompt Generator using NOVITA API
02/25/2025

To better aid my project of generating my own images based on my art style, 
I have created an Image to Prompt Generator using the NOVITA API
documentation here: https://novita.ai/docs/api-reference/model-apis-image-to-prompt

This generator will take an image as input and generate a prompt based on the content of the 
image. The prompt can then be used to generate new images using text-to-image models.
'''
# Flask application for Image to Prompt Generator using NOVITA API
from flask import Flask, request, render_template, send_file
import requests
import numpy as np
import base64
from PIL import Image
from tensorflow.keras.applications import InceptionV3
from tensorflow.keras.applications.inception_v3 import preprocess_input
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.models import Model
import io
import webbrowser  # To open the browser automatically
from threading import Timer  # To delay the browser open

# Function to read API Key from the config file
def load_api_key(file_path):
    with open(file_path, 'r') as file:
        for line in file:
            if line.startswith('NOVITA_API_KEY'):
                return line.split('=')[1].strip()
    raise Exception("API Key not found in the configuration file.")

# Load NOVITA API Key
NOVITA_API_KEY = load_api_key('config.txt')

# Initialize Flask app
app = Flask(__name__)

# Initialize the InceptionV3 model for feature extraction
base_model = InceptionV3(weights='imagenet')
model = Model(inputs=base_model.input, outputs=base_model.layers[-2].output)

url = "https://api.novita.ai/v3/img2prompt"

def resize_image(image, target_size=(299, 299)):
    img = image.resize(target_size, Image.LANCZOS)
    return img

def image_to_prompt(image):
    img = resize_image(image)
    img_array = img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = preprocess_input(img_array)
    features = model.predict(img_array)

    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG')
    encoded_image = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')

    payload = {
        "image_file": encoded_image
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {NOVITA_API_KEY}"
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        prompt = response.json()
        return prompt
    else:
        print("Error:", response.status_code, response.text)
        return None

@app.route("/", methods=["GET", "POST"])
def upload_image():
    prompt = None
    image_url = None  # Initialize image_url for rendering the uploaded image

    if request.method == "POST":
        if 'file' not in request.files:
            return "No file part"
        file = request.files['file']
        if file.filename == '':
            return "No selected file"
        
        # Load the uploaded image
        img = Image.open(file.stream).convert("RGB")
        prompt = image_to_prompt(img)  # Generate prompt from the image

        # Save the uploaded image to a BytesIO object
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG')
        image_url = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')  # To encode to base64 for HTML

    return render_template("image_to_prompt_generator.html", prompt=prompt, image_url=image_url)

@app.route('/image/<filename>')
def uploaded_file(filename):
    # This endpoint can be used to send files from server storage if needed.
    return send_file(filename)

if __name__ == "__main__":
    Timer(1, lambda: webbrowser.open('http://127.0.0.1:5000/')).start()
    app.run(debug=True)