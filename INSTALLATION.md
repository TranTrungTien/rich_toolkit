# VoxDub Studio - Installation & Configuration Guide

## Quick Start

### Windows Installation

1. **Download and Extract**
   - Extract the VoxDub folder to a location of your choice
   - Recommended: `C:\VoxDub` or your Desktop

2. **Run Setup**
   - Double-click `setup.bat`
   - Follow the installation wizard
   - This will:
     - Check Python and ffmpeg
     - Install dependencies (~200 MB)
     - Install Whisper ASR (~500 MB)
     - Install VieNeu TTS (~800 MB)
     - Optionally install GPU support (~2 GB)

3. **Configure Translation Provider**
   - Run `first_run_wizard.bat` OR
   - Edit `.env` file manually
   - Choose: VoxDub Cloud / Gemini / OpenRouter

4. **Start Application**
   - Double-click `chay_app.bat`
   - Application opens in browser at `http://localhost:8501`

---

## Prerequisites

### Required

- **Python 3.10 or higher**
  - Download: https://www.python.org/downloads/
  - ⚠️ **IMPORTANT**: Check "Add Python to PATH" during installation

- **ffmpeg**
  - Download: https://www.gyan.dev/ffmpeg/builds/
  - Extract and add `bin` folder to Windows PATH
  - Used for video/audio processing

### Optional

- **NVIDIA GPU with CUDA** (10x faster processing)
  - Accelerates Whisper ASR and Demucs vocal separation
  - Requires: NVIDIA drivers from https://www.nvidia.com/download/
  - Install with: `cai_them_gpu.bat`

---

## Translation Provider Setup

VoxDub supports three translation providers. Choose based on your needs:

### Option 1: VoxDub Cloud (Recommended)

**Pros:**
- Optimized prompts and context handling
- Automatic video analysis and review passes
- Idempotent job IDs prevent double-charging on retry
- Credit management built-in

**Cons:**
- Requires VoxDub backend deployment
- Not fully open-source

**Setup:**
```env
TRANSLATE_PROVIDER=voxdub
VOXDUB_API_URL=http://your-backend-url:3001
```

**Requirements:**
- Deploy VoxDub backend (see `control_server/README.md`)
- Backend handles API keys server-side

---

### Option 2: Gemini Direct

**Pros:**
- Free tier: 15 requests/minute
- Direct Google Gemini API integration
- Fast and reliable
- No backend needed

**Cons:**
- No automatic video analysis
- No review pass
- Must manage API key client-side
- Rate limits on free tier

**Setup:**
1. Get free API key: https://aistudio.google.com/apikey
2. Configure in `.env`:
```env
TRANSLATE_PROVIDER=gemini
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-2.0-flash-exp
```

**Rate Limits:**
- Free tier: 15 RPM (requests per minute)
- Paid tier: 1000 RPM

---

### Option 3: OpenRouter

**Pros:**
- Access to multiple AI models
- Flexible pricing
- Free tier available
- No backend needed

**Cons:**
- No automatic video analysis
- No review pass
- Must manage API key client-side
- Rate limits vary by model

**Setup:**
1. Get API key: https://openrouter.ai/keys
2. Configure in `.env`:
```env
TRANSLATE_PROVIDER=openrouter
OPENROUTER_API_KEY=your_api_key_here
OPENROUTER_MODEL=google/gemini-2.0-flash-exp:free
```

**Popular Models:**
- `google/gemini-2.0-flash-exp:free` (recommended, free)
- `anthropic/claude-3.5-sonnet`
- `openai/gpt-4`

---

## ASR Engine Selection

### Whisper (Recommended)

**Use for:** All languages

**Models:**
- `auto` (recommended): large-v3 on GPU, medium on CPU
- `large-v3`: Best accuracy, slow
- `medium`: Good balance
- `small`: Faster, lower accuracy
- `tiny`: Fastest, lowest accuracy

**Configuration:**
```env
ASR_ENGINE=whisper
WHISPER_MODEL=auto
```

**GPU Acceleration:**
- Install GPU support: `cai_them_gpu.bat`
- 10x faster than CPU
- Requires NVIDIA GPU with CUDA

---

### Paraformer

**Use for:** Chinese only (higher accuracy than Whisper)

**Setup:**
```bash
py scripts\setup_paraformer.py
```

**Configuration:**
```env
ASR_ENGINE=paraformer
DEFAULT_SOURCE_LANG=zh-CN
```

**Note:** CPU only (ONNX), no GPU acceleration

---

## Quality Presets

### Fast
- Whisper: medium model
- Background: 16kHz mono
- Translation: single pass
- Karaoke: estimated timing

**Use for:** Quick previews

### Balanced (Recommended)
- Whisper: auto (large-v3 on GPU)
- Background: 44.1kHz stereo
- Translation: analysis + main + review
- Karaoke: Whisper alignment

**Use for:** Production videos

### Quality
- Whisper: large-v3 always
- Background: 44.1kHz stereo
- Translation: analysis + main + review
- Karaoke: Whisper alignment

**Use for:** Best quality, slower

---

## GPU Acceleration

### Benefits
- Whisper ASR: 10x faster
- Demucs vocal separation: 10x faster
- Overall pipeline: 3-5x faster

### Requirements
- NVIDIA GPU with CUDA support
- Windows 10/11
- ~2 GB disk space for PyTorch

### Installation

**Automatic:**
```bash
cai_them_gpu.bat
```

**Manual:**
```bash
python -m venv .venv-gpu
.venv-gpu\Scripts\activate
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
pip install demucs
```

### Verification

GPU status is logged at pipeline start:
```
Machine Configuration: 8 cores, RAM 15.2/32.0 GB
GPU Status: ✓ available (venv-gpu: present)
```

If GPU unavailable:
```
GPU Status: ✗ not available (venv-gpu: missing)
```

---

## Troubleshooting

### Python not found

**Error:**
```
[ERROR] Python not found.
```

**Solution:**
1. Download Python 3.10+ from https://www.python.org/downloads/
2. **IMPORTANT:** Check "Add Python to PATH" during installation
3. Restart command prompt
4. Run `setup.bat` again

---

### ffmpeg not found

**Error:**
```
[WARNING] ffmpeg not found. Cannot export videos.
```

**Solution:**
1. Download "full" build: https://www.gyan.dev/ffmpeg/builds/
2. Extract to `C:\ffmpeg`
3. Add `C:\ffmpeg\bin` to Windows PATH:
   - Search "Environment Variables" in Windows
   - Edit "Path" variable
   - Add new entry: `C:\ffmpeg\bin`
4. Restart command prompt
5. Run `setup.bat` again

---

### GPU not detected

**Error:**
```
GPU Status: ✗ not available
```

**Solution:**
1. Check if you have NVIDIA GPU (not AMD/Intel)
2. Update NVIDIA drivers: https://www.nvidia.com/download/
3. Verify CUDA support:
   ```bash
   .venv-gpu\Scripts\python -c "import torch; print(torch.cuda.is_available())"
   ```
4. If still fails, reinstall GPU support:
   ```bash
   cai_them_gpu.bat
   ```

---

### Language auto-detection error

**Error:**
```
Language must be explicitly specified by user.
Automatic language detection is disabled.
```

**Solution:**
- This is by design for accuracy
- Select source language in UI before processing
- Supported languages: Chinese, English, Japanese, Korean, etc.

---

### Paraformer not available

**Error:**
```
Paraformer is selected but not installed.
```

**Solution:**
```bash
py scripts\setup_paraformer.py
```

Or switch to Whisper:
```env
ASR_ENGINE=whisper
```

---

### Translation API key missing

**Gemini Error:**
```
GEMINI_API_KEY not configured.
```

**Solution:**
1. Get free API key: https://aistudio.google.com/apikey
2. Add to `.env`:
   ```env
   GEMINI_API_KEY=your_key_here
   ```

**OpenRouter Error:**
```
OPENROUTER_API_KEY not configured.
```

**Solution:**
1. Get API key: https://openrouter.ai/keys
2. Add to `.env`:
   ```env
   OPENROUTER_API_KEY=your_key_here
   ```

---

### Rate limit exceeded

**Error:**
```
Gemini rate limit exceeded (429)
```

**Solution:**
- Free tier: 15 RPM limit
- Reduce `TRANSLATE_BATCH_SIZE` to slow down requests
- Wait 60 seconds between retries
- Upgrade to paid tier for higher limits

---

## Advanced Configuration

### Memory Optimization

**Low RAM (8 GB):**
```env
VIENEU_MAX_WORKERS=2
PARALLEL_WORKERS=2
HQ_BACKGROUND=false
```

**High RAM (32 GB+):**
```env
VIENEU_MAX_WORKERS=6
PARALLEL_WORKERS=8
HQ_BACKGROUND=true
```

### Speed vs Quality Trade-offs

**Faster Processing:**
```env
QUALITY_PRESET=fast
WHISPER_MODEL=medium
WHISPER_BEAM_SIZE=1
TRANSLATE_ANALYSIS=false
TRANSLATE_REVIEW=false
KARAOKE_ALIGNMENT=false
```

**Best Quality:**
```env
QUALITY_PRESET=quality
WHISPER_MODEL=large-v3
WHISPER_BEAM_SIZE=5
TRANSLATE_ANALYSIS=true
TRANSLATE_REVIEW=true
KARAOKE_ALIGNMENT=true
```

### Video Speed Adjustment

**Slower video (more time for Vietnamese):**
```env
VIDEO_SPEED=0.82  # video 22% longer
VOICE_SPEED=1.0   # normal voice speed
```

**Faster voice:**
```env
VIDEO_SPEED=1.0   # normal video speed
VOICE_SPEED=1.2   # voice 20% faster
```

---

## File Structure

```
VoxDub/
├── setup.bat                    # Main installer
├── first_run_wizard.bat        # Configuration wizard
├── cai_them_gpu.bat            # GPU support installer
├── chay_app.bat                # Start application
├── .env                        # Your configuration
├── .env.example                # Configuration template
├── autodub/                    # Core pipeline
│   ├── speech/                 # ASR engines
│   ├── text/                   # Translation modules
│   ├── media/                  # Audio/video processing
│   └── config.py               # Settings management
├── scripts/                    # Setup scripts
│   ├── setup_whisper.py
│   ├── setup_vieneu.py
│   └── setup_paraformer.py
├── .venv-whisper/             # Whisper virtual env
├── .venv-vieneu/              # VieNeu virtual env
├── .venv-gpu/                 # GPU support virtual env
└── output/                    # Processed videos
```

---

## Performance Benchmarks

### CPU Only (Intel i7-10700, 16GB RAM)
- Whisper ASR: ~15 min for 30 min video
- Demucs separation: ~20 min
- TTS: ~10 min (3 workers)
- **Total: ~50 min for 30 min video**

### With GPU (NVIDIA RTX 3060, 12GB VRAM)
- Whisper ASR: ~2 min for 30 min video (7.5x faster)
- Demucs separation: ~2 min (10x faster)
- TTS: ~10 min (CPU-only, unchanged)
- **Total: ~15 min for 30 min video (3.3x faster)**

---

## Support

- **Issues:** https://github.com/ttthanh2044/voxdub/issues
- **Documentation:** See `.claude/` folder for technical docs
- **Updates:** Check GitHub releases for new versions

---

## License

Open source - see LICENSE file for details.
