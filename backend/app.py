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
import gc
from functools import wraps

app = Flask(__name__)
CORS(app)

# Global variables for index and metadata
faiss_index = None
artwork_metadata = {}

def load_faiss_and_metadata():
    global faiss_index, artwork_metadata
    
    # Load FAISS index if exists
    if os.path.exists('data/artworks.index'):
        faiss_index = faiss.read_index('data/artworks.index')
        
        # Load artwork metadata
        if os.path.exists('data/artwork_metadata.json'):
            with open('data/artwork_metadata.json', 'r') as f:
                artwork_metadata = json.load(f)

class ModelManager:
    def __init__(self):
        self.model = None
        self.processor = None
    
    def load_model(self):
        if self.model is None:
            model_name = "openai/clip-vit-tiny-patch32"
            self.model = CLIPModel.from_pretrained(model_name, torch_dtype=torch.float16)
            self.processor = CLIPProcessor.from_pretrained(model_name)
    
    def unload_model(self):
        if self.model is not None:
            del self.model
            del self.processor
            self.model = None
            self.processor = None
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            gc.collect()
    
    def get_embedding(self, image):
        self.load_model()
        try:
            inputs = self.processor(images=image, return_tensors="pt", padding=True)
            with torch.no_grad():
                image_features = self.model.get_image_features(**inputs)
            image_features = image_features / image_features.norm(dim=-1, keepdim=True)
            result = image_features.cpu().detach().numpy()
            
            # Clean up
            del inputs
            del image_features
            self.unload_model()
            
            return result
        except Exception as e:
            self.unload_model()
            raise e

model_manager = ModelManager()

@app.route('/api/similar', methods=['POST'])
def find_similar_artworks():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400
    
    try:
        # Get the uploaded image
        image_file = request.files['image']
        image = Image.open(io.BytesIO(image_file.read())).convert('RGB')
        
        # Get embedding for the uploaded image
        embedding = model_manager.get_embedding(image)
        
        # Search similar artworks
        k = 5  # number of similar artworks to return
        D, I = faiss_index.search(embedding, k)
        
        # Get metadata for similar artworks
        similar_artworks = []
        for idx in I[0]:
            if str(idx) in artwork_metadata:
                similar_artworks.append(artwork_metadata[str(idx)])
        
        # Clean up
        del embedding
        gc.collect()
        
        return jsonify({
            'similar_artworks': similar_artworks
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Load FAISS index and metadata at startup
load_faiss_and_metadata()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port) 