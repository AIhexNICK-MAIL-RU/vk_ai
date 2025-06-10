from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import io
import torch
from transformers import CLIPProcessor, CLIPModel
import faiss
import numpy as np
import os
import json

app = Flask(__name__)
CORS(app)

# Global variables for models and index
clip_model = None
processor = None
faiss_index = None
artwork_metadata = {}

def load_models():
    global clip_model, processor, faiss_index
    
    # Load CLIP model and processor
    model_name = "openai/clip-vit-base-patch32"
    clip_model = CLIPModel.from_pretrained(model_name)
    processor = CLIPProcessor.from_pretrained(model_name)
    
    # Load FAISS index if exists
    if os.path.exists('data/artworks.index'):
        faiss_index = faiss.read_index('data/artworks.index')
        
        # Load artwork metadata
        if os.path.exists('data/artwork_metadata.json'):
            with open('data/artwork_metadata.json', 'r') as f:
                global artwork_metadata
                artwork_metadata = json.load(f)

def get_image_embedding(image):
    # Process image and get embeddings using CLIP
    inputs = processor(images=image, return_tensors="pt", padding=True)
    image_features = clip_model.get_image_features(**inputs)
    # Normalize the features
    image_features = image_features / image_features.norm(dim=-1, keepdim=True)
    return image_features.detach().numpy()

@app.route('/api/similar', methods=['POST'])
def find_similar_artworks():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400
    
    try:
        # Get the uploaded image
        image_file = request.files['image']
        image = Image.open(io.BytesIO(image_file.read())).convert('RGB')
        
        # Get embedding for the uploaded image
        embedding = get_image_embedding(image)
        
        # Search similar artworks
        k = 5  # number of similar artworks to return
        D, I = faiss_index.search(embedding, k)
        
        # Get metadata for similar artworks
        similar_artworks = []
        for idx in I[0]:
            if str(idx) in artwork_metadata:
                similar_artworks.append(artwork_metadata[str(idx)])
        
        return jsonify({
            'similar_artworks': similar_artworks
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.before_first_request
def initialize():
    load_models()

if __name__ == '__main__':
    app.run(debug=True, port=5000) 