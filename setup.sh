#!/bin/bash

# setup.sh - One-command setup for Instagram Reel Generator
# Usage: bash setup.sh

set -e  # Exit on error

echo "================================================"
echo "🎬 Instagram Reel Generator - Setup Script"
echo "================================================"
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo "ℹ️  $1"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Step 1: Check prerequisites
echo "Step 1/7: Checking prerequisites..."
echo ""

MISSING_DEPS=0

# Check Python
if command_exists python3; then
    PYTHON_VERSION=$(python3 --version | cut -d ' ' -f 2)
    print_success "Python found: $PYTHON_VERSION"
else
    print_error "Python 3.9+ is required but not found"
    print_info "Install from: https://www.python.org/downloads/"
    MISSING_DEPS=1
fi

# Check Node.js
if command_exists node; then
    NODE_VERSION=$(node --version)
    print_success "Node.js found: $NODE_VERSION"
else
    print_error "Node.js 18+ is required but not found"
    print_info "Install from: https://nodejs.org/"
    MISSING_DEPS=1
fi

# Check FFmpeg
if command_exists ffmpeg; then
    FFMPEG_VERSION=$(ffmpeg -version | head -n1 | cut -d ' ' -f 3)
    print_success "FFmpeg found: $FFMPEG_VERSION"
else
    print_error "FFmpeg is required but not found"
    print_info "Install from: https://ffmpeg.org/download.html"
    MISSING_DEPS=1
fi

# Check npm
if command_exists npm; then
    NPM_VERSION=$(npm --version)
    print_success "npm found: $NPM_VERSION"
else
    print_error "npm is required but not found"
    MISSING_DEPS=1
fi

if [ $MISSING_DEPS -eq 1 ]; then
    echo ""
    print_error "Missing dependencies. Please install them and try again."
    exit 1
fi

echo ""

# Step 2: Create directory structure
echo "Step 2/7: Creating directory structure..."
echo ""

mkdir -p src
mkdir -p assets/temp
mkdir -p assets/images
mkdir -p assets/voiceovers
mkdir -p output
mkdir -p templates

print_success "Directories created"
echo ""

# Step 3: Create Python virtual environment
echo "Step 3/7: Setting up Python virtual environment..."
echo ""

if [ ! -d "venv" ]; then
    python3 -m venv venv
    print_success "Virtual environment created"
else
    print_warning "Virtual environment already exists, skipping..."
fi

# Activate virtual environment
source venv/bin/activate
print_success "Virtual environment activated"
echo ""

# Step 4: Create requirements.txt
echo "Step 4/7: Creating requirements.txt..."
echo ""

cat > requirements.txt << EOF
edge-tts==6.1.9
pydub==0.25.1
httpx==0.25.2
python-dotenv==1.0.0
pillow>=10.3.0
aiofiles==23.2.1
jsonschema==4.20.0
EOF

print_success "requirements.txt created"
echo ""

# Step 5: Install Python dependencies
echo "Step 5/7: Installing Python dependencies..."
echo ""

pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt

print_success "Python dependencies installed"
echo ""

# Step 6: Create package.json
echo "Step 6/7: Creating package.json..."
echo ""

cat > package.json << EOF
{
  "name": "instagram-reel-generator",
  "version": "1.0.0",
  "description": "Autonomous Instagram Reel generator using Python + Remotion",
  "scripts": {
    "render": "remotion render",
    "preview": "remotion preview"
  },
  "dependencies": {
    "remotion": "^4.0.87",
    "@remotion/cli": "^4.0.87",
    "framer-motion": "^10.16.16",
    "react": "^18.2.0",
    "react-dom": "^18.2.0"
  }
}
EOF

print_success "package.json created"
echo ""

# Step 7: Install Node dependencies
echo "Step 7/7: Installing Node.js dependencies..."
echo ""

npm install

print_success "Node.js dependencies installed"
echo ""

# Create .env file
echo "Creating .env configuration file..."
echo ""

cat > .env << EOF
# Voice Settings
VOICE=en-US-GuyNeural
FPS=30
WIDTH=1080
HEIGHT=1920

# API Keys (Optional - free tier)
PEXELS_API_KEY=
UNSPLASH_ACCESS_KEY=

# Performance
MAX_CONCURRENT_DOWNLOADS=3
RENDER_TIMEOUT=60
EOF

print_success ".env file created"
echo ""

# Create .gitignore
echo "Creating .gitignore..."
echo ""

cat > .gitignore << EOF
# Python
venv/
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.egg-info/

# Node
node_modules/
package-lock.json

# Assets
assets/temp/
assets/images/
assets/voiceovers/
output/

# Environment
.env
.env.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
EOF

print_success ".gitignore created"
echo ""

# Create config.py
echo "Creating config.py..."
echo ""

cat > config.py << 'EOF'
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Video settings
    FPS = int(os.getenv('FPS', 30))
    WIDTH = int(os.getenv('WIDTH', 1080))
    HEIGHT = int(os.getenv('HEIGHT', 1920))
    ASPECT_RATIO = f"{WIDTH}:{HEIGHT}"
    
    # Voice settings
    VOICE = os.getenv('VOICE', 'en-US-GuyNeural')
    VOICE_RATE = '+0%'
    VOICE_PITCH = '+0Hz'
    
    # API keys
    PEXELS_API_KEY = os.getenv('PEXELS_API_KEY')
    UNSPLASH_ACCESS_KEY = os.getenv('UNSPLASH_ACCESS_KEY')
    
    # Paths
    ASSETS_DIR = './assets'
    TEMP_DIR = './assets/temp'
    OUTPUT_DIR = './output'
    TEMPLATES_DIR = './templates'
    
    # Performance
    MAX_CONCURRENT_DOWNLOADS = int(os.getenv('MAX_CONCURRENT_DOWNLOADS', 3))
    RENDER_TIMEOUT = int(os.getenv('RENDER_TIMEOUT', 60))
EOF

print_success "config.py created"
echo ""

# Create remotion.config.ts
echo "Creating remotion.config.ts..."
echo ""

cat > remotion.config.ts << 'EOF'
import { Config } from "@remotion/cli/config";

Config.setVideoImageFormat("jpeg");
Config.setOverwriteOutput(true);
Config.setConcurrency(2);
EOF

print_success "remotion.config.ts created"
echo ""

# Create basic src/index.ts
echo "Creating Remotion entry point..."
echo ""

cat > src/index.ts << 'EOF'
import { registerRoot } from "remotion";
import { ReelComposition } from "./Video";

registerRoot(ReelComposition);
EOF

print_success "src/index.ts created"
echo ""

# Create quick test script
echo "Creating test script..."
echo ""

cat > test_setup.sh << 'EOF'
#!/bin/bash

echo "Testing Edge-TTS installation..."
source venv/bin/activate

python3 << PYTHON
import asyncio
import edge_tts

async def test():
    try:
        communicate = edge_tts.Communicate("Testing voice setup", "en-US-GuyNeural")
        await communicate.save("test_voice.mp3")
        print("✅ Edge-TTS working! Test audio saved: test_voice.mp3")
        return True
    except Exception as e:
        print(f"❌ Edge-TTS error: {e}")
        return False

if asyncio.run(test()):
    exit(0)
else:
    exit(1)
PYTHON
EOF

chmod +x test_setup.sh

print_success "test_setup.sh created"
echo ""

# Create run script
echo "Creating run script..."
echo ""

cat > generate_reel.sh << 'EOF'
#!/bin/bash
source venv/bin/activate
python main.py "$@"
EOF

chmod +x generate_reel.sh

print_success "generate_reel.sh created"
echo ""

# Final summary
echo "================================================"
echo "🎉 Setup Complete!"
echo "================================================"
echo ""
echo "Next Steps:"
echo ""
echo "1. Copy the main.py code from INSTRUCTIONS.md"
echo "2. Copy the src/Video.tsx code from INSTRUCTIONS.md"
echo "3. Test the setup:"
echo "   ./test_setup.sh"
echo ""
echo "4. Generate your first reel:"
echo "   ./generate_reel.sh 'Amazing facts about space'"
echo ""
echo "Optional:"
echo "- Add Pexels API key to .env for image support"
echo "- Customize templates in templates/"
echo "- Adjust settings in .env"
echo ""
print_success "Ready to create amazing Instagram Reels! 🚀"
echo ""