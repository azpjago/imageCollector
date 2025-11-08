# Import library
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import os
import requests
from serpapi import GoogleSearch
from time import sleep
from PIL import Image, ImageStat
from io import BytesIO
import urllib3
import warnings
import colorsys
from datetime import datetime

# Disable warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
warnings.filterwarnings("ignore")

class ImageDownloaderApp:
	def __init__(self, root):
		self.root = root
		self.root.title("AI Training Data Downloader")
		self.root.geometry("900x700") # smaller size
		self.root.configure(bg='#f0f0f0')

		# Variables
		self.is_downloading = False
		self.download_thread = None
		
		self.setup_gui()
	def setup_gui(self):
		# create main frame with scrollbar
		main_frame = ttk.Frame(self.root)
		main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

		# create canvas and scrollbar
		canvas = tk.Canvas(main_frame)
		scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
		scrollable_frame = ttk.Frame(canvas)

		scrollable_frame.bind(
			"<Configure>",
			lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
		)

		canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
		canvas.configure(yscrollcommand=scrollbar.set)

		canvas.pack(side="left", fill="both", expand=True)
		scrollbar.pack(side="right", fill="y")
		
		# Title - lebih kecil
		title_label = ttk.Label(scrollable_frame, text="AI Training Data Downloader",
		font=('Arial', 24, 'bold'))
		title_label.grid(row=0, column=0, columnspan=2, pady=(0,10))
		
		# Output Directory
		ttk.Label(config_frame, text="Output Folder:").grid(row=1, column=0, sticky=tk.W, pady=3)
		self.output_dir=tk.StringVar(value="training_data")
		ttk.Entry(config_frame, textvariable=self.ouput_dir, width=30, font=('Arial', 9)).grid(row=1, column=2, pady=3, padx=(5,0),
		sticky=(tk.W, tk.E))
		ttk.Button(config_frame, text="Browse", command=self.browse_folder,
		width=8).grid(row=1, column=2, padx=(5,0))
		
		config_frame.columnconfigure(1, weight=1)
		
		# == Configuration Section == 
		config_frame = ttk.LabelFrame(scrollable_frame, text="Configuration", padding=10)
		config_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), paddy=(0,10))
		
		# API KEY Location
		ttk.Label(config_frame, text="Input SerpAPI Key").grid(row=0, column=0, sticky=tk.W, pady=3)
		self.api_key = tk.StringVar()
		api_entry = ttk.Entry(config_frame, textvariable=self.api_key, width=40, font=('Arial',9))
		ttk.Button(config_frame, text="Dapatkan Kunci API", command=self.open_serpapi_website, width=8).grid(row=0, column=2, padx=(5,0))
		
		# Output Directory
		ttk.Label(config_frame, text="Output Folder:").grid(row=1, column=0, sticky=tk.W,pady=3)
		self.output_dir= tk.StringVar(value="training_data")
		ttk.Entry(config_frame, textvariable=self.output_dir, width=30, font=('Arial', 9)).grid(row=1, column=1, pady=3, padx=(5,0), sticky=(tk.W, tk.E))
		ttk.Button(config_frame, text="Browse", command=self.browse_folder, width=8).grid(row=1, column=2, padx=(5,0))
		
		config_frame.columnconfigure(1, weight=1)

		# == SEARCH PARAMETER SECTION ==
		search_frame = ttk.LabelFrame(scrollable_frame, text="Search Parameters", padding="10")
		search_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0,10))

		# Object Type
		ttk.Label(search_frame, text="Object:").grid(row=0, column=0, sticky=tk.W, pady=3)
		self.object_type = tk.StringVar(value="banana")
		object_combo = ttk.Combobox(search_frame, textvariable=self.object_type,
		values=["banana", "mango", "tomato", "apple", "orange", "custom"], state="readonly", width=12, font=('Arial',9))
		object_combo.grid(row=0, column=1, pady=3, padx=(5,0), sticky=tk.W)
		object_combo.bind('<<ComboboxSelected>>', self.on_object_change)

		# Custom object type
		ttk.Label(search_frame, text="Custom:").grid(row=0, column=2, sticky=tk.W, pady=3, padx=(10,0))
		self.custom_object = tk.StringVar()
		ttk.Entry(search_frame, textvariable=self.custom_object, width=15, font=('Arial', 9)).grid(row=3, column=3, pady=3, padx=(5,0))

		# Categories/Stages
		ttk.Label(search_frame, text="Categories:").grid(row=1, column=0, sticky=tk.W, pady=3)
		self.categories_frame = ttk.Frame(search_frame)
		self.categories_frame.grid(row=1, column=1, columnspan=3, sticky=(tk.W, tk.E), pady=3, padx=(5, 0))
        
		self.category_vars = {}
		default_categories = ["unripe", "ripe", "overripe", "fresh", "rotten"]
		for i, cat in enumerate(default_categories):
			var = tk.BooleanVar(value=(cat in ["unripe", "ripe", "overripe"]))
			self.category_vars[cat] = var
			ttk.Checkbutton(self.categories_frame, text=cat, variable=var).grid(row=0, column=i, padx=(0, 8))

		# Custom categories/stages
		ttk.Label(search_frame, text="Custom Cats:").grid(row=2, column=0, sticky=tk.W, pady=3)
		self.custom_categories = tk.StringVar()
		ttk.Entry(search_frame, textvariable=self.custom_categories, width=25, font=('Arial', 9)).grid(row=2, column=1, columnspan=2, pady=3, padx=(5, 0), sticky=(tk.W, tk.E))
		ttk.Label(search_frame, text="(use commas)").grid(row=2, column=3, sticky=tk.W, pady=3, padx=(5, 0))

		# Image per category
		ttk.Label(search_frame, text="Images/Cat:").grid(row=3, column=0, sticky=tk.W, pady=3)
		self.images_per_category = tk.IntVar(value=50)
		ttk.Spinbox(search_frame, from_=10, to=500, textvariable=self.images_per_category, width=8).grid(row=3, column=1, pady=3, padx=(5, 0))
		search_frame.columnconfigure(1, weight=1)

		# FILTER SECTION
		filter_frame = ttk.LabelFrame(scrollable_frame, text="⚙️ Filter Options", padding="10")
		filter_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

		# Line 3, size and filter
		ttk.Label(filter_frame, text="Min Size:").grid(row=0, column=0, sticky=tk.W, pady=2)
		self.min_size = tk.StringVar(value="400x400")
		size_combo = ttk.Combobox(filter_frame, textvariable=self.min_size,
                                 values=["200x200", "400x400", "600x600", "800x800"],
                                 state="readonly", width=8)
		size_combo.grid(row=0, column=1, pady=2, padx=(5, 0))
		
		self.use_color_filter = tk.BooleanVar(value=True)
		ttk.Checkbutton(filter_frame, text="Color Filter", variable=self.use_color_filter).grid(row=0, column=2, pady=2, padx=(10, 0))
		self.safe_search = tk.BooleanVar(value=True)
		ttk.Checkbutton(filter_frame, text="Safe Search", variable=self.safe_search).grid(row=0, column=3, pady=2, padx=(10, 0))
		
		# Line 2, type and delay
		ttk.Label(filter_frame, text="Image Type:").grid(row=1, column=0, sticky=tk.W, pady=2)
		self.image_type = tk.StringVar(value="photo")
		type_combo = ttk.Combobox(filter_frame, textvariable=self.image_type,
                                 values=["photo", "clipart", "lineart", "face"],
                                 state="readonly", width=8)
		type_combo.grid(row=1, column=1, pady=2, padx=(5, 0))
		
		ttk.Label(filter_frame, text="Delay:").grid(row=1, column=2, sticky=tk.W, pady=2, padx=(10, 0))
		self.download_delay = tk.DoubleVar(value=0.5)
		ttk.Spinbox(filter_frame, from_=0.1, to=5.0, increment=0.1, 
                   textvariable=self.download_delay, width=6).grid(row=1, column=3, pady=2, padx=(5, 0))
                   
		# == BUTTON CONTROL ==
		button_frame = ttk.Frame(scrollable_frame)
		button_frame.grid(row=4, column=0, columnspan=2, pady=10)
		
		# START BUTTON
		self.start_button = ttk.Button(
		button_frame,
		text="Start Download",
		command=self.start_download,
		width=20)
		self.start_button.grid(row=0, column=0, padx=5)
		# STOP BUTTON
		self.stop_button = ttk.Button(
		button_frame,
		text="STOP",
		command=self.stop_download,
		status='disabled',
		width=10)
		self.stop_button.grid(row=0, column=1, padx=5)
		# CLEAR LOG BUTTON
		ttk.Button(
		button_frame,
		text="Clear Log",
		command=self.clear_log,
		width=10).grid(row=0, column=2, padx=5)
		# OPEN FOLDER BUTTON
		ttk.Button(
		button_frame,
		text="Open Folder",
		command=self.open_output_folder,
		width=10).grid(row=0, column=3, padx=5)
		
		# == PROGRESS SECTION == 
		progress_frame = ttk.LabelFrame(scrollable_frame, text="📊 Progress", padding="10")
		progress_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
		
		
		# progress bar compact
		ttk.Label(progress_frame, text="Overall:").grid(row=0, column=0, sticky=tk.W, pady=2)
		self.overall_progress = ttk.Progressbar(progress_frame, mode='determinate')
		self.overall_progress.grid(row=0, column=1, columnspan=3, sticky=(tk.W, tk.E), pady=2)
		
		ttk.Label(progress_frame, text="Current:").grid(row=1, column=0, sticky=tk.W, pady=2)
		self.current_progress = ttk.Progressbar(progress_frame, mode='determinate')
		self.current_progress.grid(row=1, column=1, columnspan=3, sticky=(tk.W, tk.E), pady=2)
		
		# status label compact
		self.overall_status = ttk.Label(progress_frame, text="Ready to start...", font=('Arial', 9))
		self.overall_status.grid(row=2, column=0, columnspan=4, sticky=tk.W, pady=3)
        
		self.current_status = ttk.Label(progress_frame, text="", font=('Arial', 8))
		self.current_status.grid(row=3, column=0, columnspan=4, sticky=tk.W, pady=1)
		
		self.stats_label = ttk.Label(progress_frame, text="", font=('Arial', 8, 'bold'))
		self.stats_label.grid(row=4, column=0, columnspan=4, sticky=tk.W, pady=1)
		
		# log area smaller
		ttk.Label(progress_frame, text="Log:", font=('Arial', 9, 'bold')).grid(row=5, column=0, sticky=tk.W, pady=(8, 2))
		log_frame = ttk.Frame(progress_frame)
		log_frame.grid(row=6, column=0, columnspan=4, sticky=(tk.W, tk.E, tk.N, tk.S), pady=2)
		self.log_text = tk.Text(log_frame, height=6, width=70, font=('Consolas', 8))
		self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
		log_scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
		log_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
		self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        # Configure grid weights for more responsive layout
		scrollable_frame.columnconfigure(0, weight=1)
		progress_frame.columnconfigure(1, weight=1)
		log_frame.columnconfigure(0, weight=1)
		log_frame.rowconfigure(0, weight=1)
		
		# Initialize
		self.log("🌟 AI Training Data Downloader Ready!")
		self.log("➡️ Configure parameters and click START DOWNLOAD")
		self.log("➡️ Get API key from: https://serpapi.com")
		
		def on_object_change(self, event):
			if self.object_type.get() == "custom":
				self.custom_object.set("")
				self.custom_object.focus()
			else:
				self.custom_object.set("")
    
	def open_serpapi_website(self):
		import webbrowser
		webbrowser.open("https://serpapi.com")
		self.log("🌐 Opening SerpAPI website...")
		
	def browse_folder(self):
		folder = filedialog.askdirectory()
		if folder:
			self.output_dir.set(folder)
			self.log(f"📁 Output folder: {folder}")
    
	def log(self, message):
		timestamp = datetime.now().strftime("%H:%M:%S")
		log_entry = f"[{timestamp}] {message}\n"
		self.log_text.insert(tk.END, log_entry)
		self.log_text.see(tk.END)
		self.root.update_idletasks()
    
	def clear_log(self):
		self.log_text.delete(1.0, tk.END)
		self.log("Log cleared - Ready for new download")
    
	def open_output_folder(self):
		output_path = self.output_dir.get()
		if os.path.exists(output_path):
			try:
				os.startfile(output_path)
				self.log(f"📂 Opened: {output_path}")
			except:
				self.log("❌ Could not open folder")
		else:
			messagebox.showwarning("Warning", "Output folder doesn't exist yet!")
		
	def start_download(self):
		# Validasi input
		if not self.api_key.get():
			messagebox.showerror("Error", "Please enter your SerpAPI key!\nGet free key from: https://serpapi.com")
			return
		if not self.output_dir.get():
			messagebox.showerror("Error", "Please select output directory!")
			return

		# Get selected categories
		categories = []
		for cat, var in self.category_vars.items():
			if var.get():
				categories.append(cat)
		
		# Add custom categories
		custom_cats = [cat.strip() for cat in self.custom_categories.get().split(',') if cat.strip()]
		categories.extend(custom_cats)
		
		if not categories:
			messagebox.showerror("Error", "Please select at least one category!")
			return
		# Get object type
		obj_type = self.custom_object.get() if self.object_type.get() == "custom" else self.object_type.get()
		if not obj_type:
			messagebox.showerror("Error", "Please specify object type!")
			return
			
		# Confirmation
		total_images = len(categories) * self.images_per_category.get()
		confirm = messagebox.askyesno("Confirm Download", f"Start downloading?\n\nObject: {obj_type}\nCategories: {', '.join(categories)}\nImages: {self.images_per_category.get()} per category\nTotal: {total_images} images"
        )
        
		if not confirm:
			return
			
		# Setup download
		self.is_downloading = True
		self.start_button.config(state='disabled')
		self.stop_button.config(state='normal')
		
		# Reset progress
		self.overall_progress['value'] = 0
		self.current_progress['value'] = 0
		
		
		
		
		
