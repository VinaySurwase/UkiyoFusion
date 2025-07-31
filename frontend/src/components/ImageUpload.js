import React, { useCallback, useRef, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Box, Typography, Button, Dialog, DialogTitle, DialogContent, DialogActions, Alert } from '@mui/material';
import { CloudUpload, CameraAlt, Close, FlipCameraAndroid } from '@mui/icons-material';

const ImageUpload = ({ onImageUpload }) => {
  const [cameraOpen, setCameraOpen] = useState(false);
  const [cameraError, setCameraError] = useState('');
  const [stream, setStream] = useState(null);
  const [facingMode, setFacingMode] = useState('environment'); // 'user' for front, 'environment' for back
  const videoRef = useRef(null);
  const canvasRef = useRef(null);

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

  const openCamera = async (preferredFacingMode = facingMode) => {
    try {
      setCameraError('');
      setCameraOpen(true); // Open dialog first
      
      // Stop existing stream if any
      if (stream) {
        stream.getTracks().forEach(track => track.stop());
      }
      
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 1280 },
          height: { ideal: 720 },
          facingMode: preferredFacingMode
        }
      });
      setStream(mediaStream);
      setFacingMode(preferredFacingMode);
      
      // Set video stream once the dialog is open and video element is available
      setTimeout(() => {
        if (videoRef.current) {
          videoRef.current.srcObject = mediaStream;
        }
      }, 100);
    } catch (error) {
      console.error('Error accessing camera:', error);
      setCameraError('Unable to access camera. Please ensure you have granted camera permissions.');
    }
  };

  const switchCamera = async () => {
    const newFacingMode = facingMode === 'environment' ? 'user' : 'environment';
    await openCamera(newFacingMode);
  };

  const closeCamera = () => {
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
      setStream(null);
    }
    setCameraOpen(false);
    setCameraError('');
  };

  const capturePhoto = () => {
    if (videoRef.current && canvasRef.current) {
      const video = videoRef.current;
      const canvas = canvasRef.current;
      const context = canvas.getContext('2d');
      
      // Set canvas dimensions to match video
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      
      // Draw the video frame to canvas
      context.drawImage(video, 0, 0, canvas.width, canvas.height);
      
      // Convert canvas to data URL
      const dataURL = canvas.toDataURL('image/jpeg', 0.8);
      
      // Send the captured image to parent component
      onImageUpload(dataURL);
      
      // Close camera
      closeCamera();
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp']
    },
    multiple: false
  });

  return (
    <>
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
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              Supports PNG, JPG, JPEG, GIF, BMP, WebP
            </Typography>
            <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center', flexWrap: 'wrap' }}>
              <Button
                variant="outlined"
                startIcon={<CloudUpload />}
              >
                Choose Image
              </Button>
              <Button
                variant="outlined"
                startIcon={<CameraAlt />}
                onClick={(e) => {
                  e.stopPropagation();
                  openCamera();
                }}
                sx={{ bgcolor: 'background.paper' }}
              >
                Take Photo
              </Button>
            </Box>
          </Box>
        )}
      </Box>

      {/* Camera Dialog */}
      <Dialog
        open={cameraOpen}
        onClose={closeCamera}
        maxWidth="md"
        fullWidth
        PaperProps={{
          sx: { bgcolor: 'background.paper' }
        }}
      >
        <DialogTitle sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          Take a Photo
          <Button onClick={closeCamera} sx={{ minWidth: 'auto', p: 1 }}>
            <Close />
          </Button>
        </DialogTitle>
        <DialogContent>
          {cameraError && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {cameraError}
            </Alert>
          )}
          <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', position: 'relative' }}>
            <video
              ref={videoRef}
              autoPlay
              playsInline
              muted
              style={{
                width: '100%',
                maxWidth: '600px',
                height: 'auto',
                borderRadius: '8px',
                backgroundColor: '#000'
              }}
            />
            <canvas
              ref={canvasRef}
              style={{ display: 'none' }}
            />
            {/* Camera Switch Button */}
            {stream && (
              <Button
                variant="contained"
                size="small"
                onClick={switchCamera}
                startIcon={<FlipCameraAndroid />}
                sx={{
                  position: 'absolute',
                  top: 10,
                  right: 10,
                  minWidth: 'auto',
                  bgcolor: 'rgba(0, 0, 0, 0.6)',
                  '&:hover': {
                    bgcolor: 'rgba(0, 0, 0, 0.8)'
                  }
                }}
              >
                Switch
              </Button>
            )}
          </Box>
        </DialogContent>
        <DialogActions sx={{ justifyContent: 'center', pb: 2 }}>
          <Button
            variant="contained"
            size="large"
            onClick={capturePhoto}
            startIcon={<CameraAlt />}
            disabled={!stream}
          >
            Capture Photo
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default ImageUpload;
