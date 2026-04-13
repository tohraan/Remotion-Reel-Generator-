# GUIDELINES.md - Instagram Reel Generator System Architecture

## System Overview

This document defines the architectural principles, design patterns, and system boundaries for an autonomous Instagram Reel generation pipeline that transforms a text prompt into a professional 9:16 video in under 60 seconds.

---

## Core Architecture Principles

### 1. **Separation of Concerns**
```
Orchestration Layer (Python)
    ├─ Content Generation (Script, timing)
    ├─ Asset Acquisition (Voice, images)
    └─ Data Pipeline (JSON transfer to Remotion)

Rendering Layer (Remotion/Node.js)
    ├─ Visual Composition (Layers, animations)
    ├─ Text Synchronization (Word-level timing)
    └─ Video Export (9:16 MP4)
```

### 2. **Async-First Design**
All I/O-bound operations must execute in parallel:
- Voice generation (Edge-TTS)
- Image fetching (Pexels/Unsplash API)
- Script generation (template or LLM)

**Anti-pattern:** Sequential operations that block each other
**Pattern:** Use `asyncio.gather()` for parallel execution

### 3. **Data Contract**
The Python orchestrator and Remotion renderer communicate via a strict JSON schema:

```json
{
  "script": "Full narration text",
  "voiceover_path": "./assets/voiceover.mp3",
  "duration": 28.5,
  "word_timings": [
    {"word": "Hello", "start": 0.0, "end": 0.4},
    {"word": "world", "start": 0.5, "end": 0.9}
  ],
  "images": [
    {"url": "./assets/img1.jpg", "timestamp": 3.2},
    {"url": "./assets/img2.jpg", "timestamp": 8.7}
  ],
  "theme": "modern_minimal"
}
```

### 4. **Fail-Fast Philosophy**
- Validate inputs before expensive operations
- Check file existence before rendering
- Abort early if assets fail to download
- Provide actionable error messages

---

## System Components

### Component 1: Python Orchestrator (`main.py`)

**Responsibilities:**
1. Parse user prompt
2. Generate reel script (template-based or LLM)
3. Synthesize voiceover with Edge-TTS
4. Fetch relevant images from stock APIs
5. Analyze voiceover for word-level timing
6. Package data for Remotion
7. Trigger Remotion render subprocess
8. Clean up temporary files

**Key Technologies:**
- `asyncio` - Async/await concurrency
- `edge-tts` - Microsoft Text-to-Speech
- `pydub` - Audio analysis and timing extraction
- `requests`/`httpx` - Image downloads
- `json` - Data serialization
- `subprocess` - Remotion render invocation

**Performance Target:** 15-20 seconds for orchestration phase

---

### Component 2: Remotion Renderer (`src/Video.tsx`)

**Responsibilities:**
1. Receive JSON data contract
2. Compose 9:16 video with multiple layers:
   - Background (gradient/pattern)
   - Decorative elements (abstract shapes, SVGs)
   - Main text (synced to voiceover)
   - Image overlays (pop-in animations)
   - Hand-drawn overlays (optional Lottie)
3. Export as MP4 (H.264, 1080x1920)

**Key Technologies:**
- `remotion` - React-based video framework
- `@remotion/player` - Preview capability
- Framer Motion or CSS animations
- Custom easing functions

**Performance Target:** 30-40 seconds for rendering

---

## Design Patterns

### Pattern 1: **Producer-Consumer Pipeline**
```python
async def orchestrate(prompt: str):
    # Produce assets in parallel
    script, voiceover, images = await asyncio.gather(
        generate_script(prompt),
        generate_voiceover(script),
        fetch_images(prompt)
    )
    
    # Transform data
    data = prepare_remotion_data(script, voiceover, images)
    
    # Consume in Remotion
    render_video(data)
```

### Pattern 2: **Timing Synchronization**
Word-level timing is critical for text animations:

```python
# Python: Extract timing from TTS metadata
timings = parse_edge_tts_timing(voiceover_file)

# Remotion: Render text based on frame timing
{timings.map((word, i) => (
  <Sequence from={word.start * fps} durationInFrames={word.duration * fps}>
    <Word>{word.text}</Word>
  </Sequence>
))}
```

### Pattern 3: **Theme System**
Pre-defined visual themes ensure consistency:

```javascript
const themes = {
  modern_minimal: {
    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    fontFamily: 'Inter',
    textColor: '#ffffff',
    accentColor: '#ffd700'
  },
  tech_futuristic: {
    background: '#0a0e27',
    fontFamily: 'Orbitron',
    textColor: '#00ff88',
    accentColor: '#ff0080'
  }
}
```

---

## Quality Standards

### Visual Requirements (Instagram-Worthy)
1. **Resolution:** 1080x1920 (9:16 ratio)
2. **Frame Rate:** 30 FPS minimum
3. **Text Readability:** Minimum 48px font size, high contrast
4. **Animation Smoothness:** Easing functions (cubic-bezier), no linear animations
5. **Layer Hierarchy:** Background → Decor → Images → Text → Overlays

### Audio Requirements
1. **Voice:** Male narrator (Edge-TTS: `en-US-GuyNeural`)
2. **Format:** 44.1kHz, 192kbps MP3
3. **Normalization:** -16 LUFS loudness
4. **Clarity:** No clipping, clean pronunciation

### Performance Requirements
1. **Total Time:** < 60 seconds (orchestration + render)
2. **Memory:** < 2GB RAM usage
3. **Disk:** < 500MB temporary files
4. **Error Rate:** < 5% failure rate on valid prompts

---

## Self-Annealing Process

The system includes built-in resilience mechanisms:

### Level 1: Retry Logic
```python
@retry(max_attempts=3, backoff=2.0)
async def fetch_image(url: str):
    # Auto-retry failed downloads
    pass
```

### Level 2: Fallback Assets
```python
if not images:
    # Use default gradient background instead of failing
    images = [DEFAULT_BACKGROUND]
```

### Level 3: Quality Degradation
```python
if render_time > 45:
    # Reduce FPS from 60 to 30 to meet deadline
    config.fps = 30
```

### Level 4: Health Checks
```python
def validate_system():
    checks = [
        check_node_installed(),
        check_remotion_installed(),
        check_edge_tts_available(),
        check_disk_space() > 1GB
    ]
    return all(checks)
```

---

## Scalability Considerations

### Current Scope (v1.0)
- Single prompt → Single reel
- Local execution only
- Synchronous rendering (one at a time)

### Future Expansion (v2.0+)
- Batch processing (multiple prompts → multiple reels)
- Distributed rendering (render farm)
- Cloud deployment (Google Cloud Run, AWS Lambda)
- Custom voice cloning integration

---

## Security & Privacy

### Data Handling
1. **No persistent storage** of user prompts by default
2. **Temporary files** deleted after render completion
3. **API keys** stored in `.env`, never committed to git
4. **Image licensing** verified (Pexels/Unsplash free tier compliance)

### Rate Limiting
1. **Edge-TTS:** No official limits, but respect fair use (~100 requests/hour)
2. **Pexels API:** 200 requests/hour (free tier)
3. **Unsplash API:** 50 requests/hour (free tier)

---

## Testing Strategy

### Unit Tests
- Script generation logic
- Timing extraction from audio
- JSON schema validation

### Integration Tests
- End-to-end prompt → video pipeline
- Asset fetching with mocked APIs
- Remotion rendering with sample data

### Performance Tests
- Benchmark total execution time
- Memory profiling during render
- Concurrent request handling

---

## Documentation Standards

All code must include:
1. **Docstrings** for functions (Google style)
2. **Type hints** for all function signatures
3. **Inline comments** for complex logic
4. **README examples** for common use cases

---

## Success Metrics

The system is considered successful if:

1. ✅ 95% of valid prompts generate a complete video
2. ✅ Average total time < 60 seconds
3. ✅ Videos meet Instagram upload requirements (format, ratio, duration)
4. ✅ Text is perfectly synced with voiceover
5. ✅ Visual quality rated 7/10+ by human reviewers
6. ✅ Zero cost per reel (all free tools)

---

## Governance

### Change Management
- All architecture changes require updating this document
- Breaking changes to JSON schema require version bump
- New dependencies must be justified (performance, features, licensing)

### Code Review Checklist
- [ ] Async operations used where applicable
- [ ] Error handling implemented
- [ ] Type hints added
- [ ] Performance impact measured
- [ ] Documentation updated

---

**Version:** 1.0  
**Last Updated:** January 2026  
**Maintainer:** System Architect