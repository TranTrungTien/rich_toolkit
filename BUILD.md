# VoxDub Studio - Hướng dẫn Build và Phát hành

## Yêu cầu để build

- Python 3.10+
- PyInstaller (`pip install pyinstaller`)
- Tất cả dependencies của ứng dụng đã cài (`pip install -r requirements.txt`)

## Cách build

### Tự động (Khuyên dùng)

```bash
build.bat
```

Script sẽ tự động:
1. Kiểm tra Python
2. Cài PyInstaller nếu chưa có
3. Chạy `build_release.py`
4. Tạo package ZIP đầy đủ

### Thủ công

```bash
python build_release.py
```

## Kết quả

Sau khi build thành công, bạn sẽ có:

```
dist/
├── VoxDubStudio/              # Thư mục chứa ứng dụng đã build
│   ├── VoxDubStudio.exe       # File thực thi chính
│   ├── setup.bat              # Script cài đặt dependencies
│   ├── first_run_wizard.bat   # Wizard cấu hình lần đầu
│   ├── cai_them_gpu.bat       # Cài GPU support
│   ├── chay_app.bat           # Khởi động ứng dụng
│   ├── .env.example           # Mẫu cấu hình
│   ├── README.md              # Hướng dẫn
│   ├── scripts/               # Scripts setup
│   ├── autodub/               # Source code pipeline
│   ├── autodub_gui/           # Source code GUI
│   ├── output/                # Thư mục lưu video (trống)
│   └── README_RELEASE.txt     # Hướng dẫn cài đặt nhanh
│
└── VoxDubStudio-v1.0.0.zip    # Package đầy đủ để phân phối
```

## Quy trình phát hành

### 1. Chuẩn bị

```bash
# Đảm bảo code clean, không có debug prints
# Kiểm tra version trong build_release.py

# Test ứng dụng hoạt động tốt
python autodub_gui/__main__.py
```

### 2. Build

```bash
build.bat
```

### 3. Kiểm tra package

```bash
# Giải nén ZIP
cd dist
unzip VoxDubStudio-v1.0.0.zip

# Test cài đặt
cd VoxDubStudio
setup.bat

# Test wizard
first_run_wizard.bat

# Test chạy
chay_app.bat
```

### 4. Upload lên GitHub Release

1. Tạo tag version:
   ```bash
   git tag -a v1.0.0 -m "VoxDub Studio v1.0.0 - Initial Release"
   git push origin v1.0.0
   ```

2. Tạo Release trên GitHub:
   - Vào https://github.com/ttthanh2044/voxdub/releases/new
   - Chọn tag `v1.0.0`
   - Title: `VoxDub Studio v1.0.0`
   - Description: Copy từ README.md phần "Tính năng"
   - Upload file `VoxDubStudio-v1.0.0.zip`
   - Click "Publish release"

## Cấu trúc build

### PyInstaller spec file

File `VoxDubStudio.spec` được tạo tự động bởi `build_release.py`:

- **Entry point**: `autodub_gui/__main__.py`
- **Hidden imports**: Các module cần import tường minh
- **Data files**: .env.example, README.md, tài liệu
- **Excludes**: Loại bỏ các module không dùng để giảm kích thước

### Các file được bundle

**Files riêng lẻ**:
- `setup.bat`, `first_run_wizard.bat`, `cai_them_gpu.bat`, `chay_app.bat`
- `.env.example`
- `README.md`, `INSTALLATION.md`, `CONFIGURATION.md`, `VERIFICATION_REPORT.md`
- `LICENSE`

**Thư mục**:
- `scripts/` - Setup scripts cho Whisper, VieNeu, Paraformer, GPU
- `autodub/` - Core pipeline source code
- `autodub_gui/` - GUI source code

**Lưu ý**: Virtual environments (`.venv-*`) KHÔNG được bundle. User phải chạy `setup.bat` để tạo chúng.

## Tối ưu kích thước

### Giảm kích thước EXE

1. **Exclude unused modules** - Thêm vào `excludes` trong spec:
   ```python
   excludes=[
       'matplotlib',
       'numpy.distutils',
       'pytest',
       'IPython',
       'jupyter',
       'tkinter',
   ]
   ```

2. **UPX compression** - Đã bật trong spec:
   ```python
   upx=True
   ```

3. **Strip symbols**:
   ```python
   strip=False  # Đổi thành True nếu muốn giảm thêm
   ```

### Giảm kích thước ZIP

- Không bundle `.pyc`, `__pycache__`
- Không bundle `.git*`, `*.egg-info`
- Thư mục `output/` chỉ giữ file `.gitkeep`

## Debug build issues

### Lỗi "ModuleNotFoundError" khi chạy EXE

Thêm module vào `hiddenimports` trong `build_release.py`:

```python
hiddenimports = [
    'module_name',
    'package.submodule',
]
```

### Lỗi "FileNotFoundError" cho data files

Thêm vào `datas` trong `build_release.py`:

```python
datas = [
    ('path/to/file', 'destination/folder'),
]
```

### EXE chạy chậm

- Đổi `console=True` để thấy output debug
- Check có module nào load lâu không
- Xem xét dùng `--onefile` (EXE đơn, nhưng khởi động chậm hơn)

### Build thất bại với UnicodeEncodeError

Đảm bảo script build chạy với UTF-8:

```python
# Thêm vào đầu file
# -*- coding: utf-8 -*-
```

Hoặc set encoding:
```bash
set PYTHONIOENCODING=utf-8
```

## Checklist trước khi phát hành

- [ ] Đã test ứng dụng hoạt động đầy đủ
- [ ] README.md đầy đủ hướng dẫn tiếng Việt
- [ ] Đã update VERSION trong `build_release.py`
- [ ] Đã test build trên máy sạch (chưa có .venv)
- [ ] Đã test setup.bat hoạt động
- [ ] Đã test first_run_wizard.bat
- [ ] Đã test với cả 3 translation providers (VoxDub/Gemini/OpenRouter)
- [ ] Đã test với GPU và CPU-only
- [ ] Đã test với Whisper và Paraformer
- [ ] File LICENSE có đầy đủ
- [ ] VERIFICATION_REPORT.md đã updated
- [ ] Git tag đã tạo và push
- [ ] GitHub release đã tạo với ZIP attachment

## Hỗ trợ

Nếu gặp vấn đề khi build, tạo issue tại:
https://github.com/ttthanh2044/voxdub/issues
