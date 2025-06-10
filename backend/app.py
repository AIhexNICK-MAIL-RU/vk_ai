from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import io
import numpy as np
import faiss
import os
import json

app = Flask(__name__)
CORS(app)

# Global variables
faiss_index = None
artwork_metadata = {}

def load_faiss_and_metadata():
    global faiss_index, artwork_metadata
    try:
        # Load FAISS index
        if os.path.exists('data/artworks.index'):
            faiss_index = faiss.read_index('data/artworks.index')
        else:
            raise FileNotFoundError("FAISS index not found")
        
        # Load artwork metadata
        if os.path.exists('data/artwork_metadata.json'):
            with open('data/artwork_metadata.json', 'r') as f:
                artwork_metadata = json.load(f)
        else:
            raise FileNotFoundError("Artwork metadata not found")
        
        # Load test embeddings
        if os.path.exists('data/test_embeddings.json'):
            with open('data/test_embeddings.json', 'r') as f:
                global test_embeddings
                test_embeddings = json.load(f)
        else:
            raise FileNotFoundError("Test embeddings not found")
            
    except Exception as e:
        print(f"Error loading data: {str(e)}")
        raise

@app.route('/api/similar', methods=['POST'])
def find_similar_artworks():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400
    
    try:
        # For testing purposes, we'll use a pre-computed embedding
        # In production, you would compute this using CLIP
        embedding = np.array(test_embeddings["test_image"], dtype=np.float32).reshape(1, -1)
        
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

# Load data at startup
load_faiss_and_metadata()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port) 