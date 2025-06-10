from flask import Flask, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# Hardcoded demo recommendations to avoid file I/O
DEMO_RECOMMENDATIONS = [
    {
        "id": 1,
        "title": "The Starry Night",
        "artist": "Vincent van Gogh",
        "year": 1889,
        "image_url": "https://images.metmuseum.org/CRDImages/ep/original/DP-974-001.jpg",
        "description": "One of Van Gogh's most famous works"
    },
    {
        "id": 2,
        "title": "Water Lilies",
        "artist": "Claude Monet",
        "year": 1919,
        "image_url": "https://images.metmuseum.org/CRDImages/ep/original/DP-1506-001.jpg",
        "description": "Part of Monet's Water Lilies series"
    },
    {
        "id": 3,
        "title": "The Persistence of Memory",
        "artist": "Salvador Dalí",
        "year": 1931,
        "image_url": "https://www.moma.org/media/W1siZiIsIjM4NjQ3MCJdLFsicCIsImNvbnZlcnQiLCItcXVhbGl0eSA5MCAtcmVzaXplIDIwMDB4MjAwMFx1MDAzZSJdXQ.jpg?sha=4c0635a9ee70d63e",
        "description": "Famous surrealist painting with melting clocks"
    }
]

@app.route('/api/similar', methods=['POST'])
def find_similar_artworks():
    return jsonify({
        'similar_artworks': DEMO_RECOMMENDATIONS
    })

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'message': 'Art recommendation demo service is running'
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port) 