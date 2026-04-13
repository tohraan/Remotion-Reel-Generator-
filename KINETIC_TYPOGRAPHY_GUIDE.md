# Kinetic Typography & After Effects-Style Animations Guide

## 🎬 Overview

Your Instagram Reel Generator now features **professional kinetic typography** with After Effects-style camera movements, motion blur, and dynamic text animations.

---

## 🎨 Animation Styles

### 1. **Fly-In**
Words fly in from random directions with momentum.
- **Effect**: Explosive, energetic
- **Best for**: Attention-grabbing intros, action content
- **Technical**: Uses golden angle distribution for varied entry points

### 2. **Scale-Bounce**
Words bounce into place with spring physics.
- **Effect**: Playful, dynamic
- **Best for**: Fun facts, lighthearted content
- **Technical**: Spring animation with damping and stiffness

### 3. **Rotate-In**
Words spin and zoom into position.
- **Effect**: Dramatic, cinematic
- **Best for**: Reveals, important statements
- **Technical**: Combined rotation + scale interpolation

### 4. **Split-Flip**
Each letter flips independently like cards.
- **Effect**: Sophisticated, elegant
- **Best for**: Professional content, tutorials
- **Technical**: Per-character 3D rotation

### 5. **Glitch**
Digital glitch effect with chromatic aberration.
- **Effect**: Tech-focused, edgy
- **Best for**: Tech content, cyberpunk aesthetic
- **Technical**: Random offset with frame-based noise

---

## 📹 Camera Movements

### Zoom
Slow, continuous zoom creates depth and draws viewer in.
```typescript
// Customize intensity in preset
"zoom_intensity": 1.0  // Range: 0.5 (subtle) to 2.0 (dramatic)
```

### Pan
Horizontal camera movement adds cinematic feel.
```typescript
"pan_intensity": 1.0  // Range: 0.3 (gentle) to 1.8 (dynamic)
```

### Rotation
Subtle tilt creates unease or energy.
```typescript
"rotation": true  // Enable/disable camera tilt
```

### Parallax
Multi-layer depth with different movement speeds.
- Background particles: Slowest
- Images: Medium speed
- Text: Fastest (closest to camera)

---

## 🎭 Available Presets

### **default** - Mixed Kinetic
- Rotates through all 5 animation styles
- Balanced camera movement
- Good for: General content

**Example:**
```bash
python main.py "5 facts about the ocean"
```

### **explosive** - High Energy
- Aggressive animations (fly-in, rotate-in, glitch)
- Intense camera movement
- Lots of particles
- Good for: Viral content, sports, action

**Example:**
```bash
python main.py --preset explosive "Incredible athletic feats"
```

### **smooth_elegant** - Professional
- Subtle animations (scale-bounce, split-flip)
- Gentle camera work
- Minimal effects
- Good for: Business, educational, professional

**Example:**
```bash
python main.py --preset smooth_elegant "Marketing strategies"
```

### **cinematic** - Movie Trailer Style
- Dramatic camera movement
- Large, bold text
- Vignette effect
- Good for: Storytelling, dramatic content

**Example:**
```bash
python main.py --preset cinematic "The rise and fall of empires"
```

### **minimal_modern** - Clean & Simple
- No camera movement
- Single animation style
- Ultra-clean look
- Good for: Minimalist brands, quotes

**Example:**
```bash
python main.py --preset minimal_modern "Daily motivation"
```

### **glitch_cyberpunk** - Tech Aesthetic
- Heavy glitch effects
- Neon colors
- Tech-focused animations
- Good for: Tech content, gaming, crypto

**Example:**
```bash
python main.py --preset glitch_cyberpunk --theme tech_futuristic "AI revolution"
```

### **organic_flow** - Natural Movement
- Smooth, flowing animations
- Moderate particle effects
- Balanced feel
- Good for: Nature, wellness, lifestyle

**Example:**
```bash
python main.py --preset organic_flow "Meditation techniques"
```

### **retro_vhs** - 80s/90s Aesthetic
- VHS tracking effects
- Scanlines
- Retro feel
- Good for: Nostalgia, vintage content

**Example:**
```bash
python main.py --preset retro_vhs "80s music history"
```

---

## 🎨 Visual Themes

Combine with animation presets for complete control:

### **modern_minimal**
- Purple/violet gradient background
- Clean, modern font (Montserrat)
- Gold accents
```bash
python main.py --theme modern_minimal "Your prompt"
```

### **tech_futuristic**
- Dark blue/purple space theme
- Futuristic font (Orbitron)
- Neon green/pink accents
```bash
python main.py --theme tech_futuristic "Your prompt"
```

### **cinematic**
- Dark, dramatic background
- Bold font (Bebas Neue)
- Red accents
```bash
python main.py --theme cinematic "Your prompt"
```

---

## 🔧 Advanced Customization

### Create Custom Preset

```bash
python animation_presets.py --create
```

Interactive wizard will ask:
1. Preset name and description
2. Camera settings (zoom, pan, rotation)
3. Animation styles to use
4. Typography settings
5. Effects (motion blur, particles, glow)

### Modify Existing Preset

Edit `animation_presets.json`:

```json
{
  "my_custom": {
    "name": "My Custom Style",
    "description": "Perfect for my brand",
    "camera": {
      "zoom": true,
      "pan": false,
      "rotation": false,
      "zoom_intensity": 0.8
    },
    "typography": {
      "styles_rotation": ["scale-bounce", "split-flip"],
      "font_size": 68,
      "font_weight": 700
    },
    "effects": {
      "motion_blur": true,
      "particles": true,
      "particle_count": 25,
      "glow": false
    }
  }
}
```

Then use:
```bash
python main.py --preset my_custom "Your prompt"
```

---

## 🎯 Best Practices

### For Maximum Engagement

1. **Use explosive preset** for viral potential
2. **Match preset to content type**:
   - Facts → default or explosive
   - Tutorials → smooth_elegant
   - Stories → cinematic
   - Tech → glitch_cyberpunk
   - Quotes → minimal_modern

3. **Combine preset + theme strategically**:
   ```bash
   # Tech content
   python main.py --preset glitch_cyberpunk --theme tech_futuristic "AI news"
   
   # Dramatic storytelling
   python main.py --preset cinematic --theme cinematic "Historical events"
   
   # Professional business
   python main.py --preset smooth_elegant --theme modern_minimal "Business tips"
   ```

### Performance Optimization

1. **Motion blur** is expensive - disable for faster renders:
   - Edit preset: `"motion_blur": false`

2. **Reduce particle count** for speed:
   - Default: 30 particles
   - Fast: 15 particles
   - Ultra-fast: 0 particles

3. **Simplify camera movement**:
   - Disable rotation (fastest)
   - Reduce zoom/pan intensity

---

## 📊 Technical Details

### Motion Blur Implementation
```typescript
// Renders 3 frames offset by 0.05
// Combines with reduced opacity for blur effect
const blurSamples = 3;
```

Disable in preset for 30% faster rendering.

### Easing Functions

- **easeOutQuint**: Smooth deceleration (default)
- **easeInOutQuint**: Smooth acceleration + deceleration
- **easeOutBack**: Overshoot effect (bounce-like)
- **Bezier curves**: Custom timing control

### Camera Math

```typescript
// Zoom: 1.0 → 1.3 over duration
zoom = interpolate(frame, [0, duration], [1, 1.3])

// Pan: -30px → 30px (subtle sway)
panX = interpolate(frame, [0, duration/2, duration], [-30, 0, 30])

// Rotation: -1° → 0.5° → -0.5° (dynamic tilt)
rotation = interpolate(frame, [0, duration/2, duration], [-1, 0.5, -0.5])
```

### Parallax Layers

1. **Background particles**: `translateZ(0px)` - slowest
2. **Decorative elements**: `translateZ(30-50px)` - medium
3. **Images**: `translateZ(-20px)` - pushes back slightly
4. **Text**: `translateZ(100px)` - closest, fastest movement

---

## 🚀 Quick Commands

```bash
# List all presets
python animation_presets.py --list

# Generate with specific preset
python main.py --preset cinematic "Your prompt"

# Combine preset + theme
python main.py --preset explosive --theme tech_futuristic "Tech news"

# Create custom preset
python animation_presets.py --create

# Validate output
python video_previewer.py output/reel_*.mp4 --validate

# Create preview GIF
python video_previewer.py output/reel_*.mp4 --gif
```

---

## 🎬 Example Workflows

### Viral Social Content
```bash
python main.py --preset explosive --theme modern_minimal "Mind-blowing ocean facts"
python video_previewer.py output/reel_*.mp4 --gif
# Upload to Instagram
```

### Professional Tutorial
```bash
python main.py --preset smooth_elegant --theme modern_minimal "How to code in Python"
python video_previewer.py output/reel_*.mp4 --validate
```

### Tech News
```bash
python main.py --preset glitch_cyberpunk --theme tech_futuristic "Latest AI breakthrough"
```

### Motivational Quote
```bash
python main.py --preset minimal_modern --theme cinematic "Never give up on your dreams"
```

---

## 🔍 Troubleshooting

### Animations too fast/slow
- Adjust word timing in `TimingExtractor.get_word_timings()`
- Or use Whisper for accurate timing

### Text too small/large
- Edit preset: `"font_size": 72` (range: 48-96)

### Camera movement too intense
- Reduce intensity: `"zoom_intensity": 0.5`
- Disable: `"zoom": false`

### Rendering too slow
- Disable motion blur: `"motion_blur": false`
- Reduce particles: `"particle_count": 15`
- Reduce FPS: Set `FPS=24` in `.env`

### Want more animation variety
- Add more styles to rotation: `"styles_rotation": ["fly-in", "scale-bounce", "rotate-in", "split-flip", "glitch"]`

---

## 📚 Resources

- **Remotion Docs**: https://www.remotion.dev/docs
- **Easing Functions**: https://easings.net/
- **After Effects Equivalents**:
  - Camera Zoom = Transform > Scale
  - Camera Pan = Transform > Position
  - Rotation = Transform > Rotation
  - Motion Blur = Time > Pixel Motion Blur
  - Parallax = 3D Layers with different Z-positions

---

**Pro Tip:** Create 3-5 variations of the same prompt with different presets, then A/B test on Instagram to see which style resonates with your audience! 🚀