# 22-Remove-Background-Pro

This sample showcases **fofr/remove-background** from Replicate Explore using DelphiFMX for Python.

## Why this as Sample #22?
After reviewing the existing samples in this repo, the strongest gap is a **high-utility image post-processing workflow** (non-generative, production-friendly, and commonly needed in e-commerce/design pipelines). Existing samples already cover many top text, image generation, video, speech, and music models; this sample increases **variety** by adding a practical cutout workflow.

- **Popularity fit:** background removal tools are among the most-used practical workflows on Replicate Explore because they plug directly into product photography, marketing assets, and social creatives.
- **Variety gain:** unlike text-to-image/video samples, this one focuses on deterministic image cleanup and transparent PNG output.
- **Workflow value:** ideal precursor step before generation/editing chains (e.g., compositing with FLUX/Ideogram outputs).

## Features
- **One-click background removal** via `fofr/remove-background`.
- **Source + result side-by-side preview** in a single desktop UI.
- **Automatic PNG output download** for transparency-friendly workflows.
- **Inline API key entry** (or automatic prefill from `REPLICATE_API_TOKEN`).

## Prerequisites
```bash
pip install delphifmx replicate
```

## Running the Demo
1. Open `remove_background_pro.py`.
2. Enter your Replicate API key.
3. Click **Select Source Image** and choose a local image.
4. Click **Remove Background**.
5. Wait for the transparent PNG result to appear and save locally.
