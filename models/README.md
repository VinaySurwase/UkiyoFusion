# Custom Models Configuration for UkiyoeFusion

This directory is for storing your custom Stable Diffusion models.

## Adding Custom Models

### Method 1: Manual Copy

1. Create a new folder with your model name (e.g., `my-awesome-model`)
2. Copy all your model files into this folder
3. Ensure the folder contains:
   - `model_index.json` (required)
   - `text_encoder/` directory
   - `tokenizer/` directory
   - `unet/` directory
   - `vae/` directory
   - `scheduler/` directory

### Method 2: Using Git LFS (for Hugging Face models)

```bash
git lfs clone https://huggingface.co/username/model-name my-model-name
```

### Method 3: Using the Model Manager Script

```bash
./scripts/model_manager.sh download username/model-name
```

## Supported Model Types

- Stable Diffusion v1.x models
- Stable Diffusion v2.x models
- Fine-tuned models based on Stable Diffusion
- Custom trained models with diffusers format

## Model Structure Example

```
models/
├── my-custom-model/
│   ├── model_index.json
│   ├── text_encoder/
│   │   ├── config.json
│   │   └── pytorch_model.bin
│   ├── tokenizer/
│   │   ├── merges.txt
│   │   ├── special_tokens_map.json
│   │   ├── tokenizer_config.json
│   │   └── vocab.json
│   ├── unet/
│   │   ├── config.json
│   │   └── diffusion_pytorch_model.bin
│   ├── vae/
│   │   ├── config.json
│   │   └── diffusion_pytorch_model.bin
│   └── scheduler/
│       └── scheduler_config.json
```

## Testing Your Model

1. Add your model to the `models/` directory
2. Restart the UkiyoeFusion application
3. Your model should appear in the model selection dropdown
4. Test with a simple prompt to verify it works

## Troubleshooting

- **Model not showing up**: Check that `model_index.json` exists
- **Loading errors**: Verify all required directories and files are present
- **Out of memory**: Try reducing image size or use a smaller model

## Popular Custom Models

Some popular fine-tuned models you might want to try:

- `runwayml/stable-diffusion-v1-5`
- `stabilityai/stable-diffusion-2-1`
- `dreamlike-art/dreamlike-diffusion-1.0`
- `prompthero/openjourney`

Remember to respect the license terms of any models you use!
