# bandle.spec
# Auto-converted from your CLI command

# 1. Data files (from --add-data)
import certifi
datas = [
    ("assets", "assets"),
    ("font", "font"),
    ("ffmpeg", "ffmpeg"),
    (r"C:\Users\user\Documents\github projects\bandle clone\venv\lib\site-packages\demucs\remote", "demucs/remote"),
    #(r"C:\Users\user\AppData\Roaming\Python\Python310\site-packages\demucs\remote", "demucs/remote"),
    (certifi.where(), "certifi"),
]

# 3. Analysis
a = Analysis(
    ['quick_start.py'],      # your main script
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