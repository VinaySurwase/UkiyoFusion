import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Box, Typography, Button } from '@mui/material';
import { CloudUpload } from '@mui/icons-material';

const ImageUpload = ({ onImageUpload }) => {
  const onDrop = useCallback((acceptedFiles) => {
    const file = acceptedFiles[0];
    if (file && file.type.startsWith('image/')) {
      const reader = new FileReader();
      reader.onload = (e) => {
        onImageUpload(e.target.result);
      };
      reader.readAsDataURL(file);
    }
  }, [onImageUpload]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp']
    },
    multiple: false
  });

  return (
    <Box
      {...getRootProps()}
      className={`dropzone ${isDragActive ? 'active' : ''}`}
      sx={{
        border: '2px dashed',
        borderColor: isDragActive ? 'primary.main' : 'grey.400',
        borderRadius: 2,
        p: 3,
        textAlign: 'center',
        cursor: 'pointer',
        bgcolor: isDragActive ? 'primary.50' : 'background.paper',
        transition: 'all 0.3s ease',
        '&:hover': {
          borderColor: 'primary.main',
          bgcolor: 'primary.50'
        }
      }}
    >
      <input {...getInputProps()} />
      <CloudUpload sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
      {isDragActive ? (
        <Typography variant="body1" color="primary">
          Drop the image here...
        </Typography>
      ) : (
        <Box>
          <Typography variant="body1" gutterBottom>
            Drag & drop an image here, or click to select
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Supports PNG, JPG, JPEG, GIF, BMP, WebP
          </Typography>
          <Button
            variant="outlined"
            startIcon={<CloudUpload />}
            sx={{ mt: 2 }}
          >
            Choose Image
          </Button>
        </Box>
      )}
    </Box>
  );
};

export default ImageUpload;
