# 18-FLUX-Kontext-Pro

This demo showcases **FLUX Kontext Pro** on Replicate.com using DelphiFMX for Python.

## Why this as Sample #18?
- **Top-tier image editing model:** FLUX Kontext Pro is one of Replicate's most practical multimodal models for guided image edits.
- **Prompt + image control:** You can transform an existing image while preserving composition and style constraints.
- **Great for production workflows:** Useful for ad variants, product recolors, scene restyling, and concept iterations.

## Features
- **Text-guided Image Editing:** Provide an instruction prompt and optional source image.
- **Aspect Ratio Presets:** Choose from common output sizes or match source image.
- **Fast Local Save:** Downloads and stores generated image automatically.
- **Dynamic API Key:** Enter your Replicate API token directly in the app.

## Prerequisites
```bash
pip install delphifmx replicate
```

## Running the Demo
1. Open `flux_kontext_pro.py`.
2. Enter your Replicate API key.
3. (Optional) Choose an input image for image-to-image editing.
4. Write an editing prompt.
5. Choose an aspect ratio and click **Generate Edited Image**.
