# Deployment Instructions - Instagram Reel Generator

This folder contains the production-ready source code for the Instagram Reel Generator.

## Prerequisites
- Python 3.9+
- Node.js 18+
- FFmpeg installed on the system

## Setup
1. **API Keys**: Open `.env.example`, fill in your API keys (ElevenLabs, Drive, etc.), and rename it to `.env`.
2. **Drive Credentials**: Place your `credentials.json` in the `credentials/` folder.
3. **Run Setup**: Execute the setup script to install dependencies:
   ```bash
   bash setup.sh
   ```

## Deployment (Vercel)
This repository is configured for **Static Site Deployment** on Vercel. 
- **Build Step**: Generates a web bundle of your reels for browser preview.
- **Note**: MP4 video rendering is NOT performed on Vercel; it must be run locally or via Remotion Lambda.

## Usage (Local Video Rendering)
Generate a reel using the main script on your local machine:
```bash
./venv/bin/python main.py --preset royal_chic --upload --direct "Your script here"
```

Detailed documentation can be found in the project root `README.md`.
