# bandle.spec
# Auto-converted from your CLI command

# 1. Data files (from --add-data)
import certifi

import demucs
demucs_path = os.path.dirname(demucs.__file__)
remote_path = os.path.join(demucs_path, "remote")

datas = [
    ("assets", "assets"),
    ("font", "font"),
    ("ffmpeg", "ffmpeg"),
    (remote_path, "demucs/remote"),
    (certifi.where(), "certifi"),
]

# 3. Analysis
a = Analysis(
    ['quick_start.py', 'console.py'],      # your main script
    pathex=[],           # optionally add extra search paths
    binaries=[],
    datas=datas,
    #hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=['torchcodec'],  # optional: avoid TorchCodec issues
    noarchive=False
)

# 4. PYZ (packed Python bytecode)
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# 5. Executable
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='bandle',
    debug=False,
    strip=False,
    upx=True,
    console=True  # keep console for debugging
)

# 6. Collect everything into onedir
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    name='bandle'
)