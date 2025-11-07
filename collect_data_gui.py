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
		font=('Arial', 24, 'bold')
		title_label.grid(row=0, column=0, columnspan=2, pady=(0,10))
		
		# == Configuration Section == 
		config_frame = ttk.LabelFrame(scrollable_frame, text="Configuration", padding=10)
		config_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), paddy=(0,10))
		
		# API KEY Location
		ttk.Label(config_frame, text="Input SerpAPI Key").grid(row=0, column=0, sticky=tk.W, pady=3)
		self.api_key = tk.StringVar()
		api_entry = ttk.Entry(config_frame, textvariable=self.api_key, width=40, font=('Arial',9))
		ttk.Button(config_frame, text="Dapatkan Kunci API", command=self.open_serpapi_website, width=8).grid(row=0, column=2, padx=(5,0))
		
		
