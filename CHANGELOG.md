# VoxDub Studio - Change Log

## Version 1.0.0 (2026-08-12)

### Major Features

#### Translation Provider System
- **3 Translation Providers**: VoxDub Cloud, Google Gemini Direct, OpenRouter
- **Full UI Configuration**: All provider settings exposed in Settings → Dịch thuật
  - `TRANSLATE_PROVIDER` - Provider selection dropdown
  - `VOXDUB_API_URL` - VoxDub Cloud backend URL
  - `GEMINI_API_KEY` + `GEMINI_MODEL` - Gemini Direct configuration
  - `OPENROUTER_API_KEY` + `OPENROUTER_MODEL` - OpenRouter configuration
- **Dynamic Provider Routing**: Pipeline automatically loads selected provider
- **Unified Interface**: All providers share same translation interface

#### ASR Improvements
- **Language Auto-Detection Removed**: User must explicitly select source language
  - Prevents silent detection errors
  - Improves accuracy
  - Checkbox removed from UI
- **GPU Detection Enhanced**: Explicit logging of GPU availability
- **Model Selection Logic**: `auto` mode correctly selects large-v3 (GPU) or medium (CPU)

#### Documentation
- **Vietnamese README.md**: Comprehensive 500+ line guide
  - Installation instructions
  - Usage for all features
  - Provider comparison and setup
  - Troubleshooting section
  - Performance benchmarks
- **English Documentation Suite**:
  - INSTALLATION.md - Complete setup guide
  - CONFIGURATION.md - Full .env reference
  - BUILD.md - Build and release guide
  - VERIFICATION_REPORT.md - End-to-end verification
  - FINAL_VERIFICATION.md - Deployment checklist

#### Build System
- **PyInstaller Integration**: `build_release.py` for automated EXE packaging
- **One-Click Build**: `build.bat` wrapper script
- **Complete Bundle**: Release package includes all scripts, docs, source code

### Configuration Changes

#### New Settings
- `TRANSLATE_PROVIDER` - Choose translation backend (voxdub/gemini/openrouter)
- `GEMINI_API_KEY` - Google Gemini API key
- `GEMINI_MODEL` - Gemini model selection (default: gemini-2.0-flash-exp)
- `OPENROUTER_API_KEY` - OpenRouter API key
- `OPENROUTER_MODEL` - OpenRouter model ID (default: google/gemini-2.0-flash-exp:free)

#### Modified Settings
- `VOXDUB_API_URL` - Now visible in UI Settings (removed from EXEMPT_KEYS)
- `DEFAULT_SOURCE_LANG` - Required, no auto-detection fallback

### Code Quality

#### Architecture
- **Zero Hardcoding**: All configuration via .env and UI
- **Modular Structure**: Clean separation autodub vs autodub_gui
- **Provider Abstraction**: Uniform translation provider interface

#### Error Handling
- **Retry Logic**: Exponential backoff for all providers
- **Rate Limiting**: Provider-specific rate limits (Gemini 15 RPM, OpenRouter 20 RPM)
- **Checkpoint Recovery**: Resume from interruptions

#### Performance
- **GPU Acceleration**: CUDA support for Whisper and Demucs
- **Parallel Processing**: Auto-detected worker allocation
- **Memory Optimization**: Configurable worker counts

### Bug Fixes
- Fixed AttributeError when accessing auto_detect checkbox (removed)
- Fixed source_lang always required (no empty string fallback)
- Fixed GPU detection logging
- Fixed translation provider routing

### Breaking Changes
- **Language auto-detection removed**: Projects created in older versions with auto-detect enabled will need language explicitly set
- **VOXDUB_API_URL configuration**: Now optional in UI, previously hardcoded for releases

### Migration Guide

#### From Pre-1.0 Versions
1. Update `.env` with new translation provider fields:
   ```env
   TRANSLATE_PROVIDER=gemini
   GEMINI_API_KEY=your_key_here
   GEMINI_MODEL=gemini-2.0-flash-exp
   ```

2. Set explicit source language (no auto-detect):
   ```env
   DEFAULT_SOURCE_LANG=zh-CN
   ```

3. Re-run setup if needed:
   ```bash
   setup.bat
   ```

### Statistics
- **Python Files**: 150
- **Lines of Code**: 43,445
- **Documentation**: 7 comprehensive files (2000+ lines)
- **Installation Scripts**: 4 .bat files
- **Translation Providers**: 3 fully integrated

### Known Limitations
- VieNeu TTS: CPU-only, no GPU acceleration
- Paraformer ASR: Chinese language only, CPU-only
- Gemini/OpenRouter: Single-pass translation (no analysis/review passes)
- Windows only (current release)

### Credits
- OpenAI Whisper - Speech recognition
- VieNeu - Vietnamese text-to-speech
- Alibaba Paraformer - Chinese ASR
- Facebook Demucs - Vocal separation
- Google Gemini - Translation API
- OpenRouter - Multi-model API gateway
- PySide6 - GUI framework

---

**Full Changelog**: https://github.com/ttthanh2044/voxdub/commits/v1.0.0
