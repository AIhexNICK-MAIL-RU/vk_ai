import React, { useState } from 'react';
import {
  Box,
  Container,
  Typography,
  Button,
  Card,
  CardMedia,
  CardContent,
  Grid,
  CircularProgress
} from '@mui/material';
import { styled } from '@mui/material/styles';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import axios from 'axios';

const VisuallyHiddenInput = styled('input')`
  clip: rect(0 0 0 0);
  clip-path: inset(50%);
  height: 1px;
  overflow: hidden;
  position: absolute;
  bottom: 0;
  left: 0;
  white-space: nowrap;
  width: 1px;
`;

function App() {
  const [selectedImage, setSelectedImage] = useState(null);
  const [similarArtworks, setSimilarArtworks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleImageUpload = async (event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedImage(URL.createObjectURL(file));
      setLoading(true);
      setError(null);

      const formData = new FormData();
      formData.append('image', file);

      try {
        const response = await axios.post('http://localhost:5000/api/similar', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });
        setSimilarArtworks(response.data.similar_artworks);
      } catch (err) {
        setError('Error finding similar artworks. Please try again.');
        console.error('Error:', err);
      } finally {
        setLoading(false);
      }
    }
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h3" component="h1" gutterBottom align="center">
        Art Recommender
      </Typography>
      
      <Box sx={{ textAlign: 'center', mb: 4 }}>
        <Button
          component="label"
          variant="contained"
          startIcon={<CloudUploadIcon />}
          sx={{ mb: 2 }}
        >
          Upload Artwork
          <VisuallyHiddenInput type="file" onChange={handleImageUpload} accept="image/*" />
        </Button>

        {selectedImage && (
          <Box sx={{ mt: 2, mb: 4 }}>
            <Typography variant="h6" gutterBottom>
              Your Uploaded Artwork
            </Typography>
            <Card sx={{ maxWidth: 345, mx: 'auto' }}>
              <CardMedia
                component="img"
                height="300"
                image={selectedImage}
                alt="Uploaded artwork"
                sx={{ objectFit: 'contain' }}
              />
            </Card>
          </Box>
        )}

        {loading && (
          <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
            <CircularProgress />
          </Box>
        )}

        {error && (
          <Typography color="error" sx={{ mt: 2 }}>
            {error}
          </Typography>
        )}

        {similarArtworks.length > 0 && (
          <Box sx={{ mt: 4 }}>
            <Typography variant="h5" gutterBottom>
              Similar Artworks
            </Typography>
            <Grid container spacing={3}>
              {similarArtworks.map((artwork, index) => (
                <Grid item xs={12} sm={6} md={4} key={index}>
                  <Card>
                    <CardMedia
                      component="img"
                      height="300"
                      image={artwork.image_url}
                      alt={artwork.title}
                      sx={{ objectFit: 'contain' }}
                    />
                    <CardContent>
                      <Typography gutterBottom variant="h6" component="div">
                        {artwork.title}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {artwork.artist}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {artwork.date}
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </Box>
        )}
      </Box>
    </Container>
  );
}

export default App; 