# VoxDub Studio - Configuration Reference

Complete reference for all configuration options in `.env` file.

## Translation Provider

### Provider Selection

```env
TRANSLATE_PROVIDER=voxdub  # voxdub | gemini | openrouter
```

Choose your translation backend:
- `voxdub`: Centralized backend with optimized prompts (requires deployment)
- `gemini`: Direct Google Gemini API integration
- `openrouter`: Multi-model API gateway

### VoxDub Cloud Configuration

```env
VOXDUB_API_URL=http://your-backend-url:3001
```

Backend URL for VoxDub Cloud translation service. Leave empty to use manual translation via `TRANSLATE_PENDING.txt`.

**Features (VoxDub backend only):**
- Automatic video analysis for context extraction
- Review pass for quality assurance
- Idempotent job IDs prevent double-charging on retry
- Server-side API key management

### Gemini Direct Configuration

```env
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-2.0-flash-exp
```

- **GEMINI_API_KEY**: Get free API key at https://aistudio.google.com/apikey
- **GEMINI_MODEL**: Model to use (default: `gemini-2.0-flash-exp`)

**Rate Limits:**
- Free tier: 15 RPM
- Paid tier: 1000 RPM

### OpenRouter Configuration

```env
OPENROUTER_API_KEY=your_api_key_here
OPENROUTER_MODEL=google/gemini-2.0-flash-exp:free
```

- **OPENROUTER_API_KEY**: Get API key at https://openrouter.ai/keys
- **OPENROUTER_MODEL**: Model identifier from OpenRouter catalog

**Popular Models:**
- `google/gemini-2.0-flash-exp:free` (recommended, free)
- `anthropic/claude-3.5-sonnet` (paid, high quality)
- `openai/gpt-4` (paid, high quality)

### Translation Settings (All Providers)

```env
TRANSLATE_ENABLED=true
TRANSLATE_BATCH_SIZE=40
```

- **TRANSLATE_ENABLED**: Enable/disable automatic translation
- **TRANSLATE_BATCH_SIZE**: Segments per API request (1-100)
  - Smaller batches = better context adherence
  - Larger batches = faster processing

### Advanced Translation (VoxDub Backend Only)

```env
TRANSLATE_ANALYSIS=true
TRANSLATE_REVIEW=true
```

- **TRANSLATE_ANALYSIS**: Pre-translation analysis pass (extracts video context, terminology, pronouns)
- **TRANSLATE_REVIEW**: Post-translation review pass (re-translates questionable segments)

Both disabled automatically for Gemini/OpenRouter to reduce API costs.

---

## ASR (Speech Recognition)

### Engine Selection

```env
ASR_ENGINE=whisper  # whisper | paraformer
```

- `whisper`: All languages, GPU/CPU, multiple models
- `paraformer`: Chinese only, CPU only, higher accuracy

### Whisper Configuration

```env
WHISPER_MODEL=auto
WHISPER_BEAM_SIZE=5
DEFAULT_SOURCE_LANG=zh-CN
```

- **WHISPER_MODEL**: Model size
  - `auto`: large-v3 on GPU, medium on CPU (recommended)
  - `tiny`: Fastest, lowest accuracy
  - `base`: Fast, low accuracy
  - `small`: Faster, good accuracy
  - `medium`: Balanced
  - `large-v3`: Best accuracy, slow
- **WHISPER_BEAM_SIZE**: Beam search width (1-10, default 5)
  - Lower = faster, less accurate
  - Higher = slower, more accurate
  - Set to 1 on CPU-only systems for 2-3x speed boost
- **DEFAULT_SOURCE_LANG**: Source language code (zh-CN, en-US, ja-JP, ko-KR)

**Language auto-detection is disabled** — user must select source language explicitly.

### Paraformer Configuration

```env
ASR_ENGINE=paraformer
DEFAULT_SOURCE_LANG=zh-CN
```

Paraformer only supports Chinese (zh-CN). Install with:
```bash
py scripts\setup_paraformer.py
```

No GPU acceleration (CPU-only ONNX inference).

---

## Quality Presets

### Preset Selection

```env
QUALITY_PRESET=balanced  # fast | balanced | quality
```

Single setting that controls multiple parameters:

| Setting | fast | balanced | quality |
|---------|------|----------|---------|
| Whisper model | medium | auto | large-v3 |
| Background audio | 16kHz mono | 44.1kHz stereo | 44.1kHz stereo |
| Translation passes | main only | analysis + main + review | analysis + main + review |
| Karaoke alignment | estimated | Whisper | Whisper |

Individual settings below **override** the preset.

---

## TTS (Text-to-Speech)

### VieNeu Configuration

```env
VIENEU_VOICE=Phạm Tuyên
VIENEU_STYLE=tu_nhien
VIENEU_MAX_WORKERS=
```

- **VIENEU_VOICE**: Voice name (see Settings → Audio tab for full list)
- **VIENEU_STYLE**: Speaking style
  - `tu_nhien`: Natural (default)
  - `tin_tuc`: News broadcast
  - `doc_truyen`: Storytelling
- **VIENEU_MAX_WORKERS**: Parallel TTS workers (empty = auto-detect)
  - Each worker uses ~1.5 GB RAM
  - Default: `min(6, cpu_cores)`

Install VieNeu with:
```bash
py scripts\setup_vieneu.py
```

---

## Translation Context (Optional)

Help translation AI understand video content for better consistency:

```env
TRANSLATE_DOMAIN=
TRANSLATE_CONTEXT=
TRANSLATE_PRONOUNS=
TRANSLATE_GLOSSARY=
TRANSLATE_STYLE_NOTES=
```

- **TRANSLATE_DOMAIN**: Video category (e.g., "tech review", "cooking vlog", "historical drama")
- **TRANSLATE_CONTEXT**: Channel/video description (use `\n` for multiple lines)
- **TRANSLATE_PRONOUNS**: Address forms (e.g., "mình – các bạn", "tôi – anh em")
- **TRANSLATE_GLOSSARY**: Fixed term translations, one per line (use `\n`):
  ```
  AI = trí tuệ nhân tạo\nGPU = card đồ họa\nRAM = bộ nhớ RAM
  ```
- **TRANSLATE_STYLE_NOTES**: Tone/style requirements (e.g., "formal", "casual", "technical")

---

## Timing & Speed

### Video Speed

```env
VIDEO_SPEED=1.0
VOICE_SPEED=1.0
```

- **VIDEO_SPEED**: Stretch entire video (0.82 = 22% longer, gives Vietnamese more time)
- **VOICE_SPEED**: TTS speed multiplier (1.2 = 20% faster speech)

**Recommendation:** Keep VIDEO_SPEED=1.0, adjust VOICE_SPEED if timing is tight.

### Translation Budget

```env
TRANSLATE_CPS_BUDGET=12.5
```

Characters per second budget for translation. Lower = shorter translations.
- 12.5: Default, balanced
- 10.0: Aggressive compression
- 15.0: More verbose

### Soft Timing Fit

```env
SOFT_TIMING_FIT=true
TIMING_MAX_DRIFT_S=1.5
TIMING_MIN_GAP_S=0.12
TIMING_MAX_ATEMPO=1.1
```

- **SOFT_TIMING_FIT**: Enable intelligent timing adjustment
- **TIMING_MAX_DRIFT_S**: Max delay allowed between segments
- **TIMING_MIN_GAP_S**: Minimum silence between segments
- **TIMING_MAX_ATEMPO**: Max speed-up ratio (1.1 = 10% faster)

**How it works:** When translation overruns, delay next segment into silence gaps. Only speed up audio if no other option.

---

## Audio Quality

### Background Audio

```env
HQ_BACKGROUND=true
```

- `true`: 44.1kHz stereo (recommended)
- `false`: 16kHz mono (faster, smaller files)

### Voice Postprocessing

```env
VOICE_POSTPROCESS=true
VOICE_TARGET_LUFS=-16.0
BG_DUCK_VOICE_DB=-7.0
```

- **VOICE_POSTPROCESS**: Normalize volume and fade each segment
- **VOICE_TARGET_LUFS**: Target loudness (lower = louder, -16.0 = standard)
- **BG_DUCK_VOICE_DB**: Background music reduction when voice plays
  - -7.0: 7dB quieter (recommended)
  - 0: No ducking

---

## Subtitles

### Mode Selection

```env
SUBTITLE_MODE=none  # none | soft | burn
```

- `none`: No subtitles
- `soft`: External .srt file (can toggle on/off in player)
- `burn`: Embedded in video (permanent)

### Preset Styles

```env
SUBTITLE_PRESET=clean  # clean | bold_yellow | box | tiktok | karaoke | cinema | custom
```

Built-in styles:
- `clean`: Simple white text with black outline
- `bold_yellow`: Bold yellow text
- `box`: Background box (CapCut style)
- `tiktok`: Large text with thick outline
- `karaoke`: Highlighted words with effects
- `cinema`: Classic bottom-center style
- `custom`: Use custom settings below

### Custom Subtitle Settings

```env
SUBTITLE_POSITION=bottom
SUBTITLE_FONT=Arial
SUBTITLE_FONT_SIZE=22
SUBTITLE_BOLD=true
SUBTITLE_MARGIN_V=40
SUBTITLE_OUTLINE=2
SUBTITLE_SHADOW=0
SUBTITLE_COLOR=#FFFFFF
SUBTITLE_OUTLINE_COLOR=#000000
```

- **SUBTITLE_POSITION**: `top` | `center` | `bottom`
- **SUBTITLE_FONT**: Font name (must be installed on system)
- **SUBTITLE_FONT_SIZE**: Point size
- **SUBTITLE_BOLD**: Bold text
- **SUBTITLE_MARGIN_V**: Vertical margin from edge (pixels)
- **SUBTITLE_OUTLINE**: Outline width (pixels)
- **SUBTITLE_SHADOW**: Shadow offset (pixels)
- **SUBTITLE_COLOR**: Text color (hex)
- **SUBTITLE_OUTLINE_COLOR**: Outline color (hex)

### Background Box

```env
SUBTITLE_BOX=none  # none | box
SUBTITLE_BOX_COLOR=#000000
SUBTITLE_BOX_OPACITY=60
```

- **SUBTITLE_BOX**: Add background box behind text
- **SUBTITLE_BOX_COLOR**: Box color (hex)
- **SUBTITLE_BOX_OPACITY**: Transparency (0-100, 100 = opaque)

### Line Breaking

```env
SUBTITLE_LINE_WORDS=0
SUBTITLE_MAX_LINES=2
SUBTITLE_ALL_CAPS=false
```

- **SUBTITLE_LINE_WORDS**: Words per line (0 = auto, 4-6 for vertical video)
- **SUBTITLE_MAX_LINES**: Maximum lines per subtitle
- **SUBTITLE_ALL_CAPS**: Force uppercase text

### Karaoke Effects

```env
SUBTITLE_DISPLAY=sentence  # sentence | karaoke
KARAOKE_WORDS_PER_CUE=3
KARAOKE_EFFECT=pop
KARAOKE_HIGHLIGHT_COLOR=#FFD54A
KARAOKE_ALIGNMENT=true
```

- **SUBTITLE_DISPLAY**: Display mode
  - `sentence`: Show entire sentence at once
  - `karaoke`: Show words progressively
- **KARAOKE_WORDS_PER_CUE**: Words per segment (3 recommended)
- **KARAOKE_EFFECT**: Animation effect
  - `pop`: Scale up effect
  - `fade`: Fade in effect
  - `karaoke`: Color change highlight
  - `none`: No animation
- **KARAOKE_HIGHLIGHT_COLOR**: Active word color (hex)
- **KARAOKE_ALIGNMENT**: Use Whisper to re-align word timing
  - `true`: Accurate timing (30-60s extra per video)
  - `false`: Estimated timing (faster)

---

## Content Generation

### Metadata Generation

```env
GENERATE_METADATA=true
```

Auto-generate YouTube/TikTok/Facebook metadata after dubbing:
- Title
- Description
- Hashtags

Requires VoxDub backend. Automatically skipped if backend not configured.

---

## System Settings

### Parallelization

```env
PARALLEL_WORKERS=
```

Concurrent workers for heavy tasks (empty = auto-detect based on CPU cores).

### Output Directory

```env
OUTPUT_DIR=./output
```

Where processed videos are saved.

### Display Name

```env
DISPLAY_NAME=
```

Name shown in web UI greeting (empty = use system username).

### Cleanup

```env
AUTO_CLEAN_INTERMEDIATES=false
```

Delete intermediate files after export:
- `true`: Save disk space, can't re-export or edit
- `false`: Keep all files for editing

---

## Updates & Support

```env
UPDATE_REPO=ttthanh2044/voxdub
SUPPORT_URL=https://github.com/ttthanh2044/voxdub/issues
```

GitHub repository for update checks and issue reporting.

---

## Example Configurations

### Fast Preview (CPU Only)

```env
QUALITY_PRESET=fast
WHISPER_MODEL=medium
WHISPER_BEAM_SIZE=1
TRANSLATE_ANALYSIS=false
TRANSLATE_REVIEW=false
HQ_BACKGROUND=false
KARAOKE_ALIGNMENT=false
VIENEU_MAX_WORKERS=2
```

### Production Quality (With GPU)

```env
QUALITY_PRESET=quality
WHISPER_MODEL=large-v3
WHISPER_BEAM_SIZE=5
TRANSLATE_ANALYSIS=true
TRANSLATE_REVIEW=true
HQ_BACKGROUND=true
KARAOKE_ALIGNMENT=true
VIENEU_MAX_WORKERS=6
```

### Low RAM (8 GB)

```env
QUALITY_PRESET=fast
WHISPER_MODEL=medium
VIENEU_MAX_WORKERS=2
PARALLEL_WORKERS=2
HQ_BACKGROUND=false
```

### High RAM (32 GB+)

```env
QUALITY_PRESET=quality
WHISPER_MODEL=large-v3
VIENEU_MAX_WORKERS=6
PARALLEL_WORKERS=8
HQ_BACKGROUND=true
```

---

## Configuration Priority

Settings are loaded in this order (later overrides earlier):

1. `.env.example` defaults
2. `.env` user settings
3. Web UI Settings page
4. Per-project overrides (stored in project metadata)

**Recommendation:** Use `.env` for system-wide defaults, then adjust per-project in Settings UI.
