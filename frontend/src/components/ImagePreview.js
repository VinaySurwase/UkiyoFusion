import React from 'react';
import { Box } from '@mui/material';

const ImagePreview = ({ src, alt, maxHeight = 400 }) => {
  if (!src) return null;

  return (
    <Box
      sx={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        maxHeight: maxHeight,
        overflow: 'hidden',
        borderRadius: 2,
        bgcolor: 'grey.100'
      }}
    >
      <img
        src={src}
        alt={alt}
        className="image-preview"
        style={{
          maxWidth: '100%',
          maxHeight: maxHeight,
          objectFit: 'contain',
          borderRadius: 8,
          boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
        }}
      />
    </Box>
  );
};

export default ImagePreview;
