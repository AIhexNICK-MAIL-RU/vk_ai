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

app = Flask(__name__)
CORS(app)

# Global variables for models and index
clip_model = None
processor = None
faiss_index = None
artwork_metadata = {}

def load_models():
    global clip_model, processor, faiss_index
    
    try:
        # Load CLIP model and processor with lower precision
        model_name = "openai/clip-vit-tiny-patch32"  # Using tiny model instead of base
        clip_model = CLIPModel.from_pretrained(model_name, torch_dtype=torch.float16)
        processor = CLIPProcessor.from_pretrained(model_name)
        
        # Move model to CPU and clear CUDA cache
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        # Load FAISS index if exists
        if os.path.exists('data/artworks.index'):
            faiss_index = faiss.read_index('data/artworks.index')
            
            # Load artwork metadata
            if os.path.exists('data/artwork_metadata.json'):
                with open('data/artwork_metadata.json', 'r') as f:
                    global artwork_metadata
                    artwork_metadata = json.load(f)
        
        # Force garbage collection
        gc.collect()
        
    except Exception as e:
        print(f"Error loading models: {str(e)}")
        raise

def get_image_embedding(image):
    try:
        # Process image and get embeddings using CLIP
        inputs = processor(images=image, return_tensors="pt", padding=True)
        with torch.no_grad():  # Disable gradient calculation
            image_features = clip_model.get_image_features(**inputs)
        # Normalize the features
        image_features = image_features / image_features.norm(dim=-1, keepdim=True)
        
        # Convert to numpy and clear memory
        result = image_features.cpu().detach().numpy()
        del image_features
        del inputs
        torch.cuda.empty_cache() if torch.cuda.is_available() else None
        gc.collect()
        
        return result
        
    except Exception as e:
        print(f"Error in get_image_embedding: {str(e)}")
        raise

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
        
        # Clear memory
        del embedding
        gc.collect()
        
        return jsonify({
            'similar_artworks': similar_artworks
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Load models when the application starts
load_models()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port) 