#!/usr/bin/env python3
"""
Survival Curve Data Extraction Tool

A pure Python tool for extracting data points from survival curve images.
Uses tkinter for GUI and PIL for image handling.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import os
import json
from pathlib import Path
from PIL import Image, ImageTk, ImageDraw
from typing import Dict, List, Optional, Tuple


class SurvivalCurveExtractor:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Survival Curve Data Extractor")
        self.root.geometry("1200x800")
        
        # Data storage
        self.current_image_path = None
        self.original_image = None
        self.display_image = None
        self.canvas_image = None
        self.scale_factor = 1.0
        
        # Zoom view for calibration
        self.zoom_window = None
        self.zoom_canvas = None
        self.zoom_factor = 3.0
        self.zoom_size = 100
        self.zoom_enabled = tk.BooleanVar(value=False)  # Default off
        
        
        # Dragging calibration points
        self.dragging_point = None
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        
        # Calibration data
        self.axis_calibration = {
            'x_min': None, 'x_max': None, 'y_min': None, 'y_max': None,
            'x_min_coord': None, 'x_max_coord': None, 'y_min_coord': None, 'y_max_coord': None
        }
        self.calibration_step = 0
        self.calibration_labels = ['X-axis minimum', 'X-axis maximum', 'Y-axis minimum', 'Y-axis maximum']
        
        # Axis types and units
        self.x_axis_type = 'time'  # 'time' or 'survival'
        self.y_axis_type = 'survival'  # 'survival' or 'time'
        self.x_axis_units = 'months'
        self.y_axis_units = '% cumulative survival'
        
        # Survival rate levels and groups
        self.survival_rates = ['0%', '25%', '50%', '75%', '100%']
        self.groups = []
        self.group_entries = []  # List to store group entry widgets
        
        # Selected data points
        self.selected_points = {}  # key: f"{group}_{time_point}", value: {'x': pixel_x, 'y': pixel_y}
        
        # Currently selected point for editing
        self.selected_point_key = None
        
        # UI setup
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface"""
        # Main frame with paned window for resizable columns
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create horizontal paned window (resizable columns)
        paned_window = tk.PanedWindow(main_frame, orient=tk.HORIZONTAL, sashrelief=tk.RAISED, sashwidth=5)
        paned_window.pack(fill=tk.BOTH, expand=True)
        
        # Left panel for controls with scrolling
        control_container = ttk.Frame(paned_window)
        
        # Create scrollable canvas for controls
        control_canvas = tk.Canvas(control_container, width=140, highlightthickness=0)
        scrollbar = ttk.Scrollbar(control_container, orient="vertical", command=control_canvas.yview)
        self.scrollable_frame = ttk.Frame(control_canvas)
        
        # Configure scrolling
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: control_canvas.configure(scrollregion=control_canvas.bbox("all"))
        )
        
        control_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        control_canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack scrolling components
        control_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mousewheel to canvas
        def _on_mousewheel(event):
            control_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        control_canvas.bind("<MouseWheel>", _on_mousewheel)
        
        control_panel = self.scrollable_frame
        
        # Right panel for image
        self.image_frame = ttk.Frame(paned_window)
        
        # Add both panels to the paned window
        paned_window.add(control_container, minsize=130, width=160)
        paned_window.add(self.image_frame, minsize=400)
        
        # Setup control sections
        self.setup_image_controls(control_panel)
        self.setup_calibration_controls(control_panel)
        self.setup_groups_controls(control_panel)
        self.setup_extraction_controls(control_panel)
        self.setup_export_controls(control_panel)
        
        # Setup image canvas
        self.canvas = tk.Canvas(self.image_frame, bg='white')
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind('<Button-1>', self.on_canvas_click)
        self.canvas.bind('<Motion>', self.on_canvas_motion)
        self.canvas.bind('<B1-Motion>', self.on_canvas_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_canvas_release)
        
        # Scrollbars for canvas
        v_scrollbar = ttk.Scrollbar(self.image_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.configure(yscrollcommand=v_scrollbar.set)
        
        h_scrollbar = ttk.Scrollbar(self.image_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.configure(xscrollcommand=h_scrollbar.set)
        
    def setup_image_controls(self, parent):
        """Setup image loading controls"""
        frame = ttk.LabelFrame(parent, text="1. Load Image", padding=5)
        frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(frame, text="Select Image File", command=self.load_image).pack(fill=tk.X, pady=2)
        ttk.Button(frame, text="Browse Folder", command=self.browse_folder).pack(fill=tk.X, pady=2)
        
        self.image_label = ttk.Label(frame, text="No image loaded", foreground="gray")
        self.image_label.pack(fill=tk.X, pady=5)
        
    def setup_calibration_controls(self, parent):
        """Setup axis calibration controls"""
        frame = ttk.LabelFrame(parent, text="2. Calibrate Axes", padding=5)
        frame.pack(fill=tk.X, pady=(0, 10))
        
        self.calibration_status = ttk.Label(frame, text="Click on X-axis minimum point", foreground="gold")
        self.calibration_status.pack(fill=tk.X, pady=5)
        
        input_frame = ttk.Frame(frame)
        input_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(input_frame, text="Value:").pack(side=tk.LEFT)
        self.calibration_value = ttk.Entry(input_frame)
        self.calibration_value.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 5))
        
        self.calibration_btn = ttk.Button(input_frame, text="Set", width=3, command=self.set_calibration_point, state=tk.DISABLED)
        self.calibration_btn.pack(side=tk.LEFT)
        
        ttk.Button(frame, text="Reset Calibration", command=self.reset_calibration).pack(fill=tk.X, pady=2)
        
        
        # Zoom control
        zoom_frame = ttk.Frame(frame)
        zoom_frame.pack(fill=tk.X, pady=5)
        self.zoom_checkbox = ttk.Checkbutton(zoom_frame, text="Enable Zoom Window", variable=self.zoom_enabled, command=self.on_zoom_toggle)
        self.zoom_checkbox.pack(side=tk.LEFT)
        
        # Axis type selection
        axis_frame = ttk.Frame(frame)
        axis_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(axis_frame, text="X-axis type:").pack(side=tk.LEFT)
        self.x_axis_var = tk.StringVar(value="time")
        x_axis_combo = ttk.Combobox(axis_frame, textvariable=self.x_axis_var, values=["time", "survival"], state="readonly", width=10)
        x_axis_combo.pack(side=tk.LEFT, padx=5)
        x_axis_combo.bind('<<ComboboxSelected>>', self.on_axis_type_change)
        
        ttk.Label(axis_frame, text="Y-axis:").pack(side=tk.LEFT, padx=(10, 0))
        self.y_axis_label = ttk.Label(axis_frame, text="survival", foreground="gold")
        self.y_axis_label.pack(side=tk.LEFT, padx=5)
        
        # Units input fields (stacked vertically)
        units_frame = ttk.Frame(frame)
        units_frame.pack(fill=tk.X, pady=5)
        
        # X-axis units (auto-resizable)
        x_units_frame = ttk.Frame(units_frame)
        x_units_frame.pack(fill=tk.X, pady=(0, 3))
        ttk.Label(x_units_frame, text="X-axis units:").pack(side=tk.LEFT)
        self.x_units_entry = ttk.Entry(x_units_frame)
        self.x_units_entry.insert(0, self.x_axis_units)
        self.x_units_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        
        # Y-axis units (auto-resizable)
        y_units_frame = ttk.Frame(units_frame)
        y_units_frame.pack(fill=tk.X)
        ttk.Label(y_units_frame, text="Y-axis units:").pack(side=tk.LEFT)
        self.y_units_entry = ttk.Entry(y_units_frame)
        self.y_units_entry.insert(0, self.y_axis_units)
        self.y_units_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        
    def setup_groups_controls(self, parent):
        """Setup group management controls"""
        frame = ttk.LabelFrame(parent, text="3. Set Groups", padding=5)
        frame.pack(fill=tk.X, pady=(0, 10))
        
        # Button to add new group
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=3)
        
        ttk.Button(button_frame, text="+", width=2, command=self.add_group_field).pack(side=tk.LEFT, padx=(0, 1))
        ttk.Button(button_frame, text="Upd", width=3, command=self.update_groups).pack(side=tk.LEFT, padx=1)
        ttk.Button(button_frame, text="Clr", width=3, command=self.clear_all_groups).pack(side=tk.LEFT, padx=1)
        
        self.groups_parent = frame.master
        
        # Scrollable frame for group entries
        self.groups_canvas = tk.Canvas(frame, height=120, bg='white')
        self.groups_scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.groups_canvas.yview)
        self.groups_scrollable_frame = ttk.Frame(self.groups_canvas)
        
        self.groups_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.groups_canvas.configure(scrollregion=self.groups_canvas.bbox("all"))
        )
        
        self.groups_canvas.create_window((0, 0), window=self.groups_scrollable_frame, anchor="nw")
        self.groups_canvas.configure(yscrollcommand=self.groups_scrollbar.set)
        
        # Pack scrollable area
        self.groups_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=3)
        self.groups_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=3)
        
        # Add initial group field
        self.add_group_field()
        
    def setup_extraction_controls(self, parent):
        """Setup data extraction controls"""
        frame = ttk.LabelFrame(parent, text="4. Set Time Points at Survival Rates", padding=5)
        frame.pack(fill=tk.X, pady=(0, 10))
        
        # Instructions for new workflow
        instruction_label = ttk.Label(frame, text="Select a point in the table below, then click on the image to set its position", foreground="gold")
        instruction_label.pack(fill=tk.X, pady=5)
        
        ttk.Button(frame, text="Show Survival Rate Lines", command=self.show_survival_rate_lines).pack(fill=tk.X, pady=2)
        
        # Data points list view
        ttk.Label(frame, text="Extracted Points:").pack(fill=tk.X, pady=(10, 0))
        
        # Instructions for user
        instruction_frame = ttk.Frame(frame)
        instruction_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(instruction_frame, text="Double-click to edit • Delete key to remove", foreground='gray', font=('Arial', 8)).pack(side=tk.RIGHT)
        
        # Create treeview for showing points
        self.points_tree = ttk.Treeview(frame, columns=('Group', 'Survival Rate', 'Time Value'), show='headings', height=6)
        self.points_tree.heading('Group', text='Group')
        self.points_tree.heading('Survival Rate', text='Survival Rate')
        self.points_tree.heading('Time Value', text='Time Value')
        
        self.points_tree.column('Group', width=80)
        self.points_tree.column('Survival Rate', width=100)
        self.points_tree.column('Time Value', width=100)
        
        # Scrollbar for treeview
        points_scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.points_tree.yview)
        self.points_tree.configure(yscrollcommand=points_scrollbar.set)
        
        # Pack treeview and scrollbar
        points_frame = ttk.Frame(frame)
        points_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        self.points_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        points_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Add editing functionality
        self.points_tree.bind("<Double-Button-1>", self.on_treeview_edit)
        self.points_tree.bind("<Delete>", self.on_treeview_delete)
        self.points_tree.bind("<BackSpace>", self.on_treeview_delete)
        self.points_tree.bind("<<TreeviewSelect>>", self.on_treeview_select)
        
    def setup_export_controls(self, parent):
        """Setup export controls"""
        frame = ttk.LabelFrame(parent, text="5. Export Data", padding=5)
        frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(frame, text="Export JSON", command=self.export_data).pack(fill=tk.X, pady=2)
        ttk.Button(frame, text="View Data", command=self.view_data).pack(fill=tk.X, pady=2)
        
        self.export_status = ttk.Label(frame, text="Ready to export time values for survival rates", foreground="gold")
        self.export_status.pack(fill=tk.X, pady=5)
        
    def load_image(self):
        """Load a single image file"""
        file_path = filedialog.askopenfilename(
            title="Select Image File",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp")]
        )
        if file_path:
            self.load_image_file(file_path)
            
    def browse_folder(self):
        """Browse folder and show image selection dialog"""
        folder_path = filedialog.askdirectory(title="Select Folder with Images")
        if not folder_path:
            return
            
        # Get all image files
        image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp'}
        image_files = []
        
        for file_path in Path(folder_path).rglob('*'):
            if file_path.suffix.lower() in image_extensions:
                image_files.append(str(file_path))
                
        if not image_files:
            messagebox.showinfo("No Images", "No image files found in the selected folder.")
            return
            
        # Show selection dialog
        self.show_image_selection_dialog(image_files)
        
    def show_image_selection_dialog(self, image_files):
        """Show dialog to select image from list"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Select Image")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Select an image to process:").pack(pady=10)
        
        # Listbox with scrollbar
        frame = ttk.Frame(dialog)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        listbox = tk.Listbox(frame)
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=listbox.yview)
        listbox.configure(yscrollcommand=scrollbar.set)
        
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Populate listbox
        for file_path in image_files:
            listbox.insert(tk.END, Path(file_path).name)
            
        def on_select():
            selection = listbox.curselection()
            if selection:
                selected_file = image_files[selection[0]]
                self.load_image_file(selected_file)
                dialog.destroy()
                
        ttk.Button(dialog, text="Load Selected", command=on_select).pack(pady=10)
        
    def load_image_file(self, file_path):
        """Load and display image file"""
        try:
            self.current_image_path = file_path
            self.original_image = Image.open(file_path)
            
            # Reset calibration and data
            self.reset_calibration()
            self.selected_points.clear()
            
            # Display image
            self.display_image_on_canvas()
            
            # Update UI
            self.image_label.config(text=f"Loaded: {Path(file_path).name}")
            self.calibration_btn.config(state=tk.NORMAL)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image: {str(e)}")
            
    def display_image_on_canvas(self):
        """Display image on canvas with proper scaling"""
        if not self.original_image:
            return
            
        # Calculate scale factor to fit canvas
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            self.root.after(100, self.display_image_on_canvas)
            return
            
        img_width, img_height = self.original_image.size
        
        scale_x = (canvas_width - 50) / img_width
        scale_y = (canvas_height - 50) / img_height
        self.scale_factor = min(scale_x, scale_y, 1.0)  # Don't scale up
        
        # Resize image
        new_width = int(img_width * self.scale_factor)
        new_height = int(img_height * self.scale_factor)
        
        self.display_image = self.original_image.copy()
        self.add_overlays_to_image()
        
        resized_image = self.display_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        self.canvas_image = ImageTk.PhotoImage(resized_image)
        
        # Clear canvas and display image
        self.canvas.delete("all")
        self.canvas.create_image(25, 25, anchor=tk.NW, image=self.canvas_image)
        
        # Update canvas scroll region
        self.canvas.configure(scrollregion=(0, 0, new_width + 50, new_height + 50))
        
    def add_overlays_to_image(self):
        """Add calibration points, lines, and data points to image"""
        if not self.display_image:
            return
            
        draw = ImageDraw.Draw(self.display_image)
        
        # Draw calibration points
        for key, coord in self.axis_calibration.items():
            if coord and key.endswith('_coord'):
                x, y = coord
                # Draw cross marker
                size = 5
                draw.line([(x-size, y), (x+size, y)], fill='red', width=2)
                draw.line([(x, y-size), (x, y+size)], fill='red', width=2)
                
        # Draw survival rate lines if calibration is complete
        if self.is_calibration_complete():
            self.draw_survival_rate_lines(draw)
            
        # Draw selected data points (only those with coordinates)
        for key, point in self.selected_points.items():
            if point['x'] is not None and point['y'] is not None:
                x, y = point['x'], point['y']
                size = 4
                draw.ellipse([(x-size, y-size), (x+size, y+size)], fill='blue', outline='darkblue', width=2)
            
    def draw_survival_rate_lines(self, draw):
        """Draw horizontal lines for different survival rate levels"""
        x_min_coord = self.axis_calibration['x_min_coord'][0]
        x_max_coord = self.axis_calibration['x_max_coord'][0]
        y_min_coord = self.axis_calibration['y_min_coord'][1]
        y_max_coord = self.axis_calibration['y_max_coord'][1]
        
        # Draw horizontal lines for survival rate levels: 0%, 25%, 50%, 75%, 100%
        # Y-axis represents survival rate, so we split it into these levels
        for i, survival_rate in enumerate(self.survival_rates):
            percentage = float(survival_rate.replace('%', '')) / 100.0
            y_coord = y_min_coord + percentage * (y_max_coord - y_min_coord)
            draw.line([(x_min_coord, y_coord), (x_max_coord, y_coord)], fill='red', width=1)
            
    def on_canvas_click(self, event):
        """Handle canvas click events"""
        if not self.canvas_image:
            return
            
        # Convert canvas coordinates to image coordinates
        canvas_x = self.canvas.canvasx(event.x) - 25
        canvas_y = self.canvas.canvasy(event.y) - 25
        
        # Scale to original image coordinates
        img_x = canvas_x / self.scale_factor
        img_y = canvas_y / self.scale_factor
        
        # Check bounds
        if img_x < 0 or img_y < 0 or img_x >= self.original_image.width or img_y >= self.original_image.height:
            return
        
        # Check if clicking near a calibration point for potential dragging
        near_calibration_point = False
        for key, coord in self.axis_calibration.items():
            if coord and key.endswith('_coord'):
                x, y = coord
                distance = ((img_x - x) ** 2 + (img_y - y) ** 2) ** 0.5
                if distance < 15:  # Within 15 pixels
                    self.dragging_point = key
                    self.drag_offset_x = img_x - x
                    self.drag_offset_y = img_y - y
                    near_calibration_point = True
                    break
        
        # If not near a calibration point, handle normal click
        if not near_calibration_point:
            self.handle_image_click(img_x, img_y)
        
    def handle_image_click(self, x, y):
        """Handle clicks on the image"""
        if self.calibration_step < 4:
            # Calibration mode
            self.handle_calibration_click(x, y)
        else:
            # Data extraction mode
            self.handle_data_point_click(x, y)
            
    def handle_calibration_click(self, x, y):
        """Handle calibration point clicks"""
        if self.calibration_step >= 4:
            return
            
        # Show clicked point
        self.last_click = (x, y)
        self.display_image_on_canvas()
        
        # Enable calibration button
        self.calibration_btn.config(state=tk.NORMAL)
        self.calibration_status.config(text=f"Clicked at ({x:.1f}, {y:.1f}). Enter value and click 'Set Point'.")
        
        # Show zoom window
        self.show_zoom_window(x, y)
        
    def set_calibration_point(self):
        """Set calibration point with entered value"""
        if not hasattr(self, 'last_click'):
            messagebox.showwarning("No Click", "Please click on the image first.")
            return
            
        value_text = self.calibration_value.get().strip()
        if not value_text:
            messagebox.showwarning("No Value", "Please enter a value.")
            return
            
        try:
            value = float(value_text)
        except ValueError:
            messagebox.showerror("Invalid Value", "Please enter a valid number.")
            return
            
        x, y = self.last_click
        
        # Set calibration point based on current step
        if self.calibration_step == 0:
            self.axis_calibration['x_min'] = value
            self.axis_calibration['x_min_coord'] = (x, y)
            self.calibration_step = 1
            next_instruction = "Click on X-axis maximum point"
        elif self.calibration_step == 1:
            self.axis_calibration['x_max'] = value
            self.axis_calibration['x_max_coord'] = (x, y)
            self.calibration_step = 2
            next_instruction = "Click on Y-axis minimum point"
        elif self.calibration_step == 2:
            self.axis_calibration['y_min'] = value
            self.axis_calibration['y_min_coord'] = (x, y)
            self.calibration_step = 3
            next_instruction = "Click on Y-axis maximum point"
        elif self.calibration_step == 3:
            self.axis_calibration['y_max'] = value
            self.axis_calibration['y_max_coord'] = (x, y)
            self.calibration_step = 4
            next_instruction = "Calibration complete! Set groups to start extracting data."
            
        # Clear input and update UI
        self.calibration_value.delete(0, tk.END)
        self.calibration_status.config(text=next_instruction)
        
        if self.calibration_step >= 4:
            self.calibration_btn.config(state=tk.DISABLED)
            
        # Refresh display
        self.display_image_on_canvas()
        
    def reset_calibration(self):
        """Reset calibration data"""
        self.axis_calibration = {
            'x_min': None, 'x_max': None, 'y_min': None, 'y_max': None,
            'x_min_coord': None, 'x_max_coord': None, 'y_min_coord': None, 'y_max_coord': None
        }
        self.calibration_step = 0
        self.calibration_status.config(text="Click on X-axis minimum point")
        
        if hasattr(self, 'last_click'):
            delattr(self, 'last_click')
            
        if self.original_image:
            self.display_image_on_canvas()
            
    def is_calibration_complete(self):
        """Check if calibration is complete"""
        return all(v is not None for v in self.axis_calibration.values())
        
    def handle_data_point_click(self, x, y):
        """Handle data point selection clicks"""
        if not self.is_calibration_complete():
            messagebox.showwarning("Calibration Required", "Please complete axis calibration first.")
            return
            
        if not self.groups:
            messagebox.showwarning("Groups Required", "Please set groups first.")
            return
        
        # Check if a point is selected in the table
        if not self.selected_point_key:
            messagebox.showwarning("Point Selection Required", "Please select a point in the table first, then click on the image.")
            return
            
        # Store the data point for the selected table entry
        self.selected_points[self.selected_point_key] = {'x': x, 'y': y}
        
        # Calculate real coordinates
        real_x, real_y = self.get_real_coordinates(x, y)
        
        # Parse group and survival rate from key
        group, survival_rate = self.selected_point_key.split('_', 1)
        
        # Update status
        if hasattr(self, 'calibration_status'):
            self.calibration_status.config(text=f"Point set for {group} at {survival_rate} survival: Time={real_x:.2f}")
        
        # Update the points tree view
        self.update_points_tree()
        
        # Refresh display
        self.display_image_on_canvas()
        
    def get_real_coordinates(self, pixel_x, pixel_y):
        """Convert pixel coordinates to real axis values"""
        if not self.is_calibration_complete():
            return None, None
            
        x_min_val, x_max_val = self.axis_calibration['x_min'], self.axis_calibration['x_max']
        y_min_val, y_max_val = self.axis_calibration['y_min'], self.axis_calibration['y_max']
        x_min_coord, x_max_coord = self.axis_calibration['x_min_coord'][0], self.axis_calibration['x_max_coord'][0]
        y_min_coord, y_max_coord = self.axis_calibration['y_min_coord'][1], self.axis_calibration['y_max_coord'][1]
        
        # Calculate real coordinates
        real_x = x_min_val + (pixel_x - x_min_coord) * (x_max_val - x_min_val) / (x_max_coord - x_min_coord)
        real_y = y_min_val + (y_max_coord - pixel_y) * (y_max_val - y_min_val) / (y_max_coord - y_min_coord)
        
        return real_x, real_y
        
    def show_survival_rate_lines(self):
        """Show survival rate lines on the image"""
        if not self.is_calibration_complete():
            messagebox.showwarning("Calibration Required", "Please complete axis calibration first.")
            return
            
        self.display_image_on_canvas()
        
    def export_data(self):
        """Export data to JSON file"""
        if not self.current_image_path:
            messagebox.showwarning("No Image", "Please load an image first.")
            return
            
        if not self.selected_points:
            messagebox.showwarning("No Data", "No data points selected.")
            return
            
        # Get current units
        self.x_axis_units = self.x_units_entry.get().strip() or self.x_axis_units
        self.y_axis_units = self.y_units_entry.get().strip() or self.y_axis_units
        
        # Prepare data structure - time values for each survival rate level
        data_dict = {}
        for survival_rate in self.survival_rates:
            data_dict[survival_rate] = {}
            for group in self.groups:
                key = f"{group}_{survival_rate}"
                if key in self.selected_points:
                    point = self.selected_points[key]
                    # Only convert coordinates if the point has been set
                    if point['x'] is not None and point['y'] is not None:
                        real_x, real_y = self.get_real_coordinates(point['x'], point['y'])
                        data_dict[survival_rate][group] = real_x if real_x is not None else None
                    else:
                        # Point exists but hasn't been set yet
                        data_dict[survival_rate][group] = None
                else:
                    data_dict[survival_rate][group] = None
        
        # Include units and metadata in export structure
        result = {
            'metadata': {
                'x_axis_type': self.x_axis_type,
                'y_axis_type': self.y_axis_type,
                'x_axis_units': self.x_axis_units,
                'y_axis_units': self.y_axis_units,
                'image_file': Path(self.current_image_path).name
            },
            'data': data_dict
        }
                    
        # Generate filename
        image_name = Path(self.current_image_path).stem
        output_filename = f"{image_name}_extracted_survival_time_points.json"
        output_path = Path(self.current_image_path).parent / output_filename
        
        # Save JSON
        try:
            with open(output_path, 'w') as f:
                json.dump(result, f, indent=2)
            
            self.export_status.config(text=f"Exported to: {output_filename}")
            messagebox.showinfo("Export Complete", f"Data exported to:\n{output_path}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export data: {str(e)}")
            
    def view_data(self):
        """View current data in a popup window"""
        if not self.selected_points:
            messagebox.showinfo("No Data", "No data points selected yet.")
            return
            
        # Create data view window
        window = tk.Toplevel(self.root)
        window.title("Current Data")
        window.geometry("600x400")
        window.transient(self.root)
        
        # Create text widget with scrollbar
        text_frame = ttk.Frame(window)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        text_widget = tk.Text(text_frame, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Generate data display
        output = "Current Data Points (Time values at survival rate levels):\\n\\n"
        
        for survival_rate in self.survival_rates:
            output += f"Survival Rate {survival_rate}:\\n"
            for group in self.groups:
                key = f"{group}_{survival_rate}"
                if key in self.selected_points:
                    point = self.selected_points[key]
                    # Only convert coordinates if the point has been set
                    if point['x'] is not None and point['y'] is not None:
                        real_x, real_y = self.get_real_coordinates(point['x'], point['y'])
                        if real_x is not None:
                            output += f"  {group}: Time = {real_x:.2f}\\n"
                        else:
                            output += f"  {group}: Error in calculation\\n"
                    else:
                        output += f"  {group}: Not set\\n"
                else:
                    output += f"  {group}: Not set\\n"
            output += "\\n"
            
        text_widget.insert(tk.END, output)
        text_widget.config(state=tk.DISABLED)
        
    def on_axis_type_change(self, event=None):
        """Handle axis type change"""
        selected_x = self.x_axis_var.get()
        if selected_x == 'time':
            self.x_axis_type = 'time'
            self.y_axis_type = 'survival'
            self.y_axis_label.config(text='survival')
        else:
            self.x_axis_type = 'survival'
            self.y_axis_type = 'time'
            self.y_axis_label.config(text='time')
            
        # Reset calibration when axis types change
        self.reset_calibration()
        
    def show_zoom_window(self, center_x, center_y):
        """Show zoom window for precise calibration"""
        if not self.original_image:
            return
            
        # Create or update zoom window
        if not self.zoom_window or not self.zoom_window.winfo_exists():
            self.zoom_window = tk.Toplevel(self.root)
            self.zoom_window.title("Zoom View")
            self.zoom_window.geometry(f"{self.zoom_size*2}x{self.zoom_size*2}")
            self.zoom_window.resizable(False, False)
            
            # Position in top right corner of main window
            main_x = self.root.winfo_x()
            main_y = self.root.winfo_y()
            main_width = self.root.winfo_width()
            self.zoom_window.geometry(f"+{main_x + main_width - 250}+{main_y + 50}")
            
            self.zoom_canvas = tk.Canvas(self.zoom_window, width=self.zoom_size*2, height=self.zoom_size*2, bg='white')
            self.zoom_canvas.pack()
            
        # Create zoomed image
        img_width, img_height = self.original_image.size
        
        # Calculate crop area
        crop_size = self.zoom_size // self.zoom_factor
        left = max(0, int(center_x - crop_size // 2))
        top = max(0, int(center_y - crop_size // 2))
        right = min(img_width, int(center_x + crop_size // 2))
        bottom = min(img_height, int(center_y + crop_size // 2))
        
        # Crop and zoom
        cropped = self.original_image.crop((left, top, right, bottom))
        zoomed = cropped.resize((self.zoom_size*2, self.zoom_size*2), Image.Resampling.NEAREST)
        
        # Draw crosshairs at center
        draw = ImageDraw.Draw(zoomed)
        center = self.zoom_size
        draw.line([(center-10, center), (center+10, center)], fill='red', width=2)
        draw.line([(center, center-10), (center, center+10)], fill='red', width=2)
        
        # Display zoomed image
        self.zoom_photo = ImageTk.PhotoImage(zoomed)
        self.zoom_canvas.delete("all")
        self.zoom_canvas.create_image(0, 0, anchor=tk.NW, image=self.zoom_photo)
        
    def on_canvas_motion(self, event):
        """Handle mouse motion for continuous zoom"""
        if not self.canvas_image or not self.zoom_enabled.get():
            return
            
        # Convert canvas coordinates to image coordinates
        canvas_x = self.canvas.canvasx(event.x) - 25
        canvas_y = self.canvas.canvasy(event.y) - 25
        
        # Scale to original image coordinates
        img_x = canvas_x / self.scale_factor
        img_y = canvas_y / self.scale_factor
        
        # Check bounds
        if img_x < 0 or img_y < 0 or img_x >= self.original_image.width or img_y >= self.original_image.height:
            return
            
        # Show zoom window
        self.show_zoom_window(img_x, img_y)
        
    def on_canvas_drag(self, event):
        """Handle mouse drag for moving calibration points"""
        if not self.dragging_point:
            return
            
        # Convert to image coordinates
        canvas_x = self.canvas.canvasx(event.x) - 25
        canvas_y = self.canvas.canvasy(event.y) - 25
        img_x = canvas_x / self.scale_factor
        img_y = canvas_y / self.scale_factor
        
        # Update calibration point position
        new_x = img_x - self.drag_offset_x
        new_y = img_y - self.drag_offset_y
        
        # Keep within bounds
        new_x = max(0, min(new_x, self.original_image.width))
        new_y = max(0, min(new_y, self.original_image.height))
        
        self.axis_calibration[self.dragging_point] = (new_x, new_y)
        
        # Refresh display
        self.display_image_on_canvas()
        
    def on_canvas_release(self, event):
        """Handle mouse button release"""
        self.dragging_point = None
        
    def on_zoom_toggle(self):
        """Handle zoom enable/disable toggle"""
        if not self.zoom_enabled.get():
            # Close zoom window if it exists
            if self.zoom_window and self.zoom_window.winfo_exists():
                self.zoom_window.destroy()
                self.zoom_window = None
        
    def update_points_tree(self):
        """Update the points tree view with current data"""
        # Only update if tree exists
        if not hasattr(self, 'points_tree'):
            return
            
        # Clear existing items
        for item in self.points_tree.get_children():
            self.points_tree.delete(item)
            
        # Add current points (including placeholders)
        for key, point in self.selected_points.items():
            group, survival_rate = key.split('_', 1)
            
            # Handle both set points and placeholder points
            if point['x'] is not None and point['y'] is not None:
                real_x, real_y = self.get_real_coordinates(point['x'], point['y'])
                time_value = f"{real_x:.2f}" if real_x is not None else "N/A"
            else:
                time_value = "N/A"
            
            self.points_tree.insert('', 'end', values=(
                group,
                survival_rate,
                time_value
            ))
            
    
    def on_treeview_edit(self, event):
        """Handle double-click on treeview item to edit time value"""
        item = self.points_tree.selection()
        if not item:
            return
            
        # Get the values of the clicked item
        values = self.points_tree.item(item[0])['values']
        if not values:
            return
            
        group, survival_rate, current_time = values[0], values[1], values[2]
        key = f"{group}_{survival_rate}"
        
        # Show input dialog for new time value
        new_time = simpledialog.askfloat(
            "Edit Time Value",
            f"Edit time value for {group} - {survival_rate}:",
            initialvalue=float(current_time) if current_time != "N/A" else 0.0,
            minvalue=0.0
        )
        
        if new_time is not None:
            # Update the point's coordinates based on new time value
            if key in self.selected_points and self.is_calibration_complete():
                # Get calibration coordinates (they are tuples)
                x_min_coord = self.axis_calibration['x_min_coord'][0]  # x coordinate of min point
                x_max_coord = self.axis_calibration['x_max_coord'][0]  # x coordinate of max point
                x_min_val = self.axis_calibration['x_min']
                x_max_val = self.axis_calibration['x_max']
                
                # Calculate new pixel x position
                x_range = x_max_val - x_min_val
                if x_range != 0:
                    time_ratio = (new_time - x_min_val) / x_range
                    pixel_x_range = x_max_coord - x_min_coord
                    new_pixel_x = x_min_coord + (time_ratio * pixel_x_range)
                    
                    # Keep the same y coordinate (survival rate doesn't change)
                    current_y = self.selected_points[key]['y'] if self.selected_points[key]['y'] is not None else 0
                    
                    # Update the point
                    self.selected_points[key] = {'x': new_pixel_x, 'y': current_y}
                    
                    # Update display
                    self.update_points_tree()
                    self.display_image_on_canvas()
                        
    def on_treeview_delete(self, event):
        """Handle Delete/Backspace key to remove selected points"""
        selection = self.points_tree.selection()
        if not selection:
            return
            
        # Confirm deletion
        if len(selection) == 1:
            values = self.points_tree.item(selection[0])['values']
            group, survival_rate = values[0], values[1]
            if not messagebox.askyesno("Delete Point", f"Delete {group} - {survival_rate} point?"):
                return
        else:
            if not messagebox.askyesno("Delete Points", f"Delete {len(selection)} selected points?"):
                return
        
        # Reset selected points to placeholder state (don't delete completely)
        for item in selection:
            values = self.points_tree.item(item)['values']
            group, survival_rate = values[0], values[1]
            key = f"{group}_{survival_rate}"
            
            if key in self.selected_points:
                # Reset to placeholder instead of deleting
                self.selected_points[key] = {'x': None, 'y': None}
        
        # Update display
        self.update_points_tree()
        self.display_image_on_canvas()
    
    def on_treeview_select(self, event):
        """Handle table row selection to set active point for clicking"""
        selection = self.points_tree.selection()
        if selection:
            values = self.points_tree.item(selection[0])['values']
            if len(values) >= 2:  # Make sure we have group and survival rate
                group, survival_rate = values[0], values[1]
                self.selected_point_key = f"{group}_{survival_rate}"
                
                # Update status to show which point is selected for clicking
                if hasattr(self, 'calibration_status'):
                    self.calibration_status.config(text=f"Selected: {group} - {survival_rate}. Click on image to set point.")
        else:
            self.selected_point_key = None
            # Reset status when no selection
            if hasattr(self, 'calibration_status'):
                self.calibration_status.config(text="Select a point in the table below, then click on the image to set its position")
            
    def add_group_field(self):
        """Add a new group input field"""
        group_frame = ttk.Frame(self.groups_scrollable_frame)
        group_frame.pack(fill=tk.X, pady=2)
        
        # Group number label (auto-size)
        group_num = len(self.group_entries) + 1
        label = ttk.Label(group_frame, text=f"Group {group_num}:")
        label.pack(side=tk.LEFT, padx=(0, 5))
        
        # Group name entry (auto-resizable)
        entry = ttk.Entry(group_frame)
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        entry.bind('<KeyRelease>', lambda e: self.update_groups())
        
        # Delete button
        delete_btn = ttk.Button(group_frame, text="×", width=2, 
                               command=lambda: self.remove_group_field(group_frame, entry))
        delete_btn.pack(side=tk.LEFT)
        
        # Store reference
        self.group_entries.append({'frame': group_frame, 'entry': entry, 'label': label})
        
        # Update scroll region
        self.groups_scrollable_frame.update_idletasks()
        self.groups_canvas.configure(scrollregion=self.groups_canvas.bbox("all"))
        
        # Set default names for first few groups
        defaults = ['WT', 'KO', 'HT', 'Control', 'Treatment']
        if group_num <= len(defaults):
            entry.insert(0, defaults[group_num - 1])
            
        # Auto-update groups
        self.update_groups()
            
    def remove_group_field(self, frame, entry):
        """Remove a group input field"""
        # Remove from list
        self.group_entries = [g for g in self.group_entries if g['frame'] != frame]
        
        # Destroy the frame
        frame.destroy()
        
        # Update group numbers
        for i, group_data in enumerate(self.group_entries):
            group_data['label'].config(text=f"Group {i + 1}:")
        
        # Update scroll region and groups
        self.groups_scrollable_frame.update_idletasks()
        self.groups_canvas.configure(scrollregion=self.groups_canvas.bbox("all"))
        self.update_groups()
        
    def update_groups(self):
        """Update groups from all entry fields"""
        self.groups = []
        for group_data in self.group_entries:
            group_name = group_data['entry'].get().strip()
            if group_name:
                self.groups.append(group_name)
        
        # Groups are now displayed directly in the input fields and table
        
        # Populate all possible points in the table when groups change
        self.populate_all_points()
        
        # Update points tree view if it exists
        if hasattr(self, 'points_tree'):
            self.update_points_tree()
            
            # Auto-select the first row if points exist and no point is currently selected
            if self.selected_points and not self.selected_point_key:
                first_item = self.points_tree.get_children()
                if first_item:
                    self.points_tree.selection_set(first_item[0])
                    self.points_tree.focus(first_item[0])
    
    def populate_all_points(self):
        """Create entries for all group-survival rate combinations and clean up removed groups"""
        # First, remove points for groups that no longer exist
        current_group_names = set(self.groups)
        keys_to_remove = []
        
        for key in list(self.selected_points.keys()):
            # Split key to get group name (everything before the last underscore which is the survival rate)
            parts = key.split('_')
            if len(parts) >= 2:
                group_name = '_'.join(parts[:-1])  # Handle group names that might contain underscores
                if group_name not in current_group_names:
                    keys_to_remove.append(key)
        
        # Remove points for deleted groups
        for key in keys_to_remove:
            del self.selected_points[key]
        
        if not self.groups:
            return
            
        # Create placeholder entries for all combinations that don't exist
        for group in self.groups:
            for survival_rate in self.survival_rates:
                key = f"{group}_{survival_rate}"
                if key not in self.selected_points:
                    # Add placeholder point with no coordinates (will show as "N/A")
                    self.selected_points[key] = {'x': None, 'y': None}
        
    def clear_all_groups(self):
        """Clear all group fields"""
        if messagebox.askyesno("Clear All Groups", "Are you sure you want to clear all groups?"):
            # Clear all entries except the first one
            while len(self.group_entries) > 1:
                last_group = self.group_entries[-1]
                self.remove_group_field(last_group['frame'], last_group['entry'])
            
            # Clear the remaining entry
            if self.group_entries:
                self.group_entries[0]['entry'].delete(0, tk.END)
                
            self.update_groups()
            
    def run(self):
        """Start the application"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
        
    def on_closing(self):
        """Handle application closing"""
        if self.zoom_window:
            self.zoom_window.destroy()
        self.root.destroy()


if __name__ == "__main__":
    app = SurvivalCurveExtractor()
    app.run()