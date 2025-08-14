# Automated Cross-Platform Builds

This project uses GitHub Actions to automatically build executables for Windows and macOS.

## How It Works

### Automatic Release Builds

When you create a new release tag (e.g., `v1.0.0`), GitHub automatically:
1. Builds the Windows executable on a Windows server
2. Builds the macOS executable on a macOS server
3. Creates a GitHub Release with both files attached

### Creating a New Release

1. **Update version in pyproject.toml**:
   ```toml
   version = "1.0.0"
   ```

2. **Commit and push changes**:
   ```bash
   git add pyproject.toml
   git commit -m "Bump version to 1.0.0"
   git push
   ```

3. **Create and push a tag**:
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

4. **Wait for builds** (usually 5-10 minutes):
   - Go to Actions tab on GitHub
   - Watch the "Build and Release" workflow
   - When complete, check Releases page

### Manual Build Trigger

You can also trigger builds manually:
1. Go to Actions tab on GitHub
2. Select "Build and Release" workflow
3. Click "Run workflow"
4. Select branch and click "Run workflow"

## Build Outputs

The automated build creates:
- `SurvivalCurveExtractor-Windows-x64.zip` - Windows 64-bit executable
- `SurvivalCurveExtractor-macOS-arm64.zip` - macOS Apple Silicon
- `SurvivalCurveExtractor-macOS-x64.zip` - macOS Intel (if built on Intel runner)

## Local Testing

Before creating a release, test locally:
```bash
# Test the build process
poetry run python build.py

# Test the executable
# macOS
open dist/SurvivalCurveExtractor.app

# Windows
dist\SurvivalCurveExtractor.exe

# Linux
./dist/SurvivalCurveExtractor
```

## Troubleshooting

### Build Fails on GitHub

1. **Check Actions logs**:
   - Click on the failed job
   - Expand the failed step
   - Look for error messages

2. **Common issues**:
   - Python version mismatch - check pyproject.toml
   - Missing dependencies - check poetry.lock is committed
   - Platform-specific issues - test locally first

### Release Not Created

- Ensure tag starts with 'v' (e.g., v1.0.0, not 1.0.0)
- Check that GITHUB_TOKEN has write permissions
- Verify both platform builds succeeded

## Advanced Configuration

### Adding Linux Builds

Uncomment the Linux section in `.github/workflows/build-release.yml`:
```yaml
build-linux:
  runs-on: ubuntu-latest
  steps:
    # ... (similar to other platforms)
```

### Signing Executables

For production releases, consider:
- **Windows**: Code signing certificate
- **macOS**: Apple Developer ID
- Add signing steps to workflow

### Custom Build Matrix

Edit `.github/workflows/build-test.yml` to test on different Python versions:
```yaml
matrix:
  python-version: ['3.9', '3.10', '3.11', '3.12']
```

## Benefits

✅ **No local Windows machine needed** - GitHub provides it
✅ **Consistent builds** - Same environment every time
✅ **Automatic releases** - Just push a tag
✅ **Multi-platform** - Build for all platforms at once
✅ **Free for public repos** - GitHub Actions is free for open source