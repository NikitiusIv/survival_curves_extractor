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
        
        # Navigation system for dataset
        self.dataset_path = None
        self.image_files = []
        self.filtered_image_files = None  # For filtering incomplete images
        self.current_index = 0
        self.metadata_cache = {}
        # Removed metadata_groups fallback - now only use current image's data
        self.auto_save_enabled = True
        self.ui_refreshing = False  # Flag to prevent auto-population during UI refresh
        self.loading_in_progress = False  # Flag to prevent auto-save during data loading
        self.user_modified_data = False  # Flag to track if user made changes since last load
        
        # Configure UI theme and colors
        self.configure_theme()
        
        # UI setup
        self.setup_ui()
        
        # Initialize description
        self.update_image_description("Select a dataset to begin image annotation.")
        
        # Initially hide scrollbars and set sash position
        self.root.after(100, self.initial_layout_adjustments)
        
        # Bind window focus events to maintain button styling on macOS
        self.root.bind('<FocusIn>', lambda e: self.root.after(10, self.maintain_button_styling))
        self.root.bind('<FocusOut>', lambda e: self.root.after(10, self.maintain_button_styling))
        self.root.bind('<Activate>', lambda e: self.root.after(10, self.maintain_button_styling))
        self.root.bind('<Deactivate>', lambda e: self.root.after(10, self.maintain_button_styling))
    
    def configure_theme(self):
        """Configure consistent theme and colors across platforms"""
        import platform
        
        # Define color scheme
        self.colors = {
            'bg': '#2b2b2b',           # Dark gray background
            'bg_dark': '#1e1e1e',      # Darker gray
            'canvas_bg': 'white',      # Canvas background (keep white for image)
            'text': '#ffffff',         # White text color
            'select_bg': '#0078d4',    # Selection background
            'select_fg': 'white',      # Selection text
            'button_bg': '#3c3c3c',    # Button background
            'entry_bg': '#3c3c3c',     # Entry background (dark for theme consistency)
            'frame_bg': '#2b2b2b'      # Frame background
        }
        
        # Configure root window
        self.root.configure(bg=self.colors['bg'])
        
        # Configure ttk style for consistent appearance
        style = ttk.Style()
        
        # Set theme based on platform
        if platform.system() == 'Windows':
            try:
                style.theme_use('winnative')
            except:
                style.theme_use('default')
        elif platform.system() == 'Darwin':
            try:
                style.theme_use('aqua')
            except:
                style.theme_use('default')
        else:
            style.theme_use('default')
        
        # Configure specific widget styles
        style.configure('TFrame', background=self.colors['bg'])
        style.configure('TLabelFrame', background=self.colors['bg'], foreground=self.colors['text'])
        style.configure('TLabelFrame.Label', background=self.colors['bg'], foreground=self.colors['text'])
        style.configure('TLabel', background=self.colors['bg'], foreground=self.colors['text'])
        style.configure('TButton', background=self.colors['button_bg'], foreground=self.colors['text'])
        style.configure('TEntry', fieldbackground='#3c3c3c', foreground='white')
        style.configure('TText', fieldbackground='#3c3c3c', foreground='white')
        
        # Configure Treeview
        style.configure('Treeview', background='#3c3c3c', 
                       foreground='white',
                       fieldbackground='#3c3c3c')
        style.configure('Treeview.Heading', background=self.colors['bg_dark'], foreground=self.colors['text'])
        style.map('Treeview', background=[('selected', self.colors['select_bg'])],
                  foreground=[('selected', self.colors['select_fg'])])
    
    def create_button(self, parent, text, command=None, width=None, state=None):
        """Create a styled button with consistent dark theme"""
        import platform
        
        if platform.system() == 'Darwin':  # macOS - use Frame-based button
            # Create a frame that looks like a button for macOS
            btn_frame = tk.Frame(parent, bg=self.colors['button_bg'], relief=tk.RAISED, bd=1)
            
            # Create label inside frame
            btn_label = tk.Label(btn_frame, text=text, 
                               bg=self.colors['button_bg'], fg=self.colors['text'],
                               font=('Arial', 11, 'normal'),
                               cursor='hand2')
            btn_label.pack(expand=True, fill=tk.BOTH, padx=6, pady=4)
            
            # Store the command and other properties
            btn_frame.command = command
            btn_frame.btn_label = btn_label
            btn_frame.is_enabled = True  # Track button state
            
            # Add click behavior
            def on_click(event):
                if btn_frame.winfo_exists() and getattr(btn_frame, 'is_enabled', True):
                    # Visual feedback
                    btn_frame.configure(relief=tk.SUNKEN)
                    btn_label.config(bg='#4a4a4a')
                    btn_frame.after(100, lambda: (
                        btn_frame.configure(relief=tk.RAISED),
                        btn_label.config(bg=self.colors['button_bg'])
                    ) if btn_frame.winfo_exists() else None)
                    # Execute command if provided
                    if command:
                        try:
                            command()
                        except Exception as e:
                            print(f"Button command error: {e}")
            
            def on_enter(event):
                if btn_frame.winfo_exists() and getattr(btn_frame, 'is_enabled', True):
                    btn_label.config(bg='#4a4a4a')
                    
            def on_leave(event):
                if btn_frame.winfo_exists() and getattr(btn_frame, 'is_enabled', True):
                    btn_label.config(bg=self.colors['button_bg'])
            
            # Bind events to both frame and label for better reliability
            for widget in [btn_frame, btn_label]:
                widget.bind('<Button-1>', on_click)
                widget.bind('<Enter>', on_enter)
                widget.bind('<Leave>', on_leave)
                widget.bind('<ButtonRelease-1>', lambda e: None)  # Consume event
            
            # Add simple config method to mimic tk.Button API
            def config_method(**kwargs):
                if 'state' in kwargs:
                    if kwargs['state'] == tk.DISABLED:
                        btn_frame.is_enabled = False
                        btn_label.config(fg='#666666', cursor='')
                        btn_frame.configure(bg='#2a2a2a')
                        btn_label.config(bg='#2a2a2a')
                    else:  # NORMAL or other enabled state
                        btn_frame.is_enabled = True
                        btn_label.config(fg=self.colors['text'], cursor='hand2')
                        btn_frame.configure(bg=self.colors['button_bg'])
                        btn_label.config(bg=self.colors['button_bg'])
                if 'text' in kwargs:
                    btn_label.config(text=kwargs['text'])
                    
            btn_frame.config = config_method
            
            if width:
                btn_frame.configure(width=width * 8)  # Approximate character width
            if state == tk.DISABLED:
                btn_frame.config(state=tk.DISABLED)
            else:
                # Ensure button starts in enabled state
                btn_frame.is_enabled = True
                
            return btn_frame
            
        else:  # Windows and Linux - use regular tk.Button
            btn = tk.Button(parent, text=text, command=command,
                           bg=self.colors['button_bg'], fg=self.colors['text'],
                           activebackground='#4a4a4a', activeforeground='white',
                           relief=tk.RAISED, bd=1,
                           highlightthickness=0,
                           font=('Arial', 11))
            
            if width:
                btn.config(width=width)
            if state:
                btn.config(state=state)
                
            return btn
    
    def maintain_button_styling(self):
        """Maintain button styling across all buttons (mainly for Windows/Linux)"""
        import platform
        if platform.system() != 'Darwin':  # Only needed for non-macOS
            def apply_to_buttons(widget):
                try:
                    for child in widget.winfo_children():
                        if isinstance(child, tk.Button):
                            child.config(
                                bg=self.colors['button_bg'], 
                                fg=self.colors['text'],
                                activebackground='#4a4a4a', 
                                activeforeground='white',
                                highlightbackground=self.colors['button_bg']
                            )
                        apply_to_buttons(child)
                except:
                    pass
            apply_to_buttons(self.root)
        
    def setup_ui(self):
        """Setup the user interface"""
        # Main container
        container = ttk.Frame(self.root)
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Navigation bar at the top
        self.setup_navigation_bar(container)
        
        # Main frame with paned window for resizable columns
        main_frame = ttk.Frame(container)
        main_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Create horizontal paned window (resizable columns)
        paned_window = tk.PanedWindow(main_frame, orient=tk.HORIZONTAL, sashrelief=tk.RAISED, sashwidth=5)
        paned_window.pack(fill=tk.BOTH, expand=True)
        
        # Left panel for controls with scrolling
        control_container = ttk.Frame(paned_window)
        
        # Create scrollable canvas for controls
        control_canvas = tk.Canvas(control_container, highlightthickness=0, bg=self.colors['bg'])
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
        paned_window.add(control_container, minsize=250, width=320)
        paned_window.add(self.image_frame, minsize=400)
        
        # Store reference to paned window for later adjustment
        self.paned_window = paned_window
        
        # Setup control sections
        self.setup_calibration_controls(control_panel)
        self.setup_groups_controls(control_panel)
        self.setup_extraction_controls(control_panel)
        self.setup_export_controls(control_panel)
        
        # Create image display area with description
        image_container = ttk.Frame(self.image_frame)
        image_container.pack(fill=tk.BOTH, expand=True)
        
        # Create main canvas area with grid layout for scrollbars
        canvas_area = ttk.Frame(image_container)
        canvas_area.pack(fill=tk.BOTH, expand=True)
        
        # Configure grid weights
        canvas_area.grid_rowconfigure(0, weight=1)
        canvas_area.grid_columnconfigure(0, weight=1)
        
        # Setup image canvas in grid position (0,0)
        self.canvas = tk.Canvas(canvas_area, bg=self.colors['canvas_bg'])
        self.canvas.grid(row=0, column=0, sticky="nsew")
        
        # Create scrollbars in grid positions
        self.v_scrollbar = ttk.Scrollbar(canvas_area, orient=tk.VERTICAL, command=self.canvas.yview)
        self.h_scrollbar = ttk.Scrollbar(canvas_area, orient=tk.HORIZONTAL, command=self.canvas.xview)
        
        # Configure canvas to use scrollbars
        self.canvas.configure(yscrollcommand=self.v_scrollbar.set)
        self.canvas.configure(xscrollcommand=self.h_scrollbar.set)
        
        # Setup zoom and pan controls in top-right
        self.setup_zoom_pan_controls(canvas_area)
        self.canvas.bind('<Button-1>', self.on_canvas_click)
        self.canvas.bind('<Motion>', self.on_canvas_motion)
        self.canvas.bind('<B1-Motion>', self.on_canvas_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_canvas_release)
        
        # Add mouse wheel zoom
        self.canvas.bind('<MouseWheel>', self.on_mouse_wheel)
        self.canvas.bind('<Button-4>', self.on_mouse_wheel)  # Linux
        self.canvas.bind('<Button-5>', self.on_mouse_wheel)  # Linux
        
        # Handle canvas resize to update scrollbars
        self.canvas.bind('<Configure>', self.on_canvas_configure)
        
        # Image description panel at the bottom
        self.setup_description_panel(self.image_frame)
        
    def setup_navigation_bar(self, parent):
        """Setup navigation bar for dataset browsing"""
        nav_frame = ttk.Frame(parent)
        nav_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Dataset path selection
        dataset_frame = ttk.Frame(nav_frame)
        dataset_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Label(dataset_frame, text="Dataset:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.create_button(dataset_frame, text="Select Dataset Folder", command=self.select_dataset).pack(side=tk.LEFT, padx=(0, 10))
        
        self.dataset_label = ttk.Label(dataset_frame, text="No dataset selected", foreground="#999999")
        self.dataset_label.pack(side=tk.LEFT, padx=(0, 20))
        
        # Navigation controls
        nav_controls = ttk.Frame(nav_frame)
        nav_controls.pack(side=tk.RIGHT)
        
        # Progress and filter controls
        progress_frame = ttk.Frame(nav_controls)
        progress_frame.pack(side=tk.LEFT, padx=(0, 10))
        
        self.progress_label = ttk.Label(progress_frame, text="Progress: 0/0 (0%)")
        self.progress_label.pack(side=tk.TOP)
        
        # Only incomplete checkbox
        self.only_incomplete_var = tk.BooleanVar()
        self.only_incomplete_check = ttk.Checkbutton(
            progress_frame, text="Only incomplete", 
            variable=self.only_incomplete_var,
            command=self.apply_incomplete_filter
        )
        self.only_incomplete_check.pack(side=tk.TOP)
        
        # Navigation buttons
        nav_buttons = ttk.Frame(nav_controls)
        nav_buttons.pack(side=tk.LEFT, padx=(10, 0))
        
        self.prev_btn = self.create_button(nav_buttons, text="◀ Previous", command=self.prev_image, state=tk.DISABLED)
        self.prev_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.image_counter_label = ttk.Label(nav_buttons, text="0 of 0 ○")
        self.image_counter_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.next_btn = self.create_button(nav_buttons, text="Next ▶", command=self.next_image, state=tk.DISABLED)
        self.next_btn.pack(side=tk.LEFT)
        
        # Current file display
        self.current_file_label = ttk.Label(nav_frame, text="", foreground="#ffd700")
        self.current_file_label.pack(side=tk.LEFT, padx=(20, 0))
        
    def setup_description_panel(self, parent):
        """Setup image description panel"""
        desc_frame = ttk.LabelFrame(parent, text="Image Description", padding=5)
        desc_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(5, 0))
        
        # Create scrollable text widget for description
        desc_container = ttk.Frame(desc_frame)
        desc_container.pack(fill=tk.BOTH, expand=True)
        
        # Text widget with scrollbar
        self.description_text = tk.Text(desc_container, height=5, wrap=tk.WORD, 
                                       bg='#3c3c3c', fg='#ffffff', font=('Arial', 11),
                                       state=tk.DISABLED)
        self.description_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        desc_scrollbar = ttk.Scrollbar(desc_container, orient=tk.VERTICAL, 
                                      command=self.description_text.yview)
        desc_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.description_text.configure(yscrollcommand=desc_scrollbar.set)
    
    def setup_zoom_pan_controls(self, parent):
        """Setup simple zoom controls in bottom-right corner"""
        # Initialize zoom level
        self.zoom_level = 1.0
        
        # Create zoom control frame in bottom-right
        self.zoom_frame = ttk.Frame(parent, relief='raised', borderwidth=1)
        self.zoom_frame.place(relx=1.0, rely=1.0, anchor='se', x=-10, y=-10)
        
        # Zoom out button
        self.zoom_out_btn = ttk.Button(self.zoom_frame, text="−", width=3,
                                     command=self.zoom_out)
        self.zoom_out_btn.pack(side=tk.LEFT, padx=2)
        
        # Zoom label
        self.zoom_label = ttk.Label(self.zoom_frame, text="100%", font=('Arial', 10), width=5)
        self.zoom_label.pack(side=tk.LEFT, padx=5)
        
        # Zoom in button
        self.zoom_in_btn = ttk.Button(self.zoom_frame, text="+", width=3,
                                    command=self.zoom_in)
        self.zoom_in_btn.pack(side=tk.LEFT, padx=2)
        
        # Reset zoom button
        self.reset_btn = ttk.Button(self.zoom_frame, text="Reset", width=6,
                                  command=self.reset_zoom)
        self.reset_btn.pack(side=tk.LEFT, padx=(5, 2))
    
    
    def update_image_description(self, description):
        """Update the image description text"""
        if hasattr(self, 'description_text'):
            self.description_text.config(state=tk.NORMAL)
            self.description_text.delete(1.0, tk.END)
            if description:
                self.description_text.insert(1.0, description)
            else:
                self.description_text.insert(1.0, "No description available for this image.")
            self.description_text.config(state=tk.DISABLED)
        
        
    def setup_calibration_controls(self, parent):
        """Setup axis calibration controls"""
        frame = ttk.LabelFrame(parent, text="1. Calibrate Axes", padding=5)
        frame.pack(fill=tk.X, pady=(0, 10))
        
        self.calibration_status = ttk.Label(frame, text="Click on X-axis minimum point", foreground="gold")
        self.calibration_status.pack(fill=tk.X, pady=5)
        
        input_frame = ttk.Frame(frame)
        input_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(input_frame, text="Value:").pack(side=tk.LEFT)
        self.calibration_value = ttk.Entry(input_frame)
        self.calibration_value.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 5))
        
        self.calibration_btn = self.create_button(input_frame, text="Set", width=3, command=self.set_calibration_point, state=tk.DISABLED)
        self.calibration_btn.pack(side=tk.LEFT)
        
        self.create_button(frame, text="Reset Calibration", command=self.reset_calibration).pack(fill=tk.X, pady=2)
        
        
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
        self.x_units_entry.bind('<KeyRelease>', self.on_units_change)
        self.x_units_entry.bind('<FocusOut>', self.on_units_change)
        
        # Y-axis units (auto-resizable)
        y_units_frame = ttk.Frame(units_frame)
        y_units_frame.pack(fill=tk.X)
        ttk.Label(y_units_frame, text="Y-axis units:").pack(side=tk.LEFT)
        self.y_units_entry = ttk.Entry(y_units_frame)
        self.y_units_entry.insert(0, self.y_axis_units)
        self.y_units_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        self.y_units_entry.bind('<KeyRelease>', self.on_units_change)
        self.y_units_entry.bind('<FocusOut>', self.on_units_change)
        
    def setup_groups_controls(self, parent):
        """Setup group management controls"""
        frame = ttk.LabelFrame(parent, text="2. Set Groups", padding=5)
        frame.pack(fill=tk.X, pady=(0, 10))
        
        # Button to add new group
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=3)
        
        self.create_button(button_frame, text="+", width=2, command=self.add_group_field).pack(side=tk.LEFT, padx=(0, 1))
        self.create_button(button_frame, text="Upd", width=3, command=self.update_groups).pack(side=tk.LEFT, padx=1)
        self.create_button(button_frame, text="Clr", width=3, command=self.clear_all_groups).pack(side=tk.LEFT, padx=1)
        
        self.groups_parent = frame.master
        
        # Scrollable frame for group entries
        self.groups_canvas = tk.Canvas(frame, height=120, bg=self.colors['bg'])
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
        
        # Don't add any initial group field - wait for data or user action
        
    def setup_extraction_controls(self, parent):
        """Setup data extraction controls"""
        frame = ttk.LabelFrame(parent, text="3. Set Time Points at Survival Rates", padding=5)
        frame.pack(fill=tk.X, pady=(0, 10))
        
        # Instructions for new workflow
        instruction_label = ttk.Label(frame, text="Select a point in the table below, then click on the image to set its position", foreground="gold")
        instruction_label.pack(fill=tk.X, pady=5)
        
        
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
        frame = ttk.LabelFrame(parent, text="4. Complete Image", padding=5)
        frame.pack(fill=tk.X, pady=(0, 10))
        
        # Create dynamic Done/Undone button (will be updated based on status)
        self.done_undone_btn = self.create_button(frame, text="Done", command=self.toggle_done_status)
        self.done_undone_btn.pack(fill=tk.X, pady=2)
        
        self.create_button(frame, text="Report Error", command=self.report_error).pack(fill=tk.X, pady=2)
        self.create_button(frame, text="View Data", command=self.view_data).pack(fill=tk.X, pady=2)
        
        self.export_status = ttk.Label(frame, text="Ready to mark image as complete", foreground="#ffd700")
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
                
        self.create_button(dialog, text="Load Selected", command=on_select).pack(pady=10)
        
    def load_image_file(self, file_path, preserve_state=False):
        """Load and display image file"""
        try:
            self.current_image_path = file_path
            self.original_image = Image.open(file_path)
            
            # Only reset calibration and data if not preserving state
            if not preserve_state:
                print(f"LOAD_IMAGE: Resetting calibration for {file_path}")
                self.reset_calibration()
                self.selected_points.clear()
            else:
                print(f"LOAD_IMAGE: Preserving calibration and points for {file_path}")
                print(f"LOAD_IMAGE: Current calibration: {self.axis_calibration}")
            
            # Display image
            self.display_image_on_canvas()
            
            # Update UI
            if hasattr(self, 'calibration_btn'):
                self.calibration_btn.config(state=tk.NORMAL)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image: {str(e)}")
            
    def display_image_on_canvas(self):
        """Display image on canvas with proper scaling"""
        if not hasattr(self, 'original_image') or not self.original_image:
            return
            
        # Calculate scale factor to fit canvas
        try:
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
        except:
            return
        
        if canvas_width <= 1 or canvas_height <= 1:
            # Don't reschedule to avoid infinite loops
            return
            
        img_width, img_height = self.original_image.size
        
        # Calculate base scale to fit image in canvas
        scale_x = (canvas_width - 50) / img_width
        scale_y = (canvas_height - 50) / img_height
        base_scale = min(scale_x, scale_y, 1.0)  # Don't scale up beyond original
        
        # Apply zoom level
        if hasattr(self, 'zoom_level'):
            self.scale_factor = base_scale * self.zoom_level
        else:
            self.scale_factor = base_scale
        
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
        
        # Show/hide scrollbars based on image size vs canvas size
        self.update_scrollbars(new_width, new_height)
        
        # Force canvas update
        self.canvas.update_idletasks()
        self.root.update_idletasks()
    
    def update_scrollbars(self, image_width, image_height):
        """Show or hide scrollbars based on whether image is larger than canvas"""
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        
        # Only show scrollbars if we have valid canvas dimensions
        if canvas_width > 1 and canvas_height > 1:
            # Check if image (plus padding) is larger than canvas
            needs_h_scroll = (image_width + 50) > canvas_width
            needs_v_scroll = (image_height + 50) > canvas_height
            
            print(f"Needs H scroll: {needs_h_scroll}, Needs V scroll: {needs_v_scroll}")
            
            # Manage horizontal scrollbar using grid
            if needs_h_scroll:
                print("Showing horizontal scrollbar")
                self.h_scrollbar.grid(row=1, column=0, sticky="ew")
            else:
                print("Hiding horizontal scrollbar")
                self.h_scrollbar.grid_remove()
            
            # Manage vertical scrollbar using grid
            if needs_v_scroll:
                print("Showing vertical scrollbar")
                self.v_scrollbar.grid(row=0, column=1, sticky="ns")
            else:
                print("Hiding vertical scrollbar")
                self.v_scrollbar.grid_remove()
        
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
        
        # Mark that user has modified data
        self.user_modified_data = True
        
        # Auto-populate points with survival axis coordinates after calibration
        if self.calibration_step == 4:
            self.auto_populate_survival_coordinates()
            
        # Clear input and update UI
        self.calibration_value.delete(0, tk.END)
        self.calibration_status.config(text=next_instruction)
        
        if self.calibration_step >= 4:
            self.calibration_btn.config(state=tk.DISABLED)
            
        # Refresh display
        self.display_image_on_canvas()
        
        # Auto-save after calibration changes
        self.auto_save_current_state()
        
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
        """Handle data point selection clicks - only set X coordinate, Y is pre-calculated"""
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
        
        # Get existing point (should have Y coordinate pre-calculated)
        existing_point = self.selected_points.get(self.selected_point_key)
        if not existing_point or existing_point.get('y') is None:
            messagebox.showwarning("Invalid Point", "Selected point doesn't have survival coordinates. Please populate points first.")
            return
            
        # Store only the X coordinate (time), keep the existing Y coordinate (survival)
        self.selected_points[self.selected_point_key] = {
            'x': x,  # User-clicked time position
            'y': existing_point['y']  # Pre-calculated survival position
        }
        
        # Mark that user has modified data
        self.user_modified_data = True
        
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
        
        # Auto-save after data point changes
        self.auto_save_current_state()
        
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
        
    def mark_done(self):
        """Mark current image as done"""
        if not self.current_image_path:
            messagebox.showwarning("No Image", "Please select an image first.")
            return
            
        # Auto-save current state with done status
        self.auto_save_current_state(status="done")
        self.export_status.config(text="Image marked as DONE ✓")
        
        # Update navigation to show status
        self.update_navigation_status()
        
        # Update the done/undone button
        self.update_done_undone_button()
        
    def toggle_done_status(self):
        """Toggle between done and undone status"""
        if not self.current_image_path:
            messagebox.showwarning("No Image", "Please select an image first.")
            return
            
        # Check current status
        current_status = self.get_current_image_status()
        
        if current_status == "done":
            # Image is done, so undone it
            self.mark_undone()
        else:
            # Image is not done (or has error), so mark as done
            self.mark_done()
    
    def get_current_image_status(self):
        """Get the current status of the loaded image"""
        if not self.dataset_path or not self.image_files or self.current_index >= len(self.image_files):
            return None
            
        base_name = self.image_files[self.current_index]
        try:
            results_path = self.dataset_path / "results" / f"{base_name}.json"
            if results_path.exists():
                with open(results_path, 'r') as f:
                    data = json.load(f)
                return data.get("status")
        except Exception as e:
            print(f"Error getting status for {base_name}: {e}")
        return None
        
    def mark_undone(self):
        """Remove done/error status from current image"""
        if not self.current_image_path:
            messagebox.showwarning("No Image", "Please select an image first.")
            return
            
        # Remove status by saving with empty status and error
        self.auto_save_current_state_clear_status()
        self.export_status.config(text="Status cleared - ready to mark image")
        
        # Update navigation to show status
        self.update_navigation_status()
        
        # Update the done/undone button
        self.update_done_undone_button()
        
    def update_done_undone_button(self):
        """Update the done/undone button text based on current status"""
        if not hasattr(self, 'done_undone_btn'):
            return
            
        current_status = self.get_current_image_status()
        
        if current_status == "done":
            self.done_undone_btn.config(text="Undone")
        else:
            self.done_undone_btn.config(text="Done")
        
    def report_error(self):
        """Report an error for current image"""
        if not self.current_image_path:
            messagebox.showwarning("No Image", "Please select an image first.")
            return
            
        # Show dialog to input error text
        error_text = simpledialog.askstring(
            "Report Error",
            "Describe the error or issue with this image:",
            initialvalue=""
        )
        
        if error_text:  # Only proceed if user entered text and didn't cancel
            # Auto-save current state with error status
            self.auto_save_current_state(status="error", error=error_text.strip())
            self.export_status.config(text="Error reported ✗")
            messagebox.showinfo("Error Reported", "Error has been recorded for this image!")
            
            # Update navigation to show status
            self.update_navigation_status()
            
            # Update the done/undone button
            self.update_done_undone_button()
    
    def update_navigation_status(self):
        """Update navigation display with status indicators"""
        if not hasattr(self, 'image_counter_label') or not self.dataset_path:
            return
            
        if self.current_index >= len(self.image_files):
            return
            
        current_file = self.image_files[self.current_index]
        status_indicator = self.get_image_status_indicator(current_file)
        
        # Update the counter label to include status
        counter_text = f"{self.current_index + 1}/{len(self.image_files)} {status_indicator}"
        self.image_counter_label.config(text=counter_text)
        
        # Update progress info if it exists
        if hasattr(self, 'progress_label'):
            self.update_progress_info()
    
    def get_image_status_indicator(self, base_name):
        """Get status indicator (✓/✗/○) for an image"""
        try:
            results_path = self.dataset_path / "results" / f"{base_name}.json"
            if results_path.exists():
                with open(results_path, 'r') as f:
                    data = json.load(f)
                
                if "status" in data:
                    if data["status"] == "done":
                        return "✓"
                    elif data["status"] == "error":
                        return "✗"
            return "○"  # Not completed
        except:
            return "○"
    
    def get_completion_stats(self):
        """Get completion statistics for the dataset"""
        if not self.dataset_path or not self.image_files:
            return 0, 0, 0
            
        done_count = 0
        error_count = 0
        total_count = len(self.image_files)
        
        for image_file in self.image_files:
            try:
                results_path = self.dataset_path / "results" / f"{image_file}.json"
                if results_path.exists():
                    with open(results_path, 'r') as f:
                        data = json.load(f)
                    
                    if "status" in data:
                        if data["status"] == "done":
                            done_count += 1
                        elif data["status"] == "error":
                            error_count += 1
            except:
                continue
                
        return done_count, error_count, total_count
    
    def refresh_groups_ui(self):
        """Refresh groups UI to match current groups list without triggering auto-population"""
        # Set flag to prevent auto-population during UI refresh
        self.ui_refreshing = True
        
        # Clear existing group entries
        for group_data in self.group_entries:
            group_data['frame'].destroy()
        self.group_entries.clear()
        
        # Add group fields for current groups (without triggering events)
        for i, group_name in enumerate(self.groups):
            self.add_group_field_silent()
            if self.group_entries:
                last_entry = self.group_entries[-1]['entry']
                last_entry.delete(0, tk.END)
                last_entry.insert(0, group_name)
                # Bind the event AFTER setting the value to avoid triggering during restore
                last_entry.bind('<KeyRelease>', lambda e: self.update_groups())
        
        # Add one empty field if no groups exist
        if not self.groups:
            self.add_group_field()
        
        # Clear the flag
        self.ui_refreshing = False
        
        print(f"Refreshed UI for {len(self.groups)} groups: {self.groups}")
    
    def update_progress_info(self):
        """Update progress label with completion stats"""
        if not hasattr(self, 'progress_label'):
            return
            
        done_count, error_count, total_count = self.get_completion_stats()
        completed_count = done_count + error_count
        percentage = int((completed_count / total_count) * 100) if total_count > 0 else 0
        
        progress_text = f"Progress: {completed_count}/{total_count} ({percentage}%)"
        self.progress_label.config(text=progress_text)
    
    def apply_incomplete_filter(self):
        """Apply or remove incomplete images filter"""
        if not self.dataset_path or not self.image_files:
            return
            
        if self.only_incomplete_var.get():
            # Filter to show only incomplete images
            self.filtered_image_files = []
            for image_file in self.image_files:
                status_indicator = self.get_image_status_indicator(image_file)
                if status_indicator == "○":  # Not completed
                    self.filtered_image_files.append(image_file)
            
            # Reset current index to first incomplete image
            if self.filtered_image_files:
                self.current_index = 0
                self.load_image_by_index(0, use_filtered=True)
            else:
                messagebox.showinfo("All Complete", "All images have been completed!")
                self.only_incomplete_var.set(False)  # Uncheck the box
        else:
            # Show all images
            self.filtered_image_files = None
            # Keep current image if possible
            if self.current_index < len(self.image_files):
                self.load_image_by_index(self.current_index, use_filtered=False)
        
        self.update_navigation_controls()
        
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
    
    def on_units_change(self, event=None):
        """Handle axis units change"""
        # Update internal units values
        if hasattr(self, 'x_units_entry'):
            new_x_units = self.x_units_entry.get().strip()
            if new_x_units:
                self.x_axis_units = new_x_units
        
        if hasattr(self, 'y_units_entry'):
            new_y_units = self.y_units_entry.get().strip()
            if new_y_units:
                self.y_axis_units = new_y_units
        
        # Auto-save changes
        self.auto_save_current_state()
        
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
            
            self.zoom_canvas = tk.Canvas(self.zoom_window, width=self.zoom_size*2, height=self.zoom_size*2, bg=self.colors['bg'])
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
        
        # Draw enhanced guidelines
        draw = ImageDraw.Draw(zoomed)
        center = self.zoom_size
        zoom_width = self.zoom_size * 2
        zoom_height = self.zoom_size * 2
        
        # Draw center crosshairs
        draw.line([(center-15, center), (center+15, center)], fill='red', width=2)
        draw.line([(center, center-15), (center, center+15)], fill='red', width=2)
        
        # Draw survival percentage guidelines if calibrated
        if self.is_calibrated():
            # Get Y coordinates for survival percentages
            y_min_coord = self.axis_calibration['y_min_coord'][1] if self.axis_calibration['y_min_coord'] else None
            y_max_coord = self.axis_calibration['y_max_coord'][1] if self.axis_calibration['y_max_coord'] else None
            
            if y_min_coord is not None and y_max_coord is not None:
                # Calculate survival line positions
                survival_percentages = [0, 25, 50, 75, 100]
                
                for percentage in survival_percentages:
                    # Calculate Y position for this survival percentage
                    ratio = percentage / 100.0
                    survival_y = y_min_coord - (ratio * (y_min_coord - y_max_coord))
                    
                    # Check if this line is visible in the zoom view
                    relative_y = survival_y - top
                    if 0 <= relative_y <= (bottom - top):
                        # Scale to zoom view
                        zoom_y = int(relative_y * zoom_height / (bottom - top))
                        
                        # Draw the survival guideline
                        color = 'red'
                        draw.line([(0, zoom_y), (zoom_width, zoom_y)], fill=color, width=2)
                        
                        # Add percentage label
                        draw.text((5, zoom_y + 2), f"{percentage}%", fill=color)
        
        # Display zoomed image
        self.zoom_photo = ImageTk.PhotoImage(zoomed)
        self.zoom_canvas.delete("all")
        self.zoom_canvas.create_image(0, 0, anchor=tk.NW, image=self.zoom_photo)
        
    def on_canvas_motion(self, event):
        """Handle mouse motion for pan mode"""
        # Legacy zoom functionality (if enabled)
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
                    
                    # Auto-save after table edit
                    self.auto_save_current_state()
                        
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
        
        # Mark that user has modified data
        self.user_modified_data = True
        
        # Update display
        self.update_points_tree()
        self.display_image_on_canvas()
        
        # Auto-save after point deletion
        self.auto_save_current_state()
    
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
        delete_btn = self.create_button(group_frame, text="×", width=2, 
                               command=lambda: self.remove_group_field(group_frame, entry))
        delete_btn.pack(side=tk.LEFT)
        
        # Store reference
        self.group_entries.append({'frame': group_frame, 'entry': entry, 'label': label})
        
        # Update scroll region
        self.groups_scrollable_frame.update_idletasks()
        self.groups_canvas.configure(scrollregion=self.groups_canvas.bbox("all"))
        
        # Don't set any default values - leave empty for user to fill
            
        # Auto-update groups
        self.update_groups()
    
    def add_group_field_silent(self):
        """Add a new group input field without event binding (for restore operations)"""
        group_frame = ttk.Frame(self.groups_scrollable_frame)
        group_frame.pack(fill=tk.X, pady=2)
        
        # Group number label (auto-size)
        group_num = len(self.group_entries) + 1
        label = ttk.Label(group_frame, text=f"Group {group_num}:")
        label.pack(side=tk.LEFT, padx=(0, 5))
        
        # Group name entry (auto-resizable) - NO EVENT BINDING
        entry = ttk.Entry(group_frame)
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        # Delete button
        delete_btn = self.create_button(group_frame, text="×", width=2, 
                               command=lambda: self.remove_group_field(group_frame, entry))
        delete_btn.pack(side=tk.LEFT)
        
        # Store reference
        self.group_entries.append({'frame': group_frame, 'entry': entry, 'label': label})
        
        # Update scroll region
        self.groups_scrollable_frame.update_idletasks()
        self.groups_canvas.configure(scrollregion=self.groups_canvas.bbox("all"))
            
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
        # Store previous groups to detect changes
        previous_groups = self.groups.copy() if hasattr(self, 'groups') else []
        
        self.groups = []
        for group_data in self.group_entries:
            group_name = group_data['entry'].get().strip()
            if group_name:
                self.groups.append(group_name)
        
        # If groups have changed, handle renames first, then clean up removed groups
        if previous_groups != self.groups:
            # Mark that user has modified data
            self.user_modified_data = True
            # Handle potential group renames before cleanup
            if len(previous_groups) == len(self.groups) and previous_groups and self.groups:
                self.handle_group_rename(previous_groups, self.groups)
            else:
                # Automatically cleanup removed groups and their points
                self.cleanup_removed_groups()
        
        # Groups are now displayed directly in the input fields and table
        
        # Only populate missing points (don't remove existing ones)
        self.populate_missing_points()
        
        # If calibration is complete, also auto-populate survival coordinates (but not during UI refresh)
        if self.is_calibrated() and not getattr(self, 'ui_refreshing', False):
            self.auto_populate_survival_coordinates()
        
        # Update points tree view if it exists
        if hasattr(self, 'points_tree'):
            self.update_points_tree()
            
            # Auto-select the first row if points exist and no point is currently selected
            if self.selected_points and not self.selected_point_key:
                first_item = self.points_tree.get_children()
                if first_item:
                    self.points_tree.selection_set(first_item[0])
                    self.points_tree.focus(first_item[0])
            
        # Auto-save after group changes
        self.auto_save_current_state()
    
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
    
    def populate_missing_points(self):
        """Create entries only for missing group-survival rate combinations (preserves existing points)"""
        if not self.groups:
            return
            
        points_added = 0
        # Create placeholder entries only for combinations that don't exist
        for group in self.groups:
            for survival_rate in self.survival_rates:
                key = f"{group}_{survival_rate}"
                if key not in self.selected_points:
                    # Add placeholder point with no coordinates (will show as "N/A")
                    print(f"Adding missing placeholder point: {key}")
                    self.selected_points[key] = {'x': None, 'y': None}
                    points_added += 1
                else:
                    print(f"Preserving existing point: {key}")
        
        if points_added > 0:
            print(f"populate_missing_points: Added {points_added} placeholder points")
    
    
    def auto_populate_survival_coordinates(self):
        """Automatically populate points with survival axis coordinates after calibration"""
        print(f"Auto-populate called: calibrated={self.is_calibrated()}, groups={len(self.groups) if self.groups else 0}")
        if not self.is_calibrated() or not self.groups:
            return
        
        # Calculate Y coordinates for each survival rate
        survival_percentages = [0, 25, 50, 75, 100]  # Convert survival_rates to numeric values
        survival_y_coords = {}
        
        # Get calibration values
        y_min_val = self.axis_calibration['y_min']
        y_max_val = self.axis_calibration['y_max']
        y_min_coord = self.axis_calibration['y_min_coord'][1]  # pixel Y of minimum survival
        y_max_coord = self.axis_calibration['y_max_coord'][1]  # pixel Y of maximum survival
        
        # Calculate pixel Y coordinate for each survival percentage
        for i, percentage in enumerate(survival_percentages):
            survival_rate = self.survival_rates[i]  # "0%", "25%", etc.
            
            # Linear interpolation between min and max survival coordinates
            # Note: Y coordinates are flipped (higher survival = lower pixel Y)
            ratio = percentage / 100.0
            pixel_y = y_min_coord - (ratio * (y_min_coord - y_max_coord))
            survival_y_coords[survival_rate] = pixel_y
        
        # Create points for all group-survival rate combinations
        points_added = 0
        for group in self.groups:
            for survival_rate in self.survival_rates:
                key = f"{group}_{survival_rate}"
                
                # Check if point exists and is already populated/set
                existing_point = self.selected_points.get(key)
                
                # Only add/update if point doesn't exist OR if it's completely empty
                if existing_point is None:
                    # Point doesn't exist - create new one
                    print(f"Creating new point: {key}")
                    self.selected_points[key] = {
                        'x': None,  # User needs to click to set time coordinate
                        'y': survival_y_coords[survival_rate]  # Auto-calculated survival coordinate
                    }
                    points_added += 1
                elif existing_point.get('x') is None and existing_point.get('y') is None:
                    # Point exists but is completely empty - add Y coordinate only
                    print(f"Adding Y coordinate to empty point: {key}")
                    self.selected_points[key]['y'] = survival_y_coords[survival_rate]
                elif existing_point.get('y') is None and existing_point.get('x') is not None:
                    # Point has X but no Y - add Y coordinate
                    print(f"Adding Y coordinate to point with X: {key}")
                    self.selected_points[key]['y'] = survival_y_coords[survival_rate]
                else:
                    # Point already has data - don't touch it
                    print(f"Preserving existing point: {key} = {existing_point}")
        
        print(f"Auto-populate completed: {points_added} points added, total points: {len(self.selected_points)}")
        
        if points_added > 0 or True:  # Always update display even if no new points added
            # Update the points tree view
            if hasattr(self, 'points_tree'):
                self.update_points_tree()
            
            # Auto-save the populated points
            self.auto_save_current_state()
        
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
    
    def select_dataset(self):
        """Select the extraction_data folder containing PNG and metadata"""
        folder_path = filedialog.askdirectory(title="Select extraction_data folder")
        if folder_path:
            extraction_path = Path(folder_path)
            png_path = extraction_path / "png"
            metadata_path = extraction_path / "metadata"
            
            if png_path.exists() and metadata_path.exists():
                self.dataset_path = extraction_path
                self.load_dataset()
            else:
                messagebox.showerror("Invalid Dataset", 
                    "Selected folder must contain 'png' and 'metadata' subfolders")
    
    def load_dataset(self):
        """Load all images from the dataset"""
        png_path = self.dataset_path / "png"
        
        # Get all PNG files and sort them
        png_files = list(png_path.glob("*.png"))
        png_files.sort()
        
        # Store just the base names (without .png extension)
        self.image_files = [f.stem for f in png_files]
        self.current_index = 0
        
        # Update UI
        self.dataset_label.config(text=f"{len(self.image_files)} images loaded")
        self.update_navigation_state()
        
        # Load first image if available
        if self.image_files:
            self.load_image_by_index(0)
    
    def load_image_by_index(self, index, use_filtered=None, preserve_calibration=False):
        """Load image and metadata by index"""
        # Set loading flag to prevent auto-save during data loading
        self.loading_in_progress = True
        
        try:
            # Determine which image list to use
            if use_filtered is None:
                use_filtered = self.only_incomplete_var.get() if hasattr(self, 'only_incomplete_var') else False
            
            current_list = self.filtered_image_files if (use_filtered and self.filtered_image_files) else self.image_files
            
            if 0 <= index < len(current_list):
                self.current_index = index
                base_name = current_list[index]
                
                # Check if results file exists before resetting
                results_path = self.dataset_path / "results" / f"{base_name}.json"
                
                if not results_path.exists():
                    # Only reset if no saved data exists
                    print(f"No saved data for {base_name} - resetting state")
                    self.reset_for_new_image()
                else:
                    # Clear only the UI groups, don't reset calibration/points that might be reloaded
                    print(f"Saved data exists for {base_name} - preserving state")
                    self.groups.clear()
                    self.refresh_groups_ui()
                
                # Load PNG image
                png_path = self.dataset_path / "png" / f"{base_name}.png"
                # Don't preserve state - let each image use its own calibration
                self.load_image_file(str(png_path), preserve_state=False)
                
                # Load previous extraction data FIRST (prioritize saved results)
                # Always load the correct calibration for each image
                self.load_extraction_data(base_name, preserve_calibration=False)
                
                # Load metadata only as fallback if no saved data exists
                self.load_metadata(base_name)
                
                # Update navigation UI
                self.update_navigation_state()
                
                # Update the done/undone button based on loaded image status
                self.update_done_undone_button()
        finally:
            # Always clear loading flag when done
            self.loading_in_progress = False
            # Reset user modification flag after loading
            self.user_modified_data = False
    
    def reset_for_new_image(self):
        """Reset state when loading a new image"""
        # Reset calibration
        self.axis_calibration = {
            'x_min': None, 'x_max': None, 'y_min': None, 'y_max': None,
            'x_min_coord': None, 'x_max_coord': None, 'y_min_coord': None, 'y_max_coord': None
        }
        self.calibration_step = 0
        
        # Reset points
        self.selected_points.clear()
        self.selected_point_key = None
        
        # Reset groups (will be restored from metadata or saved data)
        self.groups.clear()
        # Clear the UI display of groups
        self.refresh_groups_ui()
        
        # Update UI
        self.calibration_status.config(text="Click on X-axis minimum point")
        if hasattr(self, 'calibration_btn'):
            self.calibration_btn.config(state=tk.DISABLED)
    
    def load_metadata(self, base_name):
        """Load metadata for the current image and auto-populate groups"""
        metadata_path = self.dataset_path / "metadata" / f"{base_name}.json"
        
        # SIMPLE RULE: Check if results file exists - if yes, check each field before populating
        results_path = self.dataset_path / "results" / f"{base_name}.json"
        results_data = {}
        
        if results_path.exists():
            try:
                with open(results_path, 'r') as f:
                    results_data = json.load(f)
                print(f"Results file exists for {base_name} - checking fields before metadata population")
            except Exception as e:
                print(f"Error reading results file for {base_name}: {e}")
        
        if metadata_path.exists():
            try:
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
                
                # Cache metadata
                self.metadata_cache[base_name] = metadata
                
                # Always update image description (doesn't interfere with user data)
                self.update_image_description(metadata.get('image_description', ''))
                
                # Check groups: only populate if groups field doesn't exist in results
                if 'groups_survival_experiment' in metadata:
                    groups_in_results = ("metadata" in results_data and "groups" in results_data["metadata"])
                    
                    if not groups_in_results and not self.groups:
                        metadata_groups = metadata['groups_survival_experiment']
                        if metadata_groups:
                            print(f"Auto-populating groups from metadata for {base_name}: {metadata_groups}")
                            self.auto_populate_groups(metadata_groups)
                        else:
                            print(f"Empty groups in metadata for {base_name}")
                    else:
                        print(f"Groups field exists in results for {base_name} - skipping metadata groups")
                
            except Exception as e:
                print(f"Error loading metadata for {base_name}: {e}")
                self.metadata_cache[base_name] = {}
                self.update_image_description("Error loading image description.")
        else:
            # No metadata file found
            self.update_image_description("No metadata file found for this image.")
            
        # Clear groups UI only if no groups exist and no groups in results
        groups_in_results = ("metadata" in results_data and "groups" in results_data["metadata"])
        if not self.groups and not groups_in_results:
            print(f"No groups found for {base_name} - ensuring groups UI is cleared")
            self.refresh_groups_ui()
    
    def auto_populate_groups(self, groups):
        """Auto-populate group entries from metadata"""
        # Clear existing groups
        self.groups = []
        for group_entry in self.group_entries:
            group_entry['frame'].destroy()
        self.group_entries = []
        
        # Add groups from metadata using silent method to avoid triggering auto-save
        for group_name in groups:
            self.add_group_field_silent()
            # Set the name in the last added entry
            if self.group_entries:
                last_entry = self.group_entries[-1]['entry']
                last_entry.delete(0, tk.END)
                last_entry.insert(0, group_name)
        
        # Update the groups list without triggering auto-save during metadata population
        self.groups = []
        for group_data in self.group_entries:
            group_name = group_data['entry'].get().strip()
            if group_name:
                self.groups.append(group_name)
        
        # Update UI without auto-save
        self.refresh_groups_ui()
        self.populate_missing_points()
    
    def prev_image(self):
        """Navigate to previous image"""
        current_list = self.get_current_image_list()
        if self.current_index > 0:
            # Auto-save current state before navigating
            current_cal_state = self.is_calibrated()
            print(f"NAVIGATION: Current calibration state before prev_image: {current_cal_state}")
            if current_cal_state:
                print(f"NAVIGATION: Current calibration: {self.axis_calibration}")
            self.auto_save_current_state()
            # Don't preserve calibration when navigating - each image should use its own calibration
            print(f"NAVIGATION: Loading previous image with its own calibration")
            self.load_image_by_index(self.current_index - 1, preserve_calibration=False)
    
    def next_image(self):
        """Navigate to next image"""
        current_list = self.get_current_image_list()
        if self.current_index < len(current_list) - 1:
            # Auto-save current state before navigating
            current_cal_state = self.is_calibrated()
            print(f"NAVIGATION: Current calibration state before next_image: {current_cal_state}")
            if current_cal_state:
                print(f"NAVIGATION: Current calibration: {self.axis_calibration}")
            self.auto_save_current_state()
            # Don't preserve calibration when navigating - each image should use its own calibration
            print(f"NAVIGATION: Loading next image with its own calibration")
            self.load_image_by_index(self.current_index + 1, preserve_calibration=False)
    
    def get_current_image_list(self):
        """Get the current image list (filtered or full)"""
        use_filtered = hasattr(self, 'only_incomplete_var') and self.only_incomplete_var.get()
        return self.filtered_image_files if (use_filtered and self.filtered_image_files) else self.image_files
    
    def update_navigation_state(self):
        """Update navigation buttons and labels"""
        if not self.image_files:
            self.prev_btn.config(state=tk.DISABLED)
            self.next_btn.config(state=tk.DISABLED)
            if hasattr(self, 'image_counter_label'):
                self.image_counter_label.config(text="0 of 0 ○")
            self.current_file_label.config(text="")
            return
        
        # Get current list and update navigation info
        current_list = self.get_current_image_list()
        total = len(current_list)
        current = self.current_index + 1
        
        # Update current file display
        if current_list and self.current_index < len(current_list):
            current_file = current_list[self.current_index]
            self.current_file_label.config(text=f"Current: {current_file}")
            
            # Update status indicators
            self.update_navigation_status()
            self.update_progress_info()
        
        # Update button states
        self.prev_btn.config(state=tk.NORMAL if self.current_index > 0 else tk.DISABLED)
        self.next_btn.config(state=tk.NORMAL if self.current_index < total - 1 else tk.DISABLED)
    
    def update_navigation_controls(self):
        """Update navigation controls after filtering changes"""
        self.update_navigation_state()
    

    def auto_save_current_state(self, status=None, error=None):
        """Automatically save the current extraction state"""
        if not self.auto_save_enabled or not self.dataset_path or not self.image_files:
            print("Auto-save skipped: not enabled or missing dataset/images")
            return
            
        if self.loading_in_progress:
            print("Auto-save skipped: loading in progress")
            return
            
        if self.current_index >= len(self.image_files):
            print("Auto-save skipped: invalid current index")
            return
            
        current_file = self.image_files[self.current_index]
        print(f"Auto-saving: {current_file}")
        self.save_extraction_data(current_file, status=status, error=error)
    
    def auto_save_current_state_clear_status(self):
        """Save current state and clear status/error"""
        if not self.auto_save_enabled or not self.dataset_path or not self.image_files:
            print("Auto-save skipped: not enabled or missing dataset/images")
            return
            
        if self.loading_in_progress:
            print("Auto-save skipped: loading in progress")
            return
            
        if self.current_index >= len(self.image_files):
            print("Auto-save skipped: invalid current index")
            return
            
        current_file = self.image_files[self.current_index]
        print(f"Auto-saving with cleared status: {current_file}")
        self.save_extraction_data_clear_status(current_file)
    
    def save_extraction_data(self, base_name, status=None, error=None):
        """Save extraction data for a specific image"""
        try:
            # Create results directory if it doesn't exist
            results_path = self.dataset_path / "results"
            results_path.mkdir(exist_ok=True)
            
            # Load existing data to preserve ALL existing information (NEVER overwrite with metadata)
            result_file = results_path / f"{base_name}.json"
            existing_data = {}
            
            if result_file.exists():
                try:
                    with open(result_file, 'r') as f:
                        existing_data = json.load(f)
                    print(f"SAVE: Found existing results file for {base_name} - preserving existing data")
                except Exception as e:
                    print(f"Could not load existing data: {e}")
                    existing_data = {}
            
            # Note: We preserve all user-created points, even if groups change
            
            # Prepare data to save 
            # RULE: Only preserve existing metadata if user hasn't made changes (prevents metadata overwrite)
            # If user made changes, always save current state
            if existing_data and not self.user_modified_data:
                print(f"SAVE: No user changes detected - preserving existing metadata for {base_name}")
                save_data = existing_data.copy()  # Start with existing data
                # Only update extraction_date and timestamp
                if "metadata" not in save_data:
                    save_data["metadata"] = {}
                save_data["metadata"]["extraction_date"] = self.get_current_timestamp()
                save_data["metadata"]["image_file"] = f"{base_name}.png"
            else:
                if existing_data and self.user_modified_data:
                    print(f"SAVE: User made changes - updating all data for {base_name}")
                else:
                    print(f"SAVE: Creating new metadata structure for {base_name}")
                save_data = {
                    "metadata": {
                        "image_file": f"{base_name}.png",
                        "extraction_date": self.get_current_timestamp(),
                        "x_axis_type": self.x_axis_type,
                        "y_axis_type": self.y_axis_type,
                        "x_axis_units": self.x_axis_units,
                        "y_axis_units": self.y_axis_units,
                        "calibration": self.axis_calibration.copy(),
                        "groups": self.groups.copy()
                    },
                    "extracted_points": {},
                    "raw_coordinates": {}
                }
                # Preserve status and error from existing data if available
                if existing_data:
                    if "status" in existing_data:
                        save_data["status"] = existing_data["status"]
                    if "error" in existing_data:
                        save_data["error"] = existing_data["error"]
            
            # Handle status and error if provided (these override any existing values)
            if status is not None:
                save_data["status"] = status
                print(f"Saving status: {status}")
            if error is not None:
                save_data["error"] = error
                print(f"Saving error: {error}")
            
            # Process extracted points - include ALL points (populated and set)
            for key, coord in self.selected_points.items():
                # Parse key (format: "group_survivalrate")
                try:
                    group, survival_rate = key.rsplit('_', 1)
                    
                    # Only include if group still exists
                    if group in self.groups:
                        # Always save raw coordinates (even populated points with X=None)
                        save_data["raw_coordinates"][key] = coord
                        
                        # Initialize extracted_points structure for this survival rate
                        if survival_rate not in save_data["extracted_points"]:
                            save_data["extracted_points"][survival_rate] = {}
                        
                        # Save time values for points with X coordinates set
                        if coord is not None and coord.get('x') is not None:
                            # Convert pixel coordinates to real values using the calibration being saved
                            time_value = None
                            saved_calibration = save_data["metadata"]["calibration"]
                            if self.is_calibration_data_complete(saved_calibration):
                                time_value = self.pixel_to_real_x_with_calibration(coord['x'], saved_calibration)
                                print(f"SAVE: Using saved calibration for {base_name} - pixel {coord['x']} -> time {time_value}")
                            else:
                                print(f"SAVE: No valid calibration for {base_name} - saving time as None")
                            
                            save_data["extracted_points"][survival_rate][group] = time_value
                        else:
                            # For populated points without X coordinate, save as null
                            save_data["extracted_points"][survival_rate][group] = None
                    
                except ValueError:
                    # Handle malformed keys - save anyway for compatibility
                    save_data["raw_coordinates"][key] = coord
            
            # Save to JSON file
            result_file = results_path / f"{base_name}.json"
            with open(result_file, 'w') as f:
                json.dump(save_data, f, indent=2, default=str)
                
        except Exception as e:
            print(f"Auto-save failed for {base_name}: {e}")
    
    def save_extraction_data_clear_status(self, base_name):
        """Save extraction data and explicitly clear status/error fields"""
        try:
            # Create results directory if it doesn't exist
            results_path = self.dataset_path / "results"
            results_path.mkdir(exist_ok=True)
            
            # Load existing data to preserve ALL existing information (NEVER overwrite with metadata)
            result_file = results_path / f"{base_name}.json"
            existing_data = {}
            
            if result_file.exists():
                try:
                    with open(result_file, 'r') as f:
                        existing_data = json.load(f)
                    print(f"SAVE_CLEAR: Found existing results file for {base_name} - preserving existing data")
                except Exception as e:
                    print(f"Could not load existing data: {e}")
                    existing_data = {}
            
            # Prepare data to save 
            # RULE: Only preserve existing metadata if user hasn't made changes (prevents metadata overwrite)
            # If user made changes, always save current state
            if existing_data and not self.user_modified_data:
                print(f"SAVE_CLEAR: No user changes detected - preserving existing metadata for {base_name}")
                save_data = existing_data.copy()  # Start with existing data
                # Only update extraction_date and remove status/error
                if "metadata" not in save_data:
                    save_data["metadata"] = {}
                save_data["metadata"]["extraction_date"] = self.get_current_timestamp()
                save_data["metadata"]["image_file"] = f"{base_name}.png"
                # Remove status and error fields as intended
                save_data.pop("status", None)
                save_data.pop("error", None)
            else:
                if existing_data and self.user_modified_data:
                    print(f"SAVE_CLEAR: User made changes - updating all data for {base_name}")
                else:
                    print(f"SAVE_CLEAR: Creating new metadata structure for {base_name}")
                save_data = {
                    "metadata": {
                        "image_file": f"{base_name}.png",
                        "extraction_date": self.get_current_timestamp(),
                        "x_axis_type": self.x_axis_type,
                        "y_axis_type": self.y_axis_type,
                        "x_axis_units": self.x_axis_units,
                        "y_axis_units": self.y_axis_units,
                        "calibration": self.axis_calibration.copy(),
                        "groups": self.groups.copy()
                    },
                    "extracted_points": {},
                    "raw_coordinates": {}
                }
            
            # Process extracted points - same as regular save
            for key, coord in self.selected_points.items():
                try:
                    group, survival_rate = key.rsplit('_', 1)
                    if group in self.groups:
                        save_data["raw_coordinates"][key] = coord
                        if survival_rate not in save_data["extracted_points"]:
                            save_data["extracted_points"][survival_rate] = {}
                        
                        if coord is not None and coord.get('x') is not None:
                            time_value = None
                            saved_calibration = save_data["metadata"]["calibration"]
                            if self.is_calibration_data_complete(saved_calibration):
                                time_value = self.pixel_to_real_x_with_calibration(coord['x'], saved_calibration)
                                print(f"SAVE_CLEAR: Using saved calibration for {base_name} - pixel {coord['x']} -> time {time_value}")
                            else:
                                print(f"SAVE_CLEAR: No valid calibration for {base_name} - saving time as None")
                            save_data["extracted_points"][survival_rate][group] = time_value
                        else:
                            save_data["extracted_points"][survival_rate][group] = None
                except ValueError:
                    save_data["raw_coordinates"][key] = coord
            
            # Save to JSON file (deliberately not including status or error)
            result_file = results_path / f"{base_name}.json"
            with open(result_file, 'w') as f:
                json.dump(save_data, f, indent=2, default=str)
            
            print(f"Status/error cleared for {base_name}")
                
        except Exception as e:
            print(f"Clear status failed for {base_name}: {e}")
    
    def cleanup_removed_groups(self):
        """Remove data points for groups that no longer exist"""
        keys_to_remove = []
        current_group_names = set(self.groups)
        
        for key in list(self.selected_points.keys()):
            if '_' in key:
                try:
                    group, survival_rate = key.rsplit('_', 1)
                    # If the group is no longer in the current groups list, mark for removal
                    if group not in current_group_names:
                        keys_to_remove.append(key)
                except ValueError:
                    continue
        
        # Remove the obsolete keys
        if keys_to_remove:
            removed_groups = set()
            for key in keys_to_remove:
                group, _ = key.rsplit('_', 1)
                removed_groups.add(group)
                del self.selected_points[key]
            
            print(f"Cleaned up {len(keys_to_remove)} points from {len(removed_groups)} removed groups: {', '.join(sorted(removed_groups))}")
            
            # Update the points tree view after cleanup
            if hasattr(self, 'points_tree'):
                self.update_points_tree()
            
            # Auto-save after cleanup
            self.auto_save_current_state()
    
    def handle_group_rename(self, old_groups, new_groups):
        """Handle group renaming by updating point keys"""
        if len(old_groups) != len(new_groups):
            return  # This is addition/removal, not renaming
            
        # Create mapping of old to new group names
        group_mapping = {}
        for old_group, new_group in zip(old_groups, new_groups):
            if old_group != new_group and old_group and new_group:
                group_mapping[old_group] = new_group
        
        if not group_mapping:
            return  # No renames detected
            
        # Update keys in selected_points
        points_to_update = {}
        for old_key, coord in list(self.selected_points.items()):
            if '_' in old_key:
                try:
                    group, survival_rate = old_key.rsplit('_', 1)
                    if group in group_mapping:
                        new_group = group_mapping[group]
                        new_key = f"{new_group}_{survival_rate}"
                        points_to_update[new_key] = coord
                        del self.selected_points[old_key]
                except ValueError:
                    continue
        
        # Add the updated points
        self.selected_points.update(points_to_update)
    
    def load_extraction_data(self, base_name, preserve_calibration=False):
        """Load previously saved extraction data"""
        # Track what was loaded from results to prevent metadata override
        loaded_data = {
            'calibration': False,
            'groups': False, 
            'points': False,
            'status': False,
            'axis_config': False
        }
        
        try:
            results_path = self.dataset_path / "results" / f"{base_name}.json"
            
            if results_path.exists():
                with open(results_path, 'r') as f:
                    data = json.load(f)
                
                # Restore groups if saved (priority over metadata)
                if "metadata" in data and "groups" in data["metadata"]:
                    saved_groups = data["metadata"]["groups"]
                    if saved_groups:  # Only use if not empty
                        print(f"Using saved groups for {base_name}: {saved_groups}")
                        self.groups = saved_groups.copy()  # Direct assignment without auto-population
                        self.refresh_groups_ui()  # Update UI only
                        loaded_data['groups'] = True
                    else:
                        # Even empty groups in results should prevent metadata loading
                        print(f"Empty groups found in results for {base_name} - preventing metadata override")
                        loaded_data['groups'] = True
                
                # Restore axis types and units if saved (priority over defaults)
                if "metadata" in data:
                    metadata = data["metadata"]
                    if "x_axis_type" in metadata or "y_axis_type" in metadata or "x_axis_units" in metadata or "y_axis_units" in metadata:
                        loaded_data['axis_config'] = True
                        
                    if "x_axis_type" in metadata:
                        self.x_axis_type = metadata["x_axis_type"]
                        if hasattr(self, 'x_axis_var'):
                            self.x_axis_var.set(self.x_axis_type)
                    if "y_axis_type" in metadata:
                        self.y_axis_type = metadata["y_axis_type"]
                        if hasattr(self, 'y_axis_label'):
                            self.y_axis_label.config(text=metadata["y_axis_type"])
                    if "x_axis_units" in metadata:
                        self.x_axis_units = metadata["x_axis_units"]
                        if hasattr(self, 'x_units_entry'):
                            self.x_units_entry.delete(0, tk.END)
                            self.x_units_entry.insert(0, self.x_axis_units)
                    if "y_axis_units" in metadata:
                        self.y_axis_units = metadata["y_axis_units"]
                        if hasattr(self, 'y_units_entry'):
                            self.y_units_entry.delete(0, tk.END)
                            self.y_units_entry.insert(0, self.y_axis_units)
                
                # Restore calibration if saved (unless preserving current calibration)
                if not preserve_calibration and "calibration" in data.get("metadata", {}):
                    saved_calibration = data["metadata"]["calibration"]
                    self.axis_calibration.update(saved_calibration)
                    loaded_data['calibration'] = True
                    # Update calibration step based on how complete it is
                    if self.is_calibrated():
                        self.calibration_step = 4
                        self.calibration_status.config(text="Calibration complete! (loaded from file)")
                        if hasattr(self, 'calibration_btn'):
                            self.calibration_btn.config(state=tk.DISABLED)
                elif preserve_calibration:
                    print(f"LOAD_EXTRACTION: Preserving current calibration for {base_name} - not loading from saved data")
                    print(f"LOAD_EXTRACTION: Current calibration being preserved: {self.axis_calibration}")
                
                # Restore selected points from raw coordinates FIRST
                if "raw_coordinates" in data:
                    self.selected_points = data["raw_coordinates"]
                    loaded_data['points'] = True
                    if hasattr(self, 'points_tree'):
                        self.update_points_tree()
                    self.display_image_on_canvas()
                    print(f"Loaded {len(self.selected_points)} existing points from saved data")
                
                # Only auto-populate points if calibration exists AND no points were loaded
                if self.is_calibrated() and not loaded_data['points']:
                    print("Calibration loaded but no points exist - auto-populating survival coordinates")
                    self.auto_populate_survival_coordinates()
                elif self.is_calibrated() and loaded_data['points']:
                    print("Calibration and points loaded - preserving existing points, no auto-population")
                
                # Restore status and error information if saved
                if "status" in data:
                    loaded_data['status'] = True
                    print(f"Loaded status '{data['status']}' for {base_name}")
                if "error" in data:
                    print(f"Loaded error info for {base_name}: {data['error']}")
                
            # Store what was loaded for metadata method to respect
            self._loaded_from_results = loaded_data
            return loaded_data
                
        except Exception as e:
            print(f"Failed to load extraction data for {base_name}: {e}")
            self._loaded_from_results = loaded_data
            return loaded_data
    
    def get_current_timestamp(self):
        """Get current timestamp in ISO format"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def is_calibrated(self):
        """Check if axis calibration is complete"""
        cal = self.axis_calibration
        return all(val is not None for val in [
            cal['x_min'], cal['x_max'], cal['y_min'], cal['y_max'],
            cal['x_min_coord'], cal['x_max_coord'], cal['y_min_coord'], cal['y_max_coord']
        ])
    
    def is_calibration_data_complete(self, calibration):
        """Check if a given calibration dictionary is complete"""
        if not calibration:
            return False
        return all(val is not None for val in [
            calibration.get('x_min'), calibration.get('x_max'), 
            calibration.get('y_min'), calibration.get('y_max'),
            calibration.get('x_min_coord'), calibration.get('x_max_coord'), 
            calibration.get('y_min_coord'), calibration.get('y_max_coord')
        ])
    
    def pixel_to_real_x_with_calibration(self, pixel_x, calibration):
        """Convert pixel X coordinate to real X axis value using specific calibration"""
        if not self.is_calibration_data_complete(calibration):
            return None
            
        x_min_coord = calibration['x_min_coord'][0]  # x coordinate of min point
        x_max_coord = calibration['x_max_coord'][0]  # x coordinate of max point
        x_min_val = calibration['x_min']
        x_max_val = calibration['x_max']
        
        # Linear interpolation
        x_range = x_max_val - x_min_val
        pixel_x_range = x_max_coord - x_min_coord
        
        if pixel_x_range == 0:
            return x_min_val
            
        # Calculate position as ratio and interpolate
        ratio = (pixel_x - x_min_coord) / pixel_x_range
        real_x = x_min_val + (ratio * x_range)
        
        return real_x
    
    def pixel_to_real_x(self, pixel_x):
        """Convert pixel X coordinate to real X axis value"""
        if not self.is_calibrated():
            return None
            
        x_min_coord = self.axis_calibration['x_min_coord'][0]  # x coordinate of min point
        x_max_coord = self.axis_calibration['x_max_coord'][0]  # x coordinate of max point
        x_min_val = self.axis_calibration['x_min']
        x_max_val = self.axis_calibration['x_max']
        
        # Linear interpolation
        x_range = x_max_val - x_min_val
        pixel_x_range = x_max_coord - x_min_coord
        
        if pixel_x_range == 0:
            return x_min_val
            
        ratio = (pixel_x - x_min_coord) / pixel_x_range
        real_x = x_min_val + (ratio * x_range)
        
        return real_x
    
    
    def zoom_in(self):
        """Zoom in on the image"""
        try:
            if not hasattr(self, 'zoom_level'):
                self.zoom_level = 1.0
            self.zoom_level = min(self.zoom_level * 1.25, 5.0)  # Max 5x zoom
            self.update_zoom()
        except Exception as e:
            print(f"Error in zoom_in: {e}")
    
    def zoom_out(self):
        """Zoom out on the image"""
        try:
            if not hasattr(self, 'zoom_level'):
                self.zoom_level = 1.0
            self.zoom_level = max(self.zoom_level * 0.8, 0.1)  # Min 0.1x zoom
            self.update_zoom()
        except Exception as e:
            print(f"Error in zoom_out: {e}")
    
    def reset_zoom(self):
        """Reset zoom to fit image"""
        try:
            self.zoom_level = 1.0
            self.update_zoom()
        except Exception as e:
            print(f"Error in reset_zoom: {e}")
    
    def update_zoom(self):
        """Update the image display with current zoom level"""
        # Prevent recursive updates
        if getattr(self, '_updating_zoom', False):
            return
        
        self._updating_zoom = True
        try:
            # Update zoom label
            if hasattr(self, 'zoom_label'):
                self.zoom_label.config(text=f"{int(self.zoom_level * 100)}%")
            
            # Redisplay image if it exists
            if hasattr(self, 'original_image') and self.original_image:
                self.display_image_on_canvas()
        except Exception as e:
            print(f"Error updating zoom: {e}")
        finally:
            self._updating_zoom = False
    
    def on_canvas_release(self, event):
        """Handle mouse button release"""
        # Handle calibration point release
        if self.dragging_point:
            self.dragging_point = None
    
    def on_mouse_wheel(self, event):
        """Handle mouse wheel for zooming"""
        if event.delta > 0 or event.num == 4:  # Zoom in
            self.zoom_in()
        elif event.delta < 0 or event.num == 5:  # Zoom out
            self.zoom_out()
    
    def on_canvas_configure(self, event):
        """Handle canvas resize to update scrollbar visibility"""
        if self.original_image and hasattr(self, 'canvas_image'):
            # Get current image dimensions
            img_width, img_height = self.original_image.size
            
            # Apply current zoom level
            base_scale = min((self.canvas.winfo_width() - 50) / img_width,
                           (self.canvas.winfo_height() - 50) / img_height, 1.0)
            scale_factor = base_scale * self.zoom_level
            
            new_width = int(img_width * scale_factor)
            new_height = int(img_height * scale_factor)
            
            # Update scrollbars based on new canvas size
            self.update_scrollbars(new_width, new_height)
    
    def initial_layout_adjustments(self):
        """Make initial layout adjustments after window is displayed"""
        # Hide scrollbars initially when no image is loaded
        if hasattr(self, 'v_scrollbar') and hasattr(self, 'h_scrollbar'):
            self.v_scrollbar.grid_remove()
            self.h_scrollbar.grid_remove()
        
        # Set the sash position to show control panel fully
        if hasattr(self, 'paned_window') and hasattr(self, 'scrollable_frame'):
            # Update to ensure all widgets are laid out
            self.root.update_idletasks()
            
            # Get the actual required width of the control panel content
            self.scrollable_frame.update_idletasks()
            required_width = self.scrollable_frame.winfo_reqwidth()
            
            # Add some padding for scrollbar and margins
            total_width = required_width + 40
            
            # Set sash position based on actual content width
            self.paned_window.sash_place(0, total_width, 0)
            
            print(f"Control panel width set to {total_width}px (content: {required_width}px)")

    def on_closing(self):
        """Handle application closing"""
        # Auto-save final state before closing
        self.auto_save_current_state()
        
        if self.zoom_window:
            self.zoom_window.destroy()
        self.root.destroy()


if __name__ == "__main__":
    app = SurvivalCurveExtractor()
    app.run()