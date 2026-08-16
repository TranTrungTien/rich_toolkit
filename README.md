# VoxDub Studio

**Hệ thống dịch và lồng tiếng video tự động hoàn toàn** — dịch video từ tiếng Trung/Anh/Nhật/Hàn sang tiếng Việt bằng AI nhận dạng giọng nói, dịch thuật và tổng hợp giọng đọc.

## Tính năng

- **Nhận dạng giọng nói đa ngôn ngữ**: Whisper (mọi ngôn ngữ) hoặc Paraformer (tiếng Trung, độ chính xác cao hơn)
- **Tăng tốc GPU**: Xử lý nhanh hơn 10 lần với NVIDIA CUDA
- **Dịch thuật linh hoạt**: Chọn giữa VoxDub Cloud, Google Gemini, hoặc OpenRouter
- **Giọng đọc tiếng Việt chất lượng cao**: Công nghệ tổng hợp giọng VieNeu
- **Căn thời gian thông minh**: Tự động điều chỉnh thời điểm lời thoại với nén mềm và phát hiện khoảng lặng
- **Phụ đề karaoke**: Tô sáng từng chữ theo thời gian với hiệu ứng bật lên/mờ dần
- **Nhạc nền**: Tách giọng nói thông minh với Demucs
- **Giao diện web**: Quản lý dự án dễ dàng với giao diện Streamlit

## Cài đặt nhanh

### 1. Yêu cầu hệ thống

- **Python 3.10 trở lên** - Tải tại https://www.python.org/downloads/
  - ✅ Nhớ tích "Add Python to PATH" khi cài đặt
- **ffmpeg** - Tải tại https://www.gyan.dev/ffmpeg/builds/
  - Giải nén và thêm thư mục `bin` vào biến môi trường PATH của Windows
- **Windows 10/11**
- **Tùy chọn**: Card đồ họa NVIDIA với CUDA (tăng tốc 3-10 lần)

### 2. Cài đặt ứng dụng

```bash
# Tải mã nguồn về
git clone https://github.com/ttthanh2044/voxdub.git
cd voxdub

# Chạy script cài đặt tự động
setup.bat
```

Script `setup.bat` sẽ tự động:
- Kiểm tra Python 3.10+ đã cài
- Kiểm tra ffmpeg có trong PATH
- Cài đặt các thư viện cần thiết
- Tạo file cấu hình `.env` từ mẫu `.env.example`
- Cài đặt Whisper ASR (nhận dạng giọng nói)
- Cài đặt VieNeu TTS (tổng hợp giọng tiếng Việt)
- Hỏi có muốn cài thêm hỗ trợ GPU không

**An toàn chạy lại**: Script có thể chạy nhiều lần, sẽ tự động bỏ qua các bước đã hoàn thành.

### 3. Cấu hình lần đầu

```bash
first_run_wizard.bat
```

Trình hướng dẫn tương tác sẽ giúp bạn:
1. **Chọn nhà cung cấp dịch thuật**:
   - **VoxDub Cloud**: Chất lượng tốt nhất (cần triển khai máy chủ backend riêng)
   - **Google Gemini Direct**: Miễn phí 15 lượt/phút, chất lượng tốt, dễ setup
   - **OpenRouter**: Truy cập nhiều mô hình AI, trả theo lượng dùng
2. **Nhập API key** cho dịch vụ bạn chọn
3. **Chọn engine nhận dạng giọng nói**: Whisper (đa ngôn ngữ) hoặc Paraformer (chỉ tiếng Trung, chính xác hơn)
4. **Chọn mức chất lượng**: Nhanh / Cân bằng / Chất lượng cao

### 4. Tăng tốc GPU (Tùy chọn nhưng rất khuyên dùng)

Nếu máy bạn có card NVIDIA:

```bash
cai_them_gpu.bat
```

Script sẽ:
- Tạo môi trường ảo `.venv-gpu`
- Cài PyTorch với CUDA 12.4
- Cài Demucs để tách giọng nói (dùng GPU)
- Kiểm tra GPU có hoạt động không

**Hiệu suất**: GPU giúp xử lý nhanh hơn **3-10 lần** so với CPU thuần.

### 5. Chạy ứng dụng

```bash
chay_app.bat
```

Ứng dụng sẽ mở tại `http://localhost:8501`

## Hướng dẫn sử dụng

### Quy trình cơ bản

1. **Tạo dự án mới**
   - Nhập URL video YouTube hoặc upload file video từ máy
   - Chọn ngôn ngữ gốc (tiếng Trung, Anh, Nhật, Hàn)
   - Chọn giọng đọc tiếng Việt
   - Chọn mức chất lượng

2. **Xử lý tự động**

   Pipeline sẽ tự động thực hiện các bước:
   - ✅ Tải video và tách âm thanh
   - ✅ Tách giọng nói khỏi nhạc nền (Demucs)
   - ✅ Nhận dạng lời thoại bằng ASR (Whisper/Paraformer)
   - ✅ Dịch sang tiếng Việt (Gemini/OpenRouter/VoxDub)
   - ✅ Tổng hợp giọng đọc tiếng Việt (VieNeu)
   - ✅ Căn chỉnh thời gian và trộn âm thanh
   - ✅ Xuất video hoàn chỉnh

3. **Xem lại và chỉnh sửa**
   - Phát video kết quả
   - Sửa bản dịch nếu cần (chỉnh từng câu)
   - Điều chỉnh tốc độ giọng đọc, tốc độ video
   - Tùy chỉnh phụ đề (vị trí, màu sắc, font chữ, hiệu ứng karaoke)

4. **Xuất video cuối cùng**
   - Tải về file video đã lồng tiếng
   - File metadata cho YouTube/TikTok/Facebook (nếu bật)

### Tính năng nâng cao

#### Dịch thủ công
Nếu muốn tự dịch hoặc dùng ChatGPT/Gemini:
1. Tắt "Bật dịch tự động" trong Settings → Dịch thuật
2. Khi chạy pipeline, ứng dụng sẽ dừng ở bước dịch
3. Mở file `TRANSLATE_PENDING.txt` trong thư mục dự án
4. Copy nội dung, dán vào ChatGPT/Gemini với prompt dịch của bạn
5. Copy bản dịch về, paste vào ứng dụng
6. Pipeline tự động tiếp tục các bước còn lại

#### Phụ đề
Ba chế độ phụ đề:
- **Không phụ đề**: Chỉ lồng tiếng, không có chữ
- **Phụ đề mềm**: File .srt riêng, bật/tắt được trong trình phát
- **Phụ đề cháy**: Chữ nhúng cố định vào video

**Các bộ kiểu có sẵn**:
- `clean`: Chữ trắng viền đen đơn giản
- `bold_yellow`: Chữ vàng đậm nổi bật
- `box`: Nền mờ sau chữ (kiểu CapCut)
- `tiktok`: Chữ to viền dày (dành cho video ngắn)
- `karaoke`: Tô sáng từng chữ theo lời đọc
- `cinema`: Kiểu phụ đề phim cổ điển
- `custom`: Tự chỉnh từng thông số

#### Hiệu ứng karaoke
Khi chọn kiểu hiển thị "Hiện theo cụm chữ":
- **Hiệu ứng bật lên**: Chữ phóng to khi được đọc
- **Hiệu ứng mờ dần**: Chữ hiện dần từ mờ sang rõ
- **Đổi màu theo lời đọc**: Chữ đổi màu khi được đọc (karaoke thật)
- **Không hiệu ứng**: Chỉ hiện từng cụm, không có animation

**Canh chữ theo lời đọc**: Bật để Whisper căn chỉnh chính xác thời điểm từng chữ (chạy thêm 30-60 giây nhưng rất chính xác).

#### Thư viện giọng đọc
Nhiều giọng nam/nữ khác nhau:
- Giọng miền Bắc: Phạm Tuyên, Mai Phương, Thu Thảo
- Giọng miền Nam: Anh Tuấn, Huyền Trang
- Giọng trẻ: Minh Khánh, Lan Anh
- Mỗi giọng có nhiều phong cách: Tự nhiên, Tin tức, Kể chuyện

#### Điều chỉnh tốc độ
- **Tốc độ video**: Làm chậm toàn bộ video (0.82 = dài thêm 22%) để giọng Việt có đủ chỗ
- **Tốc độ giọng đọc**: Tăng tốc giọng đọc (1.2 = nhanh hơn 20%) khi câu Việt dài hơn câu gốc

**Khuyến nghị**: Giữ tốc độ video = 1.0, chỉ tăng tốc giọng đọc nếu cần.

## Cấu hình chi tiết

### Nhà cung cấp dịch thuật

#### 1. VoxDub Cloud (Khuyên dùng nếu có máy chủ)
```env
TRANSLATE_PROVIDER=voxdub
VOXDUB_API_URL=http://your-backend-url:3001
```

**Ưu điểm**:
- Prompt tối ưu với phân tích video tự động
- Có lượt rà soát chất lượng (review pass)
- Job ID không trùng lặp, tránh tính phí 2 lần khi thử lại
- Quản lý API key tập trung ở server

**Nhược điểm**: Cần triển khai backend riêng (không miễn phí)

#### 2. Google Gemini Direct (Khuyên dùng cho cá nhân)
```env
TRANSLATE_PROVIDER=gemini
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-2.0-flash-exp
```

**Lấy API key miễn phí**: https://aistudio.google.com/apikey

**Giới hạn**:
- Miễn phí: 15 lượt/phút
- Trả phí: 1000 lượt/phút

**Ưu điểm**:
- Hoàn toàn miễn phí (đủ cho hầu hết nhu cầu cá nhân)
- Không cần backend
- Chất lượng dịch tốt
- Setup đơn giản

**Nhược điểm**: Không có lượt phân tích/rà soát như VoxDub

#### 3. OpenRouter
```env
TRANSLATE_PROVIDER=openrouter
OPENROUTER_API_KEY=your_api_key_here
OPENROUTER_MODEL=google/gemini-2.0-flash-exp:free
```

**Lấy API key**: https://openrouter.ai/keys

**Các model phổ biến**:
- `google/gemini-2.0-flash-exp:free` - Miễn phí, khuyên dùng
- `anthropic/claude-3.5-sonnet` - Trả phí, chất lượng rất cao
- `openai/gpt-4` - Trả phí, chất lượng cao

**Ưu điểm**:
- Truy cập nhiều mô hình AI khác nhau
- Linh hoạt về giá
- Có model miễn phí

### Engine nhận dạng giọng nói (ASR)

#### Whisper (Đa ngôn ngữ)
```env
ASR_ENGINE=whisper
WHISPER_MODEL=auto
DEFAULT_SOURCE_LANG=zh-CN
```

**WHISPER_MODEL**:
- `auto`: Tự chọn large-v3 nếu có GPU, medium nếu CPU (khuyên dùng)
- `tiny`: Nhanh nhất, độ chính xác thấp nhất
- `base`: Nhanh, độ chính xác thấp
- `small`: Nhanh hơn, độ chính xác tốt
- `medium`: Cân bằng
- `large-v3`: Chính xác nhất, chậm nhất

**Ngôn ngữ hỗ trợ**: Trung, Anh, Nhật, Hàn, và 90+ ngôn ngữ khác

**Lưu ý**: Tự động nhận dạng ngôn ngữ đã bị vô hiệu hóa. Bạn PHẢI chọn ngôn ngữ gốc rõ ràng để đảm bảo độ chính xác.

#### Paraformer (Chỉ tiếng Trung, độ chính xác cao hơn)
```env
ASR_ENGINE=paraformer
DEFAULT_SOURCE_LANG=zh-CN
```

Cài đặt:
```bash
py scripts\setup_paraformer.py
```

**Ưu điểm**: Chính xác hơn Whisper với video tiếng Trung
**Nhược điểm**:
- Chỉ hỗ trợ tiếng Trung
- Không có GPU, chỉ chạy trên CPU

### Mức chất lượng (Presets)

```env
QUALITY_PRESET=balanced  # fast | balanced | quality
```

| Cài đặt | Nhanh | Cân bằng | Chất lượng cao |
|---------|-------|----------|----------------|
| Model Whisper | medium | auto | large-v3 |
| Nhạc nền | 16kHz mono | 44.1kHz stereo | 44.1kHz stereo |
| Số lượt dịch | chỉ dịch | phân tích + dịch + rà soát | phân tích + dịch + rà soát |
| Canh chữ karaoke | ước lượng | Whisper | Whisper |

**Lưu ý**: Các cài đặt riêng lẻ bên dưới sẽ ghi đè preset.

### Ngữ cảnh video (Tùy chọn nhưng giúp dịch tốt hơn)

```env
TRANSLATE_DOMAIN=review công nghệ
TRANSLATE_CONTEXT=Kênh đập hộp linh kiện máy tính giá rẻ, người xem là dân tự lắp máy.
TRANSLATE_PRONOUNS=mình – các bạn
TRANSLATE_GLOSSARY=显卡 = card đồ họa\n翻车 = toang\nCPU = CPU
TRANSLATE_STYLE_NOTES=giọng hài hước, giữ thuật ngữ tiếng Anh
```

Các thông tin này giúp AI hiểu video của bạn để:
- Xưng hô nhất quán từ đầu đến cuối
- Dịch thuật ngữ chuyên ngành đúng ngữ cảnh
- Giữ phong cách phù hợp với khán giả mục tiêu

### Các cài đặt khác

Xem file `CONFIGURATION.md` để biết danh sách đầy đủ tất cả các tùy chọn cấu hình.

## Hiệu suất

### Chỉ CPU (Intel i7-10700, 16GB RAM)
- Nhận dạng Whisper: ~15 phút cho video 30 phút
- Tách giọng Demucs: ~20 phút
- Tổng hợp VieNeu: ~10 phút (3 workers)
- **Tổng cộng**: ~50 phút cho video 30 phút

### Với GPU (NVIDIA GTX 1060 6GB)
- Nhận dạng Whisper: ~2 phút cho video 30 phút (**nhanh hơn 7.5 lần**)
- Tách giọng Demucs: ~2 phút (**nhanh hơn 10 lần**)
- Tổng hợp VieNeu: ~10 phút (CPU-only, không đổi)
- **Tổng cộng**: ~15 phút cho video 30 phút (**nhanh hơn 3.3 lần**)

### Với GPU cao cấp (NVIDIA RTX 3060 12GB)
- **Tổng cộng**: ~10-12 phút cho video 30 phút (**nhanh hơn 4-5 lần**)

**Khuyến nghị**: Nếu có card NVIDIA, nhất định chạy `cai_them_gpu.bat` để tận dụng GPU.

## Cấu trúc dự án

```
voxdub/
├── autodub/              # Pipeline chính
│   ├── speech/           # Engine ASR (Whisper, Paraformer)
│   ├── text/             # Module dịch thuật
│   │   ├── translate_gemini.py       # Gemini Direct
│   │   ├── translate_openrouter.py   # OpenRouter
│   │   └── translate_voxdub.py       # VoxDub Cloud
│   ├── voice/            # Engine TTS (VieNeu)
│   ├── media/            # Xử lý âm thanh/video
│   ├── config.py         # Quản lý cấu hình
│   └── pipeline.py       # Luồng xử lý chính
├── autodub_gui/          # Giao diện PySide6
│   ├── pages/            # Các trang UI
│   └── widgets/          # Widgets tùy chỉnh
├── scripts/              # Scripts setup và tiện ích
│   ├── setup_whisper.py
│   ├── setup_vieneu.py
│   ├── setup_paraformer.py
│   └── setup_gpu.py
├── output/               # Video đã xử lý
├── .env                  # Cấu hình người dùng
├── .env.example          # Mẫu cấu hình
├── setup.bat             # Cài đặt tự động
├── first_run_wizard.bat  # Hướng dẫn cấu hình
├── cai_them_gpu.bat      # Cài GPU support
└── chay_app.bat          # Chạy ứng dụng
```

## Xử lý sự cố

### Python không tìm thấy
1. Tải Python 3.10+ từ https://www.python.org/downloads/
2. **Quan trọng**: Tích "Add Python to PATH" khi cài đặt
3. Khởi động lại Command Prompt
4. Kiểm tra: `python --version` hoặc `py --version`

### ffmpeg không tìm thấy
1. Tải ffmpeg từ https://www.gyan.dev/ffmpeg/builds/ (chọn "release full")
2. Giải nén ra thư mục như `C:\ffmpeg`
3. Thêm `C:\ffmpeg\bin` vào biến môi trường PATH:
   - Mở Settings → System → About → Advanced system settings
   - Environment Variables → Path → Edit → New
   - Paste đường dẫn `C:\ffmpeg\bin`
   - OK → OK → OK
4. Khởi động lại Command Prompt
5. Kiểm tra: `ffmpeg -version`

### GPU không được phát hiện
1. Cài driver NVIDIA mới nhất: https://www.nvidia.com/download/
2. Chạy `cai_them_gpu.bat`
3. Kiểm tra:
   ```bash
   .venv-gpu\Scripts\python -c "import torch; print(torch.cuda.is_available())"
   ```
4. Nếu vẫn báo `False`:
   - Kiểm tra card có hỗ trợ CUDA không (GTX 900 trở lên, RTX series)
   - Cài lại driver NVIDIA
   - Cài CUDA Toolkit 12.4: https://developer.nvidia.com/cuda-downloads

### Lỗi "ModuleNotFoundError"
```bash
# Cài lại dependencies
pip install -r requirements.txt

# Hoặc chạy lại setup
setup.bat
```

### Lỗi "Out of memory" (Hết RAM)
Giảm số workers trong `.env`:
```env
PARALLEL_WORKERS=2
VIENEU_MAX_WORKERS=2
HQ_BACKGROUND=false
```

### Video bị lag hoặc giọng không khớp
1. Tăng `TIMING_MAX_DRIFT_S` trong `.env` (cho phép lệch nhiều hơn)
2. Giảm `VOICE_SPEED` (giọng đọc chậm lại)
3. Hoặc giảm `VIDEO_SPEED` (video chậm lại để giọng Việt có chỗ)

### Bản dịch không tốt
1. Điền đầy đủ ngữ cảnh video ở Settings → Dịch thuật:
   - Chủ đề video
   - Ngữ cảnh (kênh nói về gì, người xem là ai)
   - Cách xưng hô
   - Thuật ngữ cố định
2. Thử model khác (nếu dùng OpenRouter)
3. Hoặc tắt dịch tự động, tự dịch bằng ChatGPT/Gemini

### API rate limit (quá giới hạn lượt gọi)
- **Gemini free tier**: 15 lượt/phút
- **OpenRouter**: Tùy model, thường 20 lượt/phút

Giảm `TRANSLATE_BATCH_SIZE` trong `.env` (dịch ít câu hơn mỗi lần gọi):
```env
TRANSLATE_BATCH_SIZE=20  # Thay vì 40
```

## Tài liệu bổ sung

- [INSTALLATION.md](INSTALLATION.md) - Hướng dẫn cài đặt chi tiết (tiếng Anh)
- [CONFIGURATION.md](CONFIGURATION.md) - Tham khảo đầy đủ các tùy chọn cấu hình
- [.env.example](.env.example) - Mẫu file cấu hình với giải thích từng dòng
- [VERIFICATION_REPORT.md](VERIFICATION_REPORT.md) - Báo cáo kiểm tra end-to-end

## Hỗ trợ

- **Báo lỗi**: https://github.com/ttthanh2044/voxdub/issues
- **Kiểm tra cập nhật**: Xem GitHub releases
- **Thảo luận**: GitHub Discussions

## Giấy phép

Mã nguồn mở - xem file LICENSE để biết chi tiết.

## Ghi công

- **Whisper**: Công nghệ nhận dạng giọng nói của OpenAI
- **VieNeu**: Công nghệ tổng hợp giọng tiếng Việt
- **Paraformer**: ASR của Alibaba DAMO Academy
- **Demucs**: Công nghệ tách giọng của Facebook Research
- **PySide6**: Framework giao diện đồ họa
- **Google Gemini**: API dịch thuật miễn phí
- **OpenRouter**: Cổng truy cập đa mô hình AI

---

**Phát triển bởi**: ttthanh2044
**Phiên bản**: 1.0.0
**Cập nhật lần cuối**: 2026-08-12


## Translation providers (Gemini / OpenRouter / DeepSeek)

Open **D?ch thu?t** in the sidebar, then choose a provider and enter its API key,
Base URL, model and temperature. API-key controls are password-masked and include
a show/hide button. Model fields accept custom values and are not hardcoded.

- Gemini default Base URL: `https://generativelanguage.googleapis.com/v1beta`
- OpenRouter default Base URL: `https://openrouter.ai/api/v1`
- DeepSeek default Base URL: `https://api.deepseek.com`

A direct-provider failure stops the translation stage with an actionable error;
it is never silently reported as a successful manual fallback.

## Windows helper files

- `install.bat` / `setup.bat`: install prerequisites and Python dependencies.
- `run.bat` / `chay_app.bat`: launch the application from any working directory.
- `update.bat`: fast-forward from Git and refresh dependencies.
- `uninstall.bat`: remove generated runtimes while preserving `output/`.

## Logs and diagnostics

Runtime logs are stored at `logs/voxdub.log` with 14-day rotation. Secrets are
not included. The application records the actual CUDA runtime result, GPU name,
ASR device, Demucs device and selected FFmpeg encoder instead of inferring GPU
status from a folder name.

## Verified architecture and execution flow

The desktop entry point is `autodub_gui.__main__` -> `autodub_gui.app.main`.
The UI starts `DubWorker`, which calls `DubPipeline.run`. The traced production
flow is: acquire local/remote input -> dual audio extraction -> background
separation -> selected ASR with explicit source language -> selected translation
provider -> VieNeu/CapCut TTS -> voice normalization and soft timing -> streamed
audio mix -> FFmpeg mux/subtitle render -> metadata/report export.

OCR is not part of the current execution flow. Source-caption removal is manual
blur-region rendering, not OCR.
