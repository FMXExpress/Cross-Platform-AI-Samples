# 21-Background-Removal-Rembg

This sample showcases **Rembg background removal** from Replicate Explore using DelphiFMX for Python.

## Why this as Sample #21?
- **Popularity-driven pick:** Background removal workflows are consistently among the highest-usage production image tasks on Replicate because they are useful in e-commerce, marketing, and social content pipelines.
- **Variety upgrade for the sample set:** Existing samples already cover text, speech, music, video generation, and text-to-image. This adds a practical **image utility** workflow rather than another pure generator.
- **Fast visual payoff:** A single input image produces an immediate transparent-PNG output, making it a strong demo for desktop UX and post-processing pipelines.

## Features
- **Background removal** via `cjwbw/rembg`.
- **Local file picker** for PNG/JPG/WEBP input images.
- **Side-by-side preview** of original and processed image.
- **Automatic result download** to a deterministic local filename.
- **Inline API key entry** (or prefill from `REPLICATE_API_TOKEN`).

## Prerequisites
```bash
pip install delphifmx replicate
```

## Running the Demo
1. Open `rembg_background_removal.py`.
2. Enter your Replicate API key.
3. Click **Select Input Image** and choose a product/photo image.
4. Click **Remove Background**.
5. Wait for the output preview and saved transparent PNG.
