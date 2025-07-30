# Custom Models Directory

Place your trained Stable Diffusion models in this directory.

## Supported Formats:

- **Diffusers format**: Complete model directories with all components
- **Safetensors/Checkpoint files**: .safetensors or .bin files

## Directory Structure:

```
custom_models/
├── my_anime_model/          # Your custom model directory
│   ├── model_index.json
│   ├── scheduler/
│   ├── text_encoder/
│   ├── tokenizer/
│   ├── unet/
│   └── vae/
├── another_model/
└── README.md               # This file
```

## How to Add Your Model:

1. **If you have a diffusers model:**

   - Copy the entire model directory here
   - Make sure it contains `model_index.json`

2. **If you have a checkpoint file:**

   - Create a new directory with your model name
   - Place the .safetensors or .bin file inside

3. **Restart the server:**
   - The application will automatically detect your model
   - It will appear in the model selection dropdown

## Example:

```bash
# Copy your trained model
cp -r /path/to/your/model custom_models/my_ukiyo_model/

# Restart the server
./start_simple.sh
```

Your model will be automatically detected and available for use!
