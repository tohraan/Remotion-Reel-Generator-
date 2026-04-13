import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Video settings
    FPS = int(os.getenv('FPS', 30))
    WIDTH = int(os.getenv('WIDTH', 1080))
    HEIGHT = int(os.getenv('HEIGHT', 1920))
    ASPECT_RATIO = f"{WIDTH}:{HEIGHT}"
    
    # API keys
    PEXELS_API_KEY = os.getenv('PEXELS_API_KEY')
    UNSPLASH_ACCESS_KEY = os.getenv('UNSPLASH_ACCESS_KEY')
    ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')
    
    # Voice settings
    VOICE_PROVIDER = "elevenlabs" 
    VOICE = "pNInz6obpgDQGcFmaJgB" # Adam ID
    
    # Paths
    ASSETS_DIR = './assets'
    TEMP_DIR = './assets/temp'
    OUTPUT_DIR = './output'
    TEMPLATES_DIR = './templates'
    
    # Performance
    MAX_CONCURRENT_DOWNLOADS = int(os.getenv('MAX_CONCURRENT_DOWNLOADS', 3))
    RENDER_TIMEOUT = int(os.getenv('RENDER_TIMEOUT', 60))
