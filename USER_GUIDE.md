# Survival Curve Extractor - User Guide

## 📋 Table of Contents
1. [Getting Started](#getting-started)
2. [First Time Setup](#first-time-setup)
3. [Using the Application](#using-the-application)
4. [Troubleshooting](#troubleshooting)

---

## 🚀 Getting Started

### What You Need
- A computer running Windows 10/11 or macOS 10.12 or newer
- The downloaded application file
- A folder containing your survival curve images

### Download the Application

#### For Mac Users:
1. Download `SurvivalCurveExtractor-macOS-arm64.zip` (for newer Macs with M1/M2 chips)
   OR `SurvivalCurveExtractor-macOS-x64.zip` (for older Intel Macs)
2. Find the downloaded file in your Downloads folder

#### For Windows Users:
1. Download `SurvivalCurveExtractor-Windows-x64.zip`
2. Find the downloaded file in your Downloads folder

---

## 🔧 First Time Setup

### Mac Installation Steps

1. **Extract the Application**
   - Double-click the downloaded `.zip` file
   - A new folder will appear with `SurvivalCurveExtractor.app` inside

2. **Move to Applications (Optional)**
   - Drag `SurvivalCurveExtractor.app` to your Applications folder
   - This makes it easier to find later

3. **First Launch**
   - Right-click (or Control-click) on `SurvivalCurveExtractor.app`
   - Select "Open" from the menu
   - Click "Open" when macOS asks if you're sure
   - (You only need to do this the first time)

### Windows Installation Steps

1. **Extract the Application**
   - Right-click the downloaded `.zip` file
   - Select "Extract All..."
   - Choose where to extract (Desktop is fine)
   - Click "Extract"

2. **First Launch**
   - Open the extracted folder
   - Double-click `SurvivalCurveExtractor.exe`
   - If Windows shows a security warning:
     - Click "More info"
     - Click "Run anyway"
   - (You only need to do this the first time)

---

## 📊 Using the Application

### Step 1: Prepare Your Data

Before starting, organize your files:

```
📁 Your_Project_Folder/
   📁 extraction_data/
      📁 png/
         📄 image1.png
         📄 image2.png
         📄 ...
      📁 metatdata/
         📄 image1.json
         📄 image2.json
         📄 ...
      📁 results/
         (This will be created automatically)
```

### Step 2: Start the Application

1. **Launch the app** by double-clicking it
2. A window will open showing "Select a dataset to begin image annotation"

### Step 3: Load Your Dataset

1. Click **"Select Dataset"** button at the top
2. Navigate to and select your `extraction_data` folder
3. The first image will load automatically

### Step 4: Calibrate the Axes

This tells the software what values correspond to the axes in your image.

1. **Look for "1. Axis Calibration"** on the left side
2. Enter the axis values:
   - X-min: The leftmost value on the X-axis (e.g., 0)
   - X-max: The rightmost value on the X-axis (e.g., 30)
   - Y-min: The bottom value on the Y-axis (e.g., 0)
   - Y-max: The top value on the Y-axis (e.g., 100)

3. Click **"Start Calibration"**
4. Click on these points in order:
   - Click on the leftmost X-axis point
   - Click on the rightmost X-axis point
   - Click on the lowest Y-axis point
   - Click on the highest Y-axis point

💡 **Tip**: Enable "Show Zoom Window" for precise clicking!

### Step 5: Extract Data Points

After calibration:

1. The software automatically creates horizontal guidelines at 0%, 25%, 50%, 75%, and 100%
2. For each survival curve in your image:
   - Click where the curve intersects each percentage line
   - The software automatically records the time value

3. The data table on the right shows your progress

### Step 6: Save Your Progress

Your work is **automatically saved** as you go! You'll see status updates like:
- "Image marked as DONE ✓" when you click Done
- "Status cleared" when you click Undone

### Step 7: Navigate Between Images

Use the navigation bar at the top:
- **◀ Previous** / **Next ▶** buttons to move between images
- Progress bar shows completion percentage
- Status indicators:
  - ✓ = Done
  - ✗ = Has errors
  - ○ = Not completed

**Filter Option**: Check "Show only incomplete" to skip finished images

### Step 8: Mark Images Complete

When you finish extracting data from an image:
1. Click the **"Done"** button
2. The image is marked with ✓
3. Move to the next image

If you made a mistake:
- Click **"Undone"** to clear the status
- Click **"Report Error"** if there's a problem with the image

---

## 🔍 Troubleshooting

### Common Issues and Solutions

#### "Can't open the app" (Mac)
- Make sure you right-clicked and selected "Open" the first time
- Go to System Preferences > Security & Privacy
- Click "Open Anyway" if you see the app mentioned

#### "Windows protected your PC" (Windows)
- This is normal for downloaded apps
- Click "More info" then "Run anyway"

#### Images aren't loading
- Check that your folder structure matches the required format
- Make sure image files are .PNG format
- Verify the `metatdata` folder is spelled correctly (note the typo!)

#### Can't see the zoom window
- Make sure "Show Zoom Window" is checked
- The zoom window appears in the top-right corner
- Move your mouse slowly for smoother zoom updates

#### Lost my work
- Don't worry! The app auto-saves everything
- Check the `extraction_data/results/` folder
- Your data is saved as JSON files with the same names as your images

### Need More Help?

- All extracted data is saved in `extraction_data/results/`
- Each image's data is saved as a `.json` file
- You can open these files in any text editor to see your data

---

## 💡 Pro Tips

1. **Use keyboard shortcuts**:
   - Arrow keys to navigate images quickly
   - Tab to move between input fields

2. **Zoom window**:
   - Red crosshairs show exactly where you'll click
   - Red horizontal lines show the survival percentages

3. **Batch processing**:
   - Use "Show only incomplete" to focus on unfinished work
   - The progress bar helps track overall completion

4. **Quality check**:
   - Click "View Data" to review extracted points
   - Values are shown in real units (not pixels)

---

## 📁 Output Format

Your extracted data is saved in JSON format in the `results` folder:

```json
{
  "metadata": {
    "image_file": "example.png",
    "extraction_date": "2024-08-14T10:30:00",
    "x_axis_units": "months",
    "y_axis_units": "% survival"
  },
  "extracted_points": {
    "0%": {
      "Group A": 5.2,
      "Group B": 4.8
    },
    "50%": {
      "Group A": 12.5,
      "Group B": 10.3
    }
  }
}
```

---

Remember: The application **auto-saves** your work, so you can close and reopen it anytime without losing progress!