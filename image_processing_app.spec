# PyInstaller spec file for Image Processing App
# Build with: pyinstaller image_processing_app.spec
#
# First-time setup:
#   pip install pyinstaller
#
# Output:
#   dist/Image Processing App.app   (macOS)
#   dist/Image Processing App/      (Windows/Linux — wrap in installer)

from PyInstaller.utils.hooks import collect_all, collect_submodules

# Collect all data files, binaries, and hidden imports for packages that
# PyInstaller cannot fully introspect at build time.
torch_datas,       torch_bins,    torch_hidden    = collect_all('torch')
torchvision_datas, tv_bins,       tv_hidden       = collect_all('torchvision')
pyside6_datas,     pyside6_bins,  pyside6_hidden  = collect_all('PySide6')
sklearn_datas,     sklearn_bins,  sklearn_hidden  = collect_all('sklearn')
scipy_datas,       scipy_bins,    scipy_hidden    = collect_all('scipy')
mpl_datas,         mpl_bins,      mpl_hidden      = collect_all('matplotlib')
sns_datas,         sns_bins,      sns_hidden      = collect_all('seaborn')
pil_datas,         pil_bins,      pil_hidden      = collect_all('PIL')

# torch.distributed spawns background threads when imported during PyInstaller's
# analysis phase, which prevents the worker subprocess from exiting and causes a
# build timeout. Strip those entries from the collected hidden imports list.
# The excludes list below stops them from being bundled at all.
_TORCH_EXCLUDE_PREFIXES = (
    'torch.distributed',
    'torch.testing',
    'torch.utils.tensorboard',
    'torch._dynamo',
    'torch._numpy',
    'torch._inductor',
)
torch_hidden = [
    h for h in torch_hidden
    if not any(h.startswith(p) for p in _TORCH_EXCLUDE_PREFIXES)
]

# PySide6.scripts.deploy_lib requires an optional 'project_lib' package that is
# not installed — filter it out to silence the warning.
pyside6_hidden = [h for h in pyside6_hidden if 'deploy_lib' not in h]

a = Analysis(
    ['image_processing_app.py'],
    pathex=['.'],
    binaries=(
        torch_bins + tv_bins + pyside6_bins +
        sklearn_bins + scipy_bins + mpl_bins + sns_bins + pil_bins
    ),
    datas=(
        torch_datas + torchvision_datas + pyside6_datas +
        sklearn_datas + scipy_datas + mpl_datas + sns_datas + pil_datas
    ),
    hiddenimports=(
        torch_hidden + tv_hidden + pyside6_hidden +
        sklearn_hidden + scipy_hidden + mpl_hidden + sns_hidden + pil_hidden +
        # App modules — explicit so they survive tree-shaking
        [
            'run_models',
            'tabs',
            'tabs.home_tab',
            'tabs.Image_Modification_Page',
            'tabs.analysis_setup_tab',
            'tabs.results_tab',
            'tabs.documentation_tab',
            'tabs.modification_tab',
        ]
    ),
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[
        'hooks/rthook_inspect_frozen.py',
        'hooks/rthook_torch_dynamo_stub.py',
    ],
    # Packages that are never used at runtime — trim to reduce bundle size.
    # torch.distributed is also excluded because it spawns threads during import
    # which cause a build-time analysis timeout.
    excludes=[
        'torch.distributed',
        'torch.testing',
        'torch.utils.tensorboard',
        # _dynamo and _numpy are stubbed via runtime hook — exclude from bundle
        # to avoid the vars()[name] NameError in _numpy/_ufuncs.py when frozen
        'torch._dynamo',
        'torch._numpy',
        'torch._inductor',
        'PySide6.scripts',
        'IPython',
        'jupyter',
        'notebook',
    ],
    # Store Python modules as individual .pyc files rather than a compressed
    # PYZ archive. PyInstaller's PYZ importer doesn't fully replicate Python's
    # normal module execution environment — dir() at module-level can't see
    # variables assigned earlier in the same module, causing NameErrors in
    # scipy and torch. noarchive=True uses Python's standard .pyc loader,
    # which handles module globals correctly.
    noarchive=True,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Image Processing App',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,          # UPX can corrupt torch/PySide6 binaries — leave off
    console=False,      # No terminal window (GUI app)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,   # None = native arch; set 'x86_64' or 'arm64' to cross-compile
    codesign_identity=None,
    entitlements_file=None,
    icon=None,          # Replace with 'assets/icon.icns' once you have one
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='Image Processing App',
)

# macOS .app bundle
app = BUNDLE(
    coll,
    name='Image Processing App.app',
    icon=None,          # Replace with 'assets/icon.icns' once you have one
    bundle_identifier='com.cs2617.imageprocessingapp',
    info_plist={
        'CFBundleDisplayName': 'Image Processing App',
        'CFBundleShortVersionString': '1.0.0',
        'NSHighResolutionCapable': True,
        'LSMinimumSystemVersion': '11.0',
        # Required on macOS to allow the app to read files outside its sandbox
        'NSDocumentsFolderUsageDescription': 'Access images for analysis.',
        'NSDesktopFolderUsageDescription': 'Access images for analysis.',
    },
)
