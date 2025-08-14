# ❓ Frequently Asked Questions

## General Questions

### Q: Do I need to install Python?
**A:** No! The application is completely standalone and includes everything needed.

### Q: What image formats are supported?
**A:** Currently only PNG images are supported. Convert other formats to PNG first.

### Q: How is my data saved?
**A:** Data is automatically saved as JSON files in the `extraction_data/results/` folder. Every click is saved immediately.

### Q: Can multiple people work on the same dataset?
**A:** Yes, but not simultaneously. Share the `extraction_data` folder and work in turns.

---

## Installation Issues

### Q: "Cannot open because developer cannot be verified" (Mac)
**A:** This is normal. Right-click the app, select "Open", then click "Open" in the dialog.

### Q: "Windows protected your PC" message
**A:** This is Windows Defender being cautious. Click "More info" then "Run anyway".

### Q: Where should I put the application?
**A:** Anywhere you like! Desktop, Applications folder, or Documents all work fine.

---

## Using the Application

### Q: What does "metatdata" mean? Is it a typo?
**A:** Yes, it's a typo in the original folder structure, but the app expects this exact spelling. Don't correct it!

### Q: How precise do I need to be when clicking?
**A:** Use the zoom window for precision. Being within 1-2 pixels is usually fine.

### Q: What if I clicked the wrong point?
**A:** Just click the correct point - it will update automatically. Or use "Undone" to reset the image.

### Q: Can I skip images?
**A:** Yes! Use the navigation arrows. Incomplete images show as ○ in the counter.

### Q: What do the status symbols mean?
**A:** 
- ✓ = Completed successfully
- ✗ = Has reported errors  
- ○ = Not yet completed

---

## Data Questions

### Q: What units should I use for axes?
**A:** Use whatever units are shown on your graph (months, days, years for time; percentage for survival).

### Q: What if my survival axis goes from 100% at bottom to 0% at top?
**A:** Enter Y-min as 100 and Y-max as 0. The software handles inverted axes.

### Q: Can I edit the extracted data later?
**A:** Yes, you can:
1. Reopen the image in the app and modify points
2. Edit the JSON files directly (for advanced users)

### Q: How do I export to Excel?
**A:** The JSON files can be:
1. Imported into Excel using Data → Get Data → From File → From JSON
2. Converted using online JSON-to-CSV converters
3. Processed with a script (ask your data analyst)

---

## Troubleshooting

### Q: The zoom window isn't showing
**A:** Make sure "Show Zoom Window" is checked in the controls panel.

### Q: Images look blurry after calibration
**A:** This is normal - the app shows guidelines over the image. The original image is unchanged.

### Q: I accidentally marked an image as "Done" 
**A:** Click the "Undone" button to clear the status.

### Q: The app crashes when I load my dataset
**A:** Check that:
- Your folder structure is correct
- All images are PNG format
- The folders are named exactly `png` and `metatdata`

### Q: Can I move the extraction_data folder?
**A:** Yes, but you'll need to re-select it in the app using "Select Dataset".

---

## Advanced Questions

### Q: Can I process multiple datasets?
**A:** Yes! Use "Select Dataset" to switch between different extraction_data folders.

### Q: Is there a batch processing mode?
**A:** Not currently. Each image needs manual calibration and point selection.

### Q: Can I customize the survival percentages (0%, 25%, etc.)?
**A:** Not in the current version. The five standard percentages are fixed.

### Q: What's the maximum image size supported?
**A:** There's no hard limit, but very large images (>10MB) may be slow. Resize if needed.

---

## Data Recovery

### Q: I accidentally deleted my results!
**A:** Check your system's Recycle Bin/Trash first. The JSON files might be recoverable.

### Q: Can I merge results from multiple people?
**A:** Yes, just copy all JSON files into the same results folder. Make sure filenames don't conflict.

### Q: How do I backup my work?
**A:** Simply copy the entire `extraction_data` folder to a backup location or cloud storage.

---

## Still Need Help?

If your question isn't answered here:
1. Check the [User Guide](USER_GUIDE.md) for detailed instructions
2. Visit the [GitHub repository](https://github.com/NikitiusIv/survival_curves_extractor) for updates
3. Report issues on the GitHub Issues page