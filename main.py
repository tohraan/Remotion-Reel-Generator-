"""
main.py - Enhanced Instagram Reel Generator with Animation Presets

Usage:
    python main.py "Your prompt here"
    python main.py --preset cinematic "Your prompt here"
    python main.py --preset explosive --theme tech_futuristic "Your prompt"
"""

import asyncio
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import List, Dict, Any

import edge_tts
import httpx
from pydub import AudioSegment

from config import Config
from drive_uploader import DriveUploader
from animation_presets import AnimationPresets

# Ensure directories exist
for directory in [Config.ASSETS_DIR, Config.TEMP_DIR, Config.OUTPUT_DIR]:
    Path(directory).mkdir(parents=True, exist_ok=True)


class TimingExtractor:
    """Extract word-level timing from Edge-TTS output"""
    
    @staticmethod
    async def get_word_timings(text: str, audio_path: str) -> List[Dict[str, Any]]:
        """Generate word timings from text and audio"""
        audio = AudioSegment.from_mp3(audio_path)
        duration = len(audio) / 1000.0
        
        words = text.split()
        word_count = len(words)
        
        timings = []
        time_per_word = duration / word_count
        
        current_time = 0
        for word in words:
            timings.append({
                "word": word,
                "start": round(current_time, 2),
                "end": round(current_time + time_per_word, 2)
            })
            current_time += time_per_word
        
        return timings


class ScriptGenerator:
    """Generate engaging reel scripts from prompts"""
    
    TEMPLATES = {
        "fact": """
        Did you know? {topic}
        
        Here's the fascinating truth: {detail_1}
        
        But wait, there's more. {detail_2}
        
        And the most surprising part? {detail_3}
        
        Now you know something incredible!
        """,
        
        "tutorial": """
        Want to learn about {topic}? Here's how.
        
        Step one: {step_1}
        
        Step two: {step_2}
        
        Step three: {step_3}
        
        And that's it! You're now ready to master {topic}.
        """,
        
        "story": """
        Let me tell you about {topic}.
        
        It all started when {beginning}
        
        Then, {middle}
        
        And finally, {end}
        
        What an incredible journey!
        """
    }
    
    @staticmethod
    def generate(prompt: str, template_type: str = "fact") -> str:
        """Generate script from prompt"""
        template = ScriptGenerator.TEMPLATES.get(template_type, ScriptGenerator.TEMPLATES["fact"])
        
        script = template.format(
            topic=prompt,
            detail_1="This is an amazing detail about the topic.",
            detail_2="Here's another fascinating aspect.",
            detail_3="The conclusion will blow your mind.",
            step_1="Start with the basics",
            step_2="Build on your foundation",
            step_3="Master the advanced concepts",
            beginning="everything changed",
            middle="the plot thickened",
            end="it all came together"
        )
        
        return script.strip()


from elevenlabs.client import AsyncElevenLabs

class VoiceGenerator:
    """Generate voiceover using ElevenLabs (Adam)"""
    
    @staticmethod
    def humanize_text(text: str) -> str:
        """Inject pauses and breathing room for the AI"""
        # Replace commas with longer pause markers
        text = text.replace(", ", " ... ")
        text = text.replace(". ", ". ... ")
        # Add breath at start? No, sticking to punctuation tuning.
        return text

    @staticmethod
    async def generate(text: str, output_path: str) -> str:
        """Generate voiceover and return path"""
        print(f"🎙️  Generating voice with ElevenLabs (Voice: {Config.VOICE})...")
        
        if not Config.ELEVENLABS_API_KEY:
            raise Exception("❌ One does not simply use ElevenLabs without an API Key.")

        client = AsyncElevenLabs(api_key=Config.ELEVENLABS_API_KEY)
        
        # Preprocess text for better prosody
        humanized_text = VoiceGenerator.humanize_text(text)
        print(f"   Humanized Script: {humanized_text[:50]}...")
        
        try:
            # Generate Audio
            # Note: convert() returns an async generator, do not await it directly
            audio_stream = client.text_to_speech.convert(
                text=humanized_text,
                voice_id=Config.VOICE,
                model_id="eleven_multilingual_v2" # Better prosody/breaths
            )
            
            # Save to file
            audio_bytes = b""
            async for chunk in audio_stream:
                audio_bytes += chunk
                
            with open(output_path, "wb") as f:
                f.write(audio_bytes)
                
            return output_path
            
        except Exception as e:
            print(f"❌ ElevenLabs Error: {e}")
            raise e


class ImageFetcher:
    """Fetch relevant images from free stock APIs"""
    
    @staticmethod
    async def fetch_from_pexels(query: str, count: int = 3) -> List[str]:
        """Fetch images from Pexels"""
        if not Config.PEXELS_API_KEY:
            return []
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.pexels.com/v1/search",
                headers={"Authorization": Config.PEXELS_API_KEY},
                params={"query": query, "per_page": count, "orientation": "portrait"}
            )
            
            if response.status_code != 200:
                return []
            
            data = response.json()
            return [photo["src"]["large2x"] for photo in data.get("photos", [])]
    
    @staticmethod
    async def download_image(url: str, save_path: str) -> str:
        """Download single image"""
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            
            if response.status_code == 200:
                with open(save_path, 'wb') as f:
                    f.write(response.content)
                return save_path
        
        return None
    
    @staticmethod
    async def fetch_images(query: str, count: int = 3) -> List[str]:
        """Fetch and download images"""
        urls = await ImageFetcher.fetch_from_pexels(query, count)
        
        if not urls:
            return []
        
        download_tasks = []
        for i, url in enumerate(urls):
            save_path = f"{Config.TEMP_DIR}/image_{i}.jpg"
            download_tasks.append(ImageFetcher.download_image(url, save_path))
        
        results = await asyncio.gather(*download_tasks)
        return [r for r in results if r is not None]


class ReelOrchestrator:
    """Main orchestration logic"""
    
    @staticmethod
    def extract_cta_keyword(script: str) -> str:
        """Extract codeword from script (e.g. DM 'LEADS' or Comment 'GROWTH')"""
        # Look for quoted strings after DM or Comment
        patterns = [
            r"(?i)DM [\"']([^\"']+)[\"']",
            r"(?i)Comment [\"']([^\"']+)[\"']",
            r"(?i)DM (?:me )?[\"']([^\"']+)[\"']",
            r"(?i)word (?:is )?[\"']([^\"']+)[\"']"
        ]
        for pattern in patterns:
            match = re.search(pattern, script)
            if match:
                return match.group(1).upper()
        return "EMAIL" # Default fallback

    @staticmethod
    async def create_reel(
        prompt: str,
        preset: str = "default",
        theme: str = "modern_minimal",
        direct_mode: bool = False
    ) -> str:
        """
        Main pipeline: prompt -> video
        Returns: path to rendered video
        """
        start_time = time.time()
        print(f"🎬 Starting reel generation for: '{prompt[:50]}...'")
        print(f"   Preset: {preset}")
        print(f"   Theme: {theme}")
        print(f"   Mode: {'Direct Input' if direct_mode else 'Generative'}")
        
        # Load animation preset
        preset_manager = AnimationPresets()
        animation_config = preset_manager.get_preset(preset)
        print(f"   Animation: {animation_config.get('name', preset)}")
        
        # Step 1: Generate script
        print("\n📝 Generating script...")
        if direct_mode:
            script = prompt
            print(f"✅ Using direct input ({len(script)} chars)")
        else:
            script = ScriptGenerator.generate(prompt)
            print(f"✅ Script generated ({len(script)} chars)")
        
        # Step 2: Parallel asset generation
        print("🎙️  Generating voiceover and fetching images...")
        voiceover_path = f"{Config.TEMP_DIR}/voiceover.mp3"
        
        if direct_mode:
            # Skip images for direct scripts to prevent long-query hangs
            voiceover = await VoiceGenerator.generate(script, voiceover_path)
            images = []
        else:
            voiceover, images = await asyncio.gather(
                VoiceGenerator.generate(script, voiceover_path),
                ImageFetcher.fetch_images(prompt, count=3)
            )
        print(f"✅ Voiceover generated: {voiceover_path}")
        print(f"✅ Images fetched: {len(images)} images")
        
        # Step 3: Extract timing
        print("⏱️  Analyzing timing...")
        word_timings = await TimingExtractor.get_word_timings(script, voiceover_path)
        
        # Get audio duration
        audio = AudioSegment.from_mp3(voiceover_path)
        duration = (len(audio) / 1000.0) + 5.0 # Add 5s buffer for Outro/CTA sequence
        
        # Convert assets to Data URIs for Remotion compatibility
        import base64

        with open(voiceover_path, "rb") as f:
            voice_b64 = base64.b64encode(f.read()).decode("utf-8")
        voice_uri = f"data:audio/mp3;base64,{voice_b64}"
        
        image_data_list = []
        if images:
            for i, img_path in enumerate(images):
                with open(img_path, "rb") as f:
                    img_b64 = base64.b64encode(f.read()).decode("utf-8")
                # Assume jpg/png detection (simplified to jpg for now)
                img_uri = f"data:image/jpeg;base64,{img_b64}"
                image_data_list.append({
                    "url": img_uri, 
                    "timestamp": i * (duration / len(images))
                })

        # Step 4: Prepare data for Remotion
        cta_keyword = ReelOrchestrator.extract_cta_keyword(script)
        print(f"🎯 Dynamic CTA Keyword: '{cta_keyword}'")

        remotion_data = {
            "script": script,
            "voiceover_path": voice_uri,
            "duration": duration,
            "word_timings": word_timings,
            "images": image_data_list,
            "theme": theme,
            "cta_keyword": cta_keyword,
            "fps": Config.FPS,
            "width": Config.WIDTH,
            "height": Config.HEIGHT,
            "animation_preset": animation_config  # Include animation config
        }
        
        # Save data JSON
        data_path = f"{Config.TEMP_DIR}/reel_data.json"
        with open(data_path, 'w') as f:
            json.dump(remotion_data, f, indent=2)
        
        print(f"✅ Data prepared: {data_path}")
        
        # Step 5: Render with Remotion
        print("🎨 Rendering video with Remotion...")
        output_path = f"{Config.OUTPUT_DIR}/reel_{preset}_{int(time.time())}.mp4"
        
        render_cmd = [
            "npx", "remotion", "render",
            "src/index.ts",
            "ReelComposition",
            output_path,
            f"--props={data_path}"
        ]
        
        process = subprocess.run(render_cmd, capture_output=True, text=True)
        
        if process.returncode != 0:
            print(f"❌ Rendering failed: {process.stderr}")
            raise Exception("Remotion rendering failed")
        
        elapsed = time.time() - start_time
        print(f"✅ Video rendered: {output_path}")
        print(f"⏱️  Total time: {elapsed:.2f} seconds")

        # Handle Drive Upload
        if hasattr(Config, 'AUTO_UPLOAD') and Config.AUTO_UPLOAD: # Fallback check
             args_upload = True
        else:
             args_upload = False

        return output_path


# CLI Entry Point
async def main():
    """Main entry point with argument parsing"""
    
    # Parse arguments
    preset = "default"
    theme = "modern_minimal"
    prompt = None
    direct_mode = False
    upload_mode = False
    
    args = sys.argv[1:]
    i = 0
    
    while i < len(args):
        if args[i] == "--preset" and i + 1 < len(args):
            preset = args[i + 1]
            i += 2
        elif args[i] == "--theme" and i + 1 < len(args):
            theme = args[i + 1]
            i += 2
        elif args[i] == "--direct":
            direct_mode = True
            i += 1
        elif args[i] == "--upload":
            upload_mode = True
            i += 1
        elif args[i] == "--help" or args[i] == "-h":
            print("""
Usage: python main.py [OPTIONS] "prompt"

Options:
  --preset <id>    Animation preset (default: default)
                   Options: default, explosive, smooth_elegant, cinematic,
                           minimal_modern, glitch_cyberpunk, organic_flow, retro_vhs
  
  --theme <id>     Visual theme (default: modern_minimal)
                   Options: modern_minimal, tech_futuristic, cinematic
  
  --help, -h       Show this help message

Examples:
  python main.py "The science of dreams"
  python main.py --preset cinematic "Amazing space facts"
  python main.py --preset explosive --theme tech_futuristic "AI revolution"

List animation presets:
  python animation_presets.py --list
            """)
            sys.exit(0)
        else:
            prompt = args[i]
            i += 1
    
    if not prompt:
        print("❌ Error: Prompt required")
        print("Usage: python main.py 'Your prompt here'")
        print("Try: python main.py --help")
        sys.exit(1)
    
    try:
        output_path = await ReelOrchestrator.create_reel(prompt, preset, theme, direct_mode)
        print(f"\n🎉 SUCCESS! Video saved to: {output_path}")

        # Check for upload
        if 'upload_mode' in locals() and upload_mode:
            try:
                uploader = DriveUploader()
                drive_link = uploader.upload_reel(output_path)
                print(f"\n🌐 Drive Link: {drive_link}")
            except Exception as e:
                print(f"\n⚠️ Drive Upload Failed: {str(e)}")

        print(f"\nValidate with: python video_previewer.py {output_path} --validate")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())