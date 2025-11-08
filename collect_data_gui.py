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
