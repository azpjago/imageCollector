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
urllib3.disable_warnings(urllib3.exceptions.InsercureRequestWarning)
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
