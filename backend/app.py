from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import io
import json
import os

app = Flask(__name__)
CORS(app)

# Global variables
demo_recommendations = {}

def load_demo_data():
    global demo_recommendations
    try:
        # Load demo recommendations
        if os.path.exists('data/demo_recommendations.json'):
            with open('data/demo_recommendations.json', 'r') as f:
                demo_recommendations = json.load(f)
        else:
            raise FileNotFoundError("Demo recommendations not found")
            
    except Exception as e:
        print(f"Error loading data: {str(e)}")
        raise

@app.route('/api/similar', methods=['POST'])
def find_similar_artworks():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400
    
    try:
        # For demo purposes, we'll always return the same pre-computed recommendations
        return jsonify({
            'similar_artworks': demo_recommendations.get('default_recommendations', [])
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Load data at startup
load_demo_data()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port) 