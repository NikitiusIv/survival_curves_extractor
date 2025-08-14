# Building Survival Curve Extractor for Windows

## Prerequisites

1. **Windows 10 or 11** (64-bit)
2. **Python 3.9-3.14** installed from [python.org](https://python.org)
3. **Git** (to clone the repository)

## Step-by-Step Build Instructions

### 1. Clone the Repository

Open Command Prompt or PowerShell and run:
```cmd
git clone https://github.com/NikitiusIv/survival_curves_extractor.git
cd survival_curves_extractor
```

### 2. Install Poetry

```cmd
# Install pipx first (recommended)
python -m pip install --user pipx
python -m pipx ensurepath

# Restart your terminal, then install poetry
pipx install poetry
```

Alternative (direct pip install):
```cmd
pip install poetry
```

### 3. Install Dependencies

```cmd
poetry install
```

### 4. Build the Windows Executable

```cmd
poetry run python build.py
```

Or use the simple build command:
```cmd
poetry run pyinstaller --onefile --windowed --name "SurvivalCurveExtractor" --hidden-import="PIL._tkinter_finder" main.py
```

### 5. Find Your Build

The executable will be created in:
- `dist/SurvivalCurveExtractor.exe`
- `dist/SurvivalCurveExtractor-Windows-x64.zip` (if using build.py)

## Troubleshooting Windows Build

### Common Issues:

1. **"Python not found"**
   - Make sure Python is in your PATH
   - Try `py -m pip` instead of `python -m pip`

2. **Poetry not found**
   - Restart terminal after pipx install
   - Or use: `python -m poetry` instead of `poetry`

3. **Build fails with "Module not found"**
   - Ensure you're in the virtual environment: `poetry shell`
   - Then run: `pyinstaller survival_curve_extractor.spec`

4. **Antivirus blocks the build**
   - Temporarily disable antivirus during build
   - Add project folder to antivirus exceptions

### Manual Build Steps (if automated build fails):

1. **Activate Poetry environment**:
   ```cmd
   poetry shell
   ```

2. **Run PyInstaller directly**:
   ```cmd
   pyinstaller survival_curve_extractor.spec
   ```

3. **Create ZIP manually**:
   - Right-click on `dist/SurvivalCurveExtractor.exe`
   - Select "Send to" → "Compressed (zipped) folder"
   - Rename to `SurvivalCurveExtractor-Windows-x64.zip`

## Testing the Build

1. **Run the executable**:
   ```cmd
   dist\SurvivalCurveExtractor.exe
   ```

2. **Check for errors**:
   - If it doesn't start, run from command prompt to see error messages
   - Common issue: Missing Visual C++ Redistributable

## Creating a Clean Build

To ensure a clean build:
```cmd
# Remove previous builds
rmdir /s /q build dist

# Clear PyInstaller cache
rmdir /s /q __pycache__

# Rebuild
poetry run python build.py
```

## Cross-Building Note

**Important**: You cannot build Windows executables on macOS or Linux. Each platform's executable must be built on that platform. This is because:
- PyInstaller bundles platform-specific Python interpreter
- Windows DLLs are different from macOS/Linux libraries
- GUI frameworks have platform-specific implementations

## Alternative: GitHub Actions

For automated builds on multiple platforms, consider setting up GitHub Actions:

```yaml
# .github/workflows/build.yml
name: Build Executables

on:
  push:
    tags:
      - 'v*'

jobs:
  build-windows:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - name: Install Poetry
        run: pip install poetry
      - name: Install dependencies
        run: poetry install
      - name: Build with PyInstaller
        run: poetry run python build.py
      - name: Upload artifact
        uses: actions/upload-artifact@v3
        with:
          name: windows-executable
          path: dist/SurvivalCurveExtractor-Windows-*.zip
```

This would automatically build Windows executables when you push a new tag.