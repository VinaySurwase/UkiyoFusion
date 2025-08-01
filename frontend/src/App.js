import React, { useState, useEffect } from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Container,
  Grid,
  Paper,
  Button,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Slider,
  Box,
  CircularProgress,
  Alert,
  Card,
  CardContent,
  Chip,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  CloudUpload,
  Download,
  Refresh,
  Settings,
  Palette,
  AutoAwesome
} from '@mui/icons-material';
import ImageUpload from './components/ImageUpload';
import ImagePreview from './components/ImagePreview';
import AdvancedSettings from './components/AdvancedSettings';
import { transformImage, getModels, getStyles } from './services/api';
import './App.css';

function App() {
  // State management
  const [originalImage, setOriginalImage] = useState(null);
  const [transformedImage, setTransformedImage] = useState(null);
  const [prompt, setPrompt] = useState('');
  const [selectedStyle, setSelectedStyle] = useState('classic_ukiyo');
  const [selectedModel, setSelectedModel] = useState('');
  const [strength, setStrength] = useState(0.85);  // Higher for more transformation
  const [guidanceScale, setGuidanceScale] = useState(12.0);  // Higher for stronger style adherence  
  const [steps, setSteps] = useState(30);  // More steps for better quality
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [models, setModels] = useState({});
  const [styles, setStyles] = useState({});
  const [showAdvanced, setShowAdvanced] = useState(false);

  // Load models and styles on component mount
  useEffect(() => {
    loadModelsAndStyles();
  }, []);

  // Helper function to get style descriptions
  const getStyleDescription = (styleId) => {
    const descriptions = {
      'classic_ukiyo': 'Traditional woodblock print with bold outlines and flat colors',
      'landscape_ukiyo': 'Scenic views with Mount Fuji, cherry blossoms, and nature',
      'portrait_ukiyo': 'Geisha, samurai, and kabuki actors in traditional dress', 
      'nature_ukiyo': 'Flora, fauna, birds, and seasonal natural elements',
      'urban_ukiyo': 'Edo period city life, markets, and street scenes',
      'seasonal_ukiyo': 'Spring, summer, autumn, winter seasonal themes'
    };
    return descriptions[styleId] || 'Traditional Japanese art style';
  };

    const loadModelsAndStyles = async () => {
    try {
      // Load models and styles
      const [modelsResponse, stylesResponse] = await Promise.all([
        getModels(),
        getStyles()
      ]);
      
      setModels(modelsResponse.models || {});
      setStyles(stylesResponse.styles || {});
      
      // Set default model if available
      const modelKeys = Object.keys(modelsResponse.models || {});
      if (modelKeys.length > 0 && !selectedModel) {
        setSelectedModel(modelKeys[0]);
      }
    } catch (error) {
      console.error('Failed to load models and styles:', error);
      setError('Failed to load application data');
    }
  };

  const handleImageUpload = (imageData) => {
    setOriginalImage(imageData);
    setTransformedImage(null);
    setError('');
  };

  const handleTransform = async () => {
    if (!originalImage) {
      setError('Please upload an image first');
      return;
    }

    // Prompt is now optional for Ukiyo-e transformation
    setIsLoading(true);
    setError('');

    try {
      console.log('Starting transformation with data:', {
        prompt: prompt.trim(),
        style: selectedStyle,
        model_id: selectedModel,
        strength: strength,
        guidance_scale: guidanceScale,
        num_inference_steps: steps
      });
      
      const result = await transformImage({
        image: originalImage,
        prompt: prompt.trim(),  // Can be empty
        style: selectedStyle,
        model_id: selectedModel,
        strength: strength,
        guidance_scale: guidanceScale,
        num_inference_steps: steps
      });

      console.log('Transformation result:', result);
      
      if (result.success) {
        console.log('Setting transformed image');
        setTransformedImage(result.image);
      } else {
        console.error('Transformation not successful:', result);
        setError(result.error || 'Transformation failed');
      }
    } catch (err) {
      console.error('Transformation error caught:', err);
      setError('Failed to transform image: ' + err.message);
      console.error('Transformation error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDownload = () => {
    if (!transformedImage) return;

    const link = document.createElement('a');
    link.href = transformedImage;
    link.download = `ukiyoe_fusion_${Date.now()}.png`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleReset = () => {
    setOriginalImage(null);
    setTransformedImage(null);
    setPrompt('');
    setError('');
  };

  return (
    <div className="App">
      <AppBar position="static" sx={{ background: 'linear-gradient(45deg, #6B73FF 30%, #9F7AEA 90%)' }}>
        <Toolbar>
          <Palette sx={{ mr: 2 }} />
          <Typography variant="h5" component="div" sx={{ flexGrow: 1, fontWeight: 'bold' }}>
            UkiyoeFusion
          </Typography>
          <Typography variant="subtitle1" sx={{ opacity: 0.9 }}>
            Traditional Japanese Art Transformation
          </Typography>
        </Toolbar>
      </AppBar>

      <Container maxWidth="xl" sx={{ py: 4 }}>
        <Grid container spacing={3}>
          {/* Left Panel - Controls */}
          <Grid item xs={12} md={4}>
            <Card elevation={3}>
              <CardContent>
                <Box display="flex" alignItems="center" mb={2}>
                  <Settings sx={{ mr: 1, color: 'primary.main' }} />
                  <Typography variant="h6">Ukiyo-e Art Styles</Typography>
                </Box>

                {/* Model Selection */}
                <FormControl fullWidth margin="normal">
                  <InputLabel>Ukiyo-e Model</InputLabel>
                  <Select
                    value={selectedModel}
                    onChange={(e) => setSelectedModel(e.target.value)}
                    label="Ukiyo-e Model"
                  >
                    {Object.entries(models).map(([id, model]) => (
                      <MenuItem key={id} value={id}>
                        <Box>
                          <Typography variant="body2">{model.name}</Typography>
                          <Chip 
                            label={model.type} 
                            size="small" 
                            color={model.type === 'local' ? 'secondary' : 'primary'}
                            sx={{ ml: 1 }}
                          />
                        </Box>
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>

                {/* Style Selection */}
                <FormControl fullWidth margin="normal">
                  <InputLabel>Ukiyo-e Style</InputLabel>
                  <Select
                    value={selectedStyle}
                    onChange={(e) => setSelectedStyle(e.target.value)}
                    label="Ukiyo-e Style"
                  >
                    {Object.entries(styles).map(([id, style]) => (
                      <MenuItem key={id} value={id}>
                        <Box>
                          <Typography variant="body2" fontWeight="medium">
                            {style.name}
                          </Typography>
                          <Typography variant="caption" color="text.secondary" display="block">
                            {getStyleDescription(id)}
                          </Typography>
                        </Box>
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>

                {/* Optional Prompt Input */}
                <TextField
                  fullWidth
                  multiline
                  rows={3}
                  label="Additional Description (Optional)"
                  placeholder="Add specific elements like cherry blossoms, samurai, temple, or leave empty for pure style..."
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  margin="normal"
                  variant="outlined"
                  helperText="Will be added to enhanced Ukiyo-e style prompt with bold outlines, flat colors, and traditional aesthetics"
                />

                {/* Advanced Settings Toggle */}
                <Box mt={2} mb={1}>
                  <Button
                    variant="outlined"
                    startIcon={<AutoAwesome />}
                    onClick={() => setShowAdvanced(!showAdvanced)}
                    fullWidth
                  >
                    {showAdvanced ? 'Hide' : 'Show'} Advanced Settings
                  </Button>
                </Box>

                {/* Advanced Settings */}
                {showAdvanced && (
                  <AdvancedSettings
                    strength={strength}
                    setStrength={setStrength}
                    guidanceScale={guidanceScale}
                    setGuidanceScale={setGuidanceScale}
                    steps={steps}
                    setSteps={setSteps}
                  />
                )}

                {/* Action Buttons */}
                <Box mt={3} display="flex" gap={1}>
                  <Button
                    variant="contained"
                    onClick={handleTransform}
                    disabled={isLoading || !originalImage}
                    startIcon={isLoading ? <CircularProgress size={20} /> : <AutoAwesome />}
                    fullWidth
                    sx={{ 
                      background: 'linear-gradient(45deg, #FF6B6B 30%, #4ECDC4 90%)',
                      py: 1.5
                    }}
                  >
                    {isLoading ? 'Creating Ukiyo-e Art...' : 'Transform to Ukiyo-e'}
                  </Button>
                </Box>

                <Box mt={1} display="flex" gap={1}>
                  <Button
                    variant="outlined"
                    onClick={handleReset}
                    startIcon={<Refresh />}
                    fullWidth
                  >
                    Reset
                  </Button>
                  <Button
                    variant="outlined"
                    onClick={handleDownload}
                    disabled={!transformedImage}
                    startIcon={<Download />}
                    fullWidth
                  >
                    Download
                  </Button>
                </Box>

                {/* Refresh Models Button */}
                <Box mt={2}>
                  <Button
                    variant="text"
                    onClick={loadModelsAndStyles}
                    startIcon={<Refresh />}
                    fullWidth
                    size="small"
                  >
                    Refresh Models
                  </Button>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* Right Panel - Images */}
          <Grid item xs={12} md={8}>
            <Grid container spacing={2}>
              {/* Original Image */}
              <Grid item xs={12} md={6}>
                <Paper elevation={3} sx={{ p: 2, height: '100%' }}>
                  <Typography variant="h6" gutterBottom>
                    Original Image
                  </Typography>
                  <ImageUpload onImageUpload={handleImageUpload} />
                  {originalImage && (
                    <Box mt={2}>
                      <ImagePreview src={originalImage} alt="Original" />
                    </Box>
                  )}
                </Paper>
              </Grid>

              {/* Transformed Image */}
              <Grid item xs={12} md={6}>
                <Paper elevation={3} sx={{ p: 2, height: '100%' }}>
                  <Typography variant="h6" gutterBottom>
                    Transformed Image
                  </Typography>
                  {isLoading ? (
                    <Box 
                      display="flex" 
                      flexDirection="column" 
                      alignItems="center" 
                      justifyContent="center" 
                      height={300}
                    >
                      <CircularProgress size={60} />
                      <Typography variant="body2" mt={2} color="text.secondary">
                        AI is working its magic...
                      </Typography>
                    </Box>
                  ) : transformedImage ? (
                    <ImagePreview src={transformedImage} alt="Transformed" />
                  ) : (
                    <Box 
                      display="flex" 
                      alignItems="center" 
                      justifyContent="center" 
                      height={300}
                      bgcolor="grey.100"
                      borderRadius={1}
                    >
                      <Typography variant="body2" color="text.secondary">
                        Transformed image will appear here
                      </Typography>
                    </Box>
                  )}
                </Paper>
              </Grid>
            </Grid>

            {/* Error Display */}
            {error && (
              <Box mt={2}>
                <Alert severity="error" onClose={() => setError('')}>
                  {error}
                </Alert>
              </Box>
            )}
          </Grid>
        </Grid>
      </Container>
    </div>
  );
}

export default App;
