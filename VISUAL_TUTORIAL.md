# 📸 Visual Tutorial - Survival Curve Extractor

## Step-by-Step with Screenshots

### 🖥️ Opening the Application

#### Mac Users:
![Mac Security Dialog](screenshots/mac-security.png)
*When you see this, click "Open"*

#### Windows Users:
![Windows Defender](screenshots/windows-defender.png)
*Click "More info" then "Run anyway"*

---

### 📂 Loading Your Dataset

![Select Dataset Button](screenshots/select-dataset.png)
1. Click the **"Select Dataset"** button at the top
2. Navigate to your `extraction_data` folder
3. Click "Open" or "Select Folder"

---

### 📊 Understanding the Interface

![Main Interface](screenshots/main-interface.png)

**Key Areas:**
- 🟦 **Left Panel**: Controls for calibration and data entry
- 🟩 **Center**: Your survival curve image
- 🟨 **Right Panel**: Data table showing extracted points
- 🟥 **Top Bar**: Navigation and progress tracking

---

### 📏 Calibrating the Axes

![Calibration Process](screenshots/calibration.png)

**Step 1: Enter Values**
- X-min: `0` (start of time axis)
- X-max: `30` (end of time axis)
- Y-min: `0` (bottom of survival axis)
- Y-max: `100` (top of survival axis)

**Step 2: Click Points**
Follow the prompts to click:
1. ⬅️ Leftmost point on X-axis
2. ➡️ Rightmost point on X-axis
3. ⬇️ Bottom point on Y-axis
4. ⬆️ Top point on Y-axis

---

### 🔍 Using the Zoom Window

![Zoom Window](screenshots/zoom-window.png)

**Features:**
- ✅ Red crosshairs for precise targeting
- ✅ Red horizontal lines show survival percentages
- ✅ Follows your mouse for easy positioning

---

### 📍 Extracting Data Points

![Data Extraction](screenshots/data-extraction.png)

**How to Extract:**
1. Survival lines appear automatically after calibration
2. Click where each curve crosses the percentage lines
3. The table updates in real-time
4. Green checkmarks show completed points

---

### ✅ Marking Images Complete

![Status Buttons](screenshots/status-buttons.png)

**Status Options:**
- **Done**: Image fully processed ✓
- **Undone**: Clear the status
- **Report Error**: Flag problematic images
- **View Data**: Check your extracted values

---

### 🧭 Navigation Controls

![Navigation Bar](screenshots/navigation.png)

**Features:**
- ◀️ ▶️ Previous/Next buttons
- 📊 Progress bar (shows 73% complete)
- 🔢 Image counter (15/89)
- ✓ ✗ ○ Status indicators
- ☑️ "Show only incomplete" filter

---

### 💾 Your Saved Data

![Results Folder](screenshots/results-folder.png)

All data is automatically saved in:
```
extraction_data/
  └── results/
      ├── image1.json ✓
      ├── image2.json ✓
      └── image3.json ○
```

---

## 🎯 Complete Workflow

1. **Start** → Open application
2. **Load** → Select dataset folder
3. **Calibrate** → Set axis values and click 4 points
4. **Extract** → Click curve intersections
5. **Save** → Automatic (just click Done)
6. **Navigate** → Next image
7. **Repeat** → Until 100% complete!

---

## 📝 Notes

- **Auto-save**: Every action is saved immediately
- **Resume**: Close and reopen anytime - your progress is kept
- **Undo**: Use "Undone" button to reset an image
- **Filter**: Use "Show only incomplete" to skip finished work

---

*Note: Screenshots are placeholders. Actual interface may vary slightly based on your operating system.*