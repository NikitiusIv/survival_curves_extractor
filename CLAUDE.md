# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Development Commands

### Running the Application
```bash
python main.py
```

### Building the Application
```bash
# Using the build script (recommended)
poetry run python build.py

# Simple single-file executable
./build_simple.sh  # On macOS/Linux

# Manual PyInstaller build
poetry run pyinstaller --onefile --windowed --name "SurvivalCurveExtractor" main.py
```

### Managing Dependencies
```bash
# Install dependencies
poetry install

# Add a new dependency
poetry add <package_name>

# Update dependencies
poetry update
```

## High-Level Architecture

### Application Overview
The Survival Curve Extractor is a Python-based GUI application for digitizing survival curve plots from scientific papers. It uses Tkinter for the UI and PIL/Pillow for image processing.

### Core Components

1. **Main Application Class (`SurvivalCurveExtractor`)**: Located in `main.py`, this monolithic class manages the entire application state and UI. Key responsibilities:
   - Dataset navigation and image loading
   - Axis calibration system with 4-point clicking
   - Data point extraction with zoom view
   - Auto-save functionality with smart save logic
   - Progress tracking and status management

2. **Data Persistence Architecture**:
   - Uses JSON files for storing extracted data points
   - Implements a three-tier data priority system:
     1. User-entered results data (highest priority)
     2. Metadata from external sources
     3. Default/empty state
   - Includes flags to prevent save cascades during loading

3. **UI Layout**:
   - Left panel: Image canvas with calibration/extraction capabilities
   - Right panel: Control interface with axis configuration, group management, and data table
   - Navigation bar: Dataset selection and image navigation with progress tracking
   - Status indicators: Visual feedback (✓/✗/○) for completion status

4. **Key Technical Considerations**:
   - Cross-platform compatibility (Windows/macOS) with platform-specific UI adjustments
   - Custom button implementation for macOS due to Tkinter styling limitations
   - Zoom window functionality for precise point selection
   - Real-time marker updates as data is modified

### Data Flow
1. User selects dataset folder containing PNG images and optional metadata
2. Calibration establishes coordinate system mapping
3. Points are extracted by clicking on curve intersections
4. Data auto-saves to JSON files alongside images
5. Export format preserves metadata and extracted coordinates

### File Structure
- `extraction_data/`: Root dataset directory
  - `png/`: Image files to process
  - `metadata/`: Optional pre-populated metadata JSON files
  - `*_extracted_survival_time_points.json`: Output files with extracted data

## Code Style Guidelines

### Naming Conventions
- **Variables**: Use snake_case for all variable names
  ```python
  current_image_path = "path/to/image.png"
  scale_factor = 1.5
  zoom_window = None
  ```

- **Functions/Methods**: Use snake_case for all function and method names
  ```python
  def load_image(self, path):
  def get_real_coordinates(self, canvas_x, canvas_y):
  def auto_save_current_state(self):
  ```

- **Classes**: Use PascalCase for class names
  ```python
  class SurvivalCurveExtractor:
  ```

- **Constants**: While not strictly enforced in the current codebase, prefer UPPER_SNAKE_CASE for true constants
  ```python
  DEFAULT_ZOOM_SIZE = 150
  MAX_RETRIES = 3
  ```

### Code Organization
- Keep the monolithic class structure for the main application (maintains consistency)
- Group related methods together logically:
  - UI setup methods
  - Data loading/saving methods
  - Event handlers
  - Utility methods
- Use descriptive method names that clearly indicate their purpose

### Documentation
- Add module-level docstrings at the top of Python files:
  ```python
  """
  Module description explaining the purpose and functionality.
  """
  ```

- Use single-line docstrings for methods:
  ```python
  def method_name(self):
      """Brief description of what the method does."""
  ```

- Add inline comments for complex logic:
  ```python
  # Calculate the real coordinates based on calibration data
  real_x = self.axis_calibration['x_min'] + (x_ratio * x_range)
  ```

### Error Handling
- Always use try-except blocks for file operations and external interactions:
  ```python
  try:
      with open(file_path, 'r') as f:
          data = json.load(f)
  except Exception as e:
      messagebox.showerror("Error", f"Failed to load file: {str(e)}")
      return None
  ```

- Use specific exception types when possible
- Report user-facing errors with `messagebox.showerror()`
- Use `print()` statements for debugging information during development

### Import Organization
Follow this order for imports:
```python
# Standard library imports
import json
import os
from pathlib import Path

# Third-party imports
from PIL import Image, ImageTk

# Type imports
from typing import Dict, List, Optional, Tuple
```

### Platform-Specific Code
- Use `platform.system()` to detect the operating system:
  ```python
  if platform.system() == "Darwin":  # macOS
      # macOS-specific code
  ```

- Create platform-specific helper methods when needed
- Document any platform-specific workarounds

### Data Persistence
- Always use JSON for data storage
- Structure data files consistently:
  ```python
  data = {
      "metadata": {...},
      "calibration": {...},
      "groups": [...],
      "extracted_data": {...}
  }
  ```

- Include version information in saved data for future compatibility
- Use the established three-tier data priority system

### UI Development
- Use the `create_button()` helper for cross-platform button creation
- Maintain consistent styling through the `self.colors` dictionary
- Group related UI elements in frames
- Use descriptive variable names for UI elements:
  ```python
  self.calibration_frame = ttk.Frame(...)
  self.save_button = self.create_button(...)
  ```

### Best Practices
1. **Path Handling**: Always use `pathlib.Path` for file system operations
2. **String Formatting**: Use f-strings for string formatting
3. **File Operations**: Always use context managers (`with` statements)
4. **State Management**: Use boolean flags to track application state
5. **Auto-save**: Implement auto-save after user actions that modify data
6. **User Feedback**: Provide clear error messages and status updates
7. **Graceful Degradation**: Fall back to defaults when operations fail

### Testing Approach
While the codebase doesn't include automated tests, follow these practices:
- Test all features manually before committing changes
- Verify cross-platform compatibility (Windows, macOS, Linux)
- Test with various image formats and sizes
- Ensure data persistence works correctly
- Verify that auto-save doesn't interfere with data loading

### Common Patterns to Follow
1. **Loading Data with Flags**:
   ```python
   self.loading_in_progress = True
   try:
       # Load data
   finally:
       self.loading_in_progress = False
   ```

2. **Platform-Specific UI Adjustments**:
   ```python
   def create_button(self, parent, **kwargs):
       if platform.system() == "Darwin":
           # macOS-specific button creation
       else:
           # Standard button creation
   ```

3. **Safe Data Access**:
   ```python
   value = data.get('key', default_value)
   ```

4. **User Confirmation for Destructive Actions**:
   ```python
   if messagebox.askyesno("Confirm", "Are you sure?"):
       # Perform action
   ```

### Code Maintenance
- Keep the existing monolithic structure (refactoring would break compatibility)
- Add new features as methods within the main class
- Maintain backwards compatibility with existing data files
- Update documentation when adding new features
- Test thoroughly on all supported platforms before releasing

### Version Control
- Make atomic commits with clear messages
- Test changes before committing
- Update version numbers in relevant files when releasing
- Document any breaking changes in commit messages