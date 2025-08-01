import React from 'react';
import {
  Box,
  Typography,
  Slider,
  Grid,
  Tooltip,
  IconButton
} from '@mui/material';
import { Info } from '@mui/icons-material';

const AdvancedSettings = ({
  strength,
  setStrength,
  guidanceScale,
  setGuidanceScale,
  steps,
  setSteps
}) => {
  return (
    <Box sx={{ mt: 2, p: 2, bgcolor: 'grey.50', borderRadius: 2 }}>
      <Typography variant="subtitle2" gutterBottom sx={{ fontWeight: 600 }}>
        Advanced Parameters
      </Typography>

      {/* Strength */}
      <Box sx={{ mb: 3 }}>
        <Box display="flex" alignItems="center" mb={1}>
          <Typography variant="body2" sx={{ flexGrow: 1 }}>
            Transformation Strength: {strength.toFixed(2)}
          </Typography>
          <Tooltip title="Higher values make bigger changes to the original image">
            <IconButton size="small">
              <Info fontSize="small" />
            </IconButton>
          </Tooltip>
        </Box>
        <Slider
          value={strength}
          onChange={(e, newValue) => setStrength(newValue)}
          min={0.1}
          max={1.0}
          step={0.05}
          marks={[
            { value: 0.1, label: '0.1' },
            { value: 0.5, label: '0.5' },
            { value: 1.0, label: '1.0' }
          ]}
          valueLabelDisplay="auto"
        />
        <Typography variant="caption" color="text.secondary">
          0.1 = Subtle changes | 1.0 = Complete transformation (0.75 optimal for Ukiyo-e)
        </Typography>
      </Box>

      {/* Guidance Scale */}
      <Box sx={{ mb: 3 }}>
        <Box display="flex" alignItems="center" mb={1}>
          <Typography variant="body2" sx={{ flexGrow: 1 }}>
            Guidance Scale: {guidanceScale.toFixed(1)}
          </Typography>
          <Tooltip title="How closely the AI follows your prompt">
            <IconButton size="small">
              <Info fontSize="small" />
            </IconButton>
          </Tooltip>
        </Box>
        <Slider
          value={guidanceScale}
          onChange={(e, newValue) => setGuidanceScale(newValue)}
          min={1.0}
          max={20.0}
          step={0.5}
          marks={[
            { value: 1, label: '1' },
            { value: 7.5, label: '7.5' },
            { value: 15, label: '15' },
            { value: 20, label: '20' }
          ]}
          valueLabelDisplay="auto"
        />
        <Typography variant="caption" color="text.secondary">
          Lower = More creative | Higher = Follows style strictly (8.5 optimal for Ukiyo-e)
        </Typography>
      </Box>

      {/* Inference Steps */}
      <Box sx={{ mb: 2 }}>
        <Box display="flex" alignItems="center" mb={1}>
          <Typography variant="body2" sx={{ flexGrow: 1 }}>
            Inference Steps: {steps}
          </Typography>
          <Tooltip title="More steps = better quality but slower generation">
            <IconButton size="small">
              <Info fontSize="small" />
            </IconButton>
          </Tooltip>
        </Box>
        <Slider
          value={steps}
          onChange={(e, newValue) => setSteps(newValue)}
          min={10}
          max={100}
          step={5}
          marks={[
            { value: 10, label: '10' },
            { value: 25, label: '25' },
            { value: 50, label: '50' },
            { value: 75, label: '75' },
            { value: 100, label: '100' }
          ]}
          valueLabelDisplay="auto"
        />
        <Typography variant="caption" color="text.secondary">
          10 = Fast | 25 = Optimal for Ukiyo-e | 50+ = High quality but slower
        </Typography>
      </Box>
    </Box>
  );
};

export default AdvancedSettings;
