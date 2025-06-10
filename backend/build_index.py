import requests
import json
import os
import faiss
import numpy as np
from PIL import Image
from transformers import CLIPProcessor, CLIPModel
from tqdm import tqdm
import io
import time
import gc

def download_artwork_data(limit=100):  # Уменьшим начальный лимит для тестирования
    """Download artwork data from the Metropolitan Museum API"""
    print("Downloading artwork data from Met API...")
    
    # Get all object IDs first
    objects_url = "https://collectionapi.metmuseum.org/public/collection/v1/search?hasImages=true&q=painting"
    response = requests.get(objects_url)
    data = response.json()
    object_ids = data['objectIDs'][:limit]
    
    artworks = []
    for obj_id in tqdm(object_ids, desc="Fetching artwork metadata"):
        try:
            url = f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{obj_id}"
            response = requests.get(url)
            artwork = response.json()
            
            # Only include artworks with primary image
            if artwork.get('primaryImage'):
                artworks.append({
                    'id': artwork['objectID'],
                    'title': artwork['title'],
                    'artist': artwork['artistDisplayName'],
                    'date': artwork['objectDate'],
                    'image_url': artwork['primaryImage'],
                    'department': artwork['department']
                })
                
            # Add a small delay to avoid overwhelming the API
            time.sleep(0.1)
            
        except Exception as e:
            print(f"Error fetching artwork {obj_id}: {str(e)}")
            continue
    
    return artworks

def process_batch(model, processor, artworks_batch, start_idx):
    """Process a batch of artworks and return their embeddings and metadata"""
    batch_embeddings = []
    batch_metadata = {}
    
    for i, artwork in enumerate(tqdm(artworks_batch, desc="Processing batch")):
        try:
            # Download image
            response = requests.get(artwork['image_url'])
            image = Image.open(io.BytesIO(response.content)).convert('RGB')
            
            # Get image embedding
            inputs = processor(images=image, return_tensors="pt", padding=True)
            image_features = model.get_image_features(**inputs)
            image_features = image_features / image_features.norm(dim=-1, keepdim=True)
            embedding = image_features.detach().numpy()
            
            # Store embedding and metadata
            batch_embeddings.append(embedding[0])  # Remove batch dimension
            batch_metadata[str(start_idx + i)] = artwork
            
            # Clear some memory
            del image_features
            del inputs
            gc.collect()
            
        except Exception as e:
            print(f"Error processing artwork {artwork['id']}: {str(e)}")
            continue
    
    return np.array(batch_embeddings), batch_metadata

def build_faiss_index(artworks, batch_size=10):
    """Build FAISS index from artwork embeddings"""
    print("Loading CLIP model...")
    model_name = "openai/clip-vit-base-patch32"
    model = CLIPModel.from_pretrained(model_name)
    processor = CLIPProcessor.from_pretrained(model_name)
    
    # Initialize FAISS index
    embedding_dim = 512  # CLIP's image embedding dimension
    index = faiss.IndexFlatIP(embedding_dim)
    
    print("Processing artworks and building index...")
    artwork_metadata = {}
    
    # Process artworks in batches
    for i in range(0, len(artworks), batch_size):
        batch = artworks[i:i + batch_size]
        embeddings, batch_metadata = process_batch(model, processor, batch, i)
        
        if len(embeddings) > 0:
            # Add embeddings to index
            index.add(embeddings)
            # Update metadata
            artwork_metadata.update(batch_metadata)
        
        # Clear some memory
        gc.collect()
    
    # Save index and metadata
    print("Saving index and metadata...")
    if not os.path.exists('data'):
        os.makedirs('data')
    
    faiss.write_index(index, 'data/artworks.index')
    with open('data/artwork_metadata.json', 'w') as f:
        json.dump(artwork_metadata, f)
    
    print(f"Index built successfully with {index.ntotal} artworks")

if __name__ == "__main__":
    # Download artwork data
    artworks = download_artwork_data(limit=100)  # Start with a smaller number for testing
    
    # Build FAISS index
    build_faiss_index(artworks) 