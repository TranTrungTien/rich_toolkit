"""Script đóng gói VoxDub Studio thành EXE phân phối.

Đóng gói ứng dụng thành file .exe standalone với PyInstaller, kèm theo
các script setup .bat, tài liệu, và cấu hình mẫu.

Cách sử dụng:
    python build_release.py

Kết quả:
    - dist/VoxDubStudio/VoxDubStudio.exe
    - dist/VoxDubStudio-v{version}.zip (package đầy đủ)
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

VERSION = "1.0.0"
APP_NAME = "VoxDubStudio"
DIST_DIR = Path("dist")
BUILD_DIR = Path("build")
RELEASE_DIR = DIST_DIR / APP_NAME
ARCHIVE_NAME = f"{APP_NAME}-v{VERSION}.zip"

# Files và folders cần copy vào package
BUNDLE_FILES = [
    "setup.bat",
    "first_run_wizard.bat",
    "cai_them_gpu.bat",
    "chay_app.bat",
    ".env.example",
    "README.md",
    "INSTALLATION.md",
    "CONFIGURATION.md",
    "VERIFICATION_REPORT.md",
    "LICENSE",
]

BUNDLE_DIRS = [
    "scripts",
    "autodub",
    "autodub_gui",
]


def check_dependencies() -> bool:
    """Kiểm tra các dependencies cần thiết để build."""
    print("🔍 Kiểm tra dependencies...")

    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")

    # Check PyInstaller
    try:
        import PyInstaller
        print(f"✅ PyInstaller {PyInstaller.__version__}")
    except ImportError:
        print("❌ PyInstaller chưa cài. Chạy: pip install pyinstaller")
        return False

    # Check ffmpeg
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            print("✅ ffmpeg")
        else:
            print("⚠️  ffmpeg không tìm thấy trong PATH")
    except FileNotFoundError:
        print("⚠️  ffmpeg không tìm thấy trong PATH")

    return True


def clean_build() -> None:
    """Dọn dẹp các thư mục build cũ."""
    print("\n🧹 Dọn dẹp build cũ...")

    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)
        print(f"  Đã xóa {BUILD_DIR}")

    if RELEASE_DIR.exists():
        shutil.rmtree(RELEASE_DIR)
        print(f"  Đã xóa {RELEASE_DIR}")

    # Xóa các file .spec cũ
    for spec_file in Path(".").glob("*.spec"):
        spec_file.unlink()
        print(f"  Đã xóa {spec_file}")


def create_spec_file() -> Path:
    """Tạo file .spec cho PyInstaller."""
    print("\n📝 Tạo file .spec...")

    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Danh sách các module ẩn cần import
hiddenimports = [
    'autodub',
    'autodub.speech',
    'autodub.text',
    'autodub.voice',
    'autodub.media',
    'autodub_gui',
    'autodub_gui.pages',
    'autodub_gui.widgets',
    'PySide6',
    'PySide6.QtCore',
    'PySide6.QtGui',
    'PySide6.QtWidgets',
    'requests',
    'google.generativeai',
    'openai',
    'yaml',
    'dotenv',
]

# Data files cần bundle
datas = [
    ('.env.example', '.'),
    ('README.md', '.'),
    ('INSTALLATION.md', '.'),
    ('CONFIGURATION.md', '.'),
]

a = Analysis(
    ['autodub_gui/__main__.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy.distutils',
        'pytest',
        'IPython',
        'jupyter',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='{APP_NAME}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # Console để thấy log, đổi False nếu muốn GUI thuần
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Thêm icon nếu có
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='{APP_NAME}',
)
'''

    spec_path = Path(f"{APP_NAME}.spec")
    spec_path.write_text(spec_content, encoding="utf-8")
    print(f"  Đã tạo {spec_path}")
    return spec_path


def build_exe(spec_file: Path) -> bool:
    """Chạy PyInstaller để build EXE."""
    print("\n🔨 Đang build EXE với PyInstaller...")
    print("  (Quá trình này có thể mất 5-10 phút)")

    cmd = [
        sys.executable,
        "-m", "PyInstaller",
        "--clean",
        "--noconfirm",
        str(spec_file),
    ]

    try:
        result = subprocess.run(cmd, check=True)
        if result.returncode == 0:
            print("✅ Build EXE thành công")
            return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Build thất bại: {e}")
        return False

    return False


def bundle_release() -> None:
    """Bundle các file cần thiết vào thư mục release."""
    print("\n📦 Đóng gói release...")

    if not RELEASE_DIR.exists():
        print(f"❌ Không tìm thấy {RELEASE_DIR}")
        return

    # Copy các file đơn lẻ
    for file_name in BUNDLE_FILES:
        src = Path(file_name)
        if src.exists():
            dst = RELEASE_DIR / file_name
            shutil.copy2(src, dst)
            print(f"  ✅ {file_name}")
        else:
            print(f"  ⚠️  Bỏ qua {file_name} (không tồn tại)")

    # Copy các thư mục
    for dir_name in BUNDLE_DIRS:
        src = Path(dir_name)
        if src.exists():
            dst = RELEASE_DIR / dir_name
            shutil.copytree(src, dst, ignore=shutil.ignore_patterns(
                '__pycache__', '*.pyc', '*.pyo', '*.pyd', '.git*', '*.egg-info'
            ))
            print(f"  ✅ {dir_name}/")
        else:
            print(f"  ⚠️  Bỏ qua {dir_name}/ (không tồn tại)")

    # Tạo thư mục output trống
    output_dir = RELEASE_DIR / "output"
    output_dir.mkdir(exist_ok=True)
    (output_dir / ".gitkeep").write_text("")
    print("  ✅ output/ (trống)")

    # Tạo README_RELEASE.txt hướng dẫn cài đặt
    readme_release = RELEASE_DIR / "README_RELEASE.txt"
    readme_release.write_text(
        f"""VoxDub Studio v{VERSION}
{'=' * 50}

HƯỚNG DẪN CÀI ĐẶT NHANH:
1. Chạy setup.bat để cài đặt dependencies
2. Chạy first_run_wizard.bat để cấu hình lần đầu
3. (Tùy chọn) Chạy cai_them_gpu.bat nếu có card NVIDIA
4. Chạy chay_app.bat để khởi động ứng dụng

HOẶC:

Chạy VoxDubStudio.exe trực tiếp (nếu đã cài đặt đầy đủ)

Chi tiết xem README.md
""",
        encoding="utf-8",
    )
    print("  ✅ README_RELEASE.txt")


def create_archive() -> None:
    """Tạo file .zip từ thư mục release."""
    print(f"\n🗜️  Tạo archive {ARCHIVE_NAME}...")

    if not RELEASE_DIR.exists():
        print(f"❌ Không tìm thấy {RELEASE_DIR}")
        return

    archive_path = DIST_DIR / ARCHIVE_NAME

    with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(RELEASE_DIR):
            # Bỏ qua __pycache__
            dirs[:] = [d for d in dirs if d != '__pycache__']

            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(DIST_DIR)
                zf.write(file_path, arcname)
                print(f"  + {arcname}")

    file_size = archive_path.stat().st_size / (1024 * 1024)  # MB
    print(f"\n✅ Đã tạo {archive_path} ({file_size:.1f} MB)")


def main() -> None:
    """Main build process."""
    print(f"""
╔═══════════════════════════════════════════════════════════╗
║  VoxDub Studio - Build Script                            ║
║  Version: {VERSION}                                       ║
╚═══════════════════════════════════════════════════════════╝
""")

    # Kiểm tra dependencies
    if not check_dependencies():
        print("\n❌ Build thất bại: thiếu dependencies")
        sys.exit(1)

    # Dọn dẹp
    clean_build()

    # Tạo .spec file
    spec_file = create_spec_file()

    # Build EXE
    if not build_exe(spec_file):
        print("\n❌ Build thất bại")
        sys.exit(1)

    # Bundle release
    bundle_release()

    # Tạo archive
    create_archive()

    print(f"""
╔═══════════════════════════════════════════════════════════╗
║  ✅ BUILD HOÀN TẤT                                        ║
╚═══════════════════════════════════════════════════════════╝

📦 Package: {DIST_DIR / ARCHIVE_NAME}
📂 Folder:  {RELEASE_DIR}

BƯỚC TIẾP THEO:
1. Giải nén {ARCHIVE_NAME}
2. Chạy setup.bat để cài đặt
3. Chạy first_run_wizard.bat để cấu hình
4. Chạy chay_app.bat hoặc VoxDubStudio.exe

Sẵn sàng phát hành! 🚀
""")


if __name__ == "__main__":
    main()
