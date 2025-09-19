"""
Youtubers Life Save Editor - Custom GUI for Youtubers Life Save Files
Designed to match the game's save data structure with all major tables and sections
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import re
import os
from typing import Dict, List, Any, Optional
import threading

# Import our existing TSE functions
try:
    import tse
except ImportError:
    print("tse.py module not found - some encode/decode features will be unavailable")
    tse = None

class YoutubersLifeSaveEditor:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Youtubers Life Save Editor")
        self.root.geometry("1400x900")
        self.root.minsize(1000, 700)
        
        # Data storage
        self.save_data = {}
        self.tables = {}
        self.table_headers = {}  # Store original column order
        self.current_file = None
        self.modified = False
        
        # Create UI
        self.setup_styles()
        self.create_menu_bar()
        self.create_main_interface()
        
    def setup_styles(self):
        """Setup custom styles for the interface"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure custom styles
        style.configure('Title.TLabel', font=('Arial', 12, 'bold'))
        style.configure('Header.TLabel', font=('Arial', 10, 'bold'))
        style.configure('MainTab.TNotebook', tabposition='n')
        
    def create_menu_bar(self):
        """Create the menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open Save File (.yls)", command=self.open_save_file)
        file_menu.add_command(label="Open Decoded File (.txt)", command=self.open_decoded_file)
        file_menu.add_separator()
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_command(label="Save As...", command=self.save_file_as)
        file_menu.add_separator()
        file_menu.add_command(label="Export to Text", command=self.export_to_text)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Decode YLS File", command=self.decode_yls_file)
        tools_menu.add_command(label="Encode to YLS", command=self.encode_to_yls)
        tools_menu.add_separator()
        tools_menu.add_command(label="Validate Save Data", command=self.validate_save_data)
        tools_menu.add_command(label="Backup Current File", command=self.backup_file)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Refresh All", command=self.refresh_all_tabs)
        view_menu.add_command(label="Expand All Trees", command=self.expand_all_trees)
        view_menu.add_command(label="Collapse All Trees", command=self.collapse_all_trees)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        
    def create_main_interface(self):
        """Create the main interface with tabs"""
        # Status bar
        self.status_bar = ttk.Label(self.root, text="No file loaded", relief=tk.SUNKEN)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Main notebook for tabs
        self.main_notebook = ttk.Notebook(self.root, style='MainTab.TNotebook')
        self.main_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create all tabs
        self.create_overview_tab()
        self.create_character_tab()
        self.create_channel_tab()
        self.create_videos_tab()
        self.create_gaming_tab()
        self.create_social_tab()
        self.create_inventory_tab()
        self.create_progression_tab()
        self.create_raw_data_tab()
        
    def create_overview_tab(self):
        """Create overview tab with general save information"""
        frame = ttk.Frame(self.main_notebook)
        self.main_notebook.add(frame, text="Overview")
        
        # Main info frame
        info_frame = ttk.LabelFrame(frame, text="Save Game Information", padding=10)
        info_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Save game details
        ttk.Label(info_frame, text="Save Name:", style='Header.TLabel').grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.save_name_var = tk.StringVar()
        self.save_name_var.trace('w', self.on_data_changed)
        self.save_name_entry = ttk.Entry(info_frame, textvariable=self.save_name_var, width=40)
        self.save_name_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(info_frame, text="Current Date:", style='Header.TLabel').grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.current_date_var = tk.StringVar()
        self.current_date_var.trace('w', self.on_data_changed)
        self.current_date_entry = ttk.Entry(info_frame, textvariable=self.current_date_var, width=20)
        self.current_date_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(info_frame, text="Money:", style='Header.TLabel').grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        self.money_var = tk.StringVar()
        self.money_var.trace('w', self.on_data_changed)
        self.money_entry = ttk.Entry(info_frame, textvariable=self.money_var, width=20)
        self.money_entry.grid(row=2, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(info_frame, text="House:", style='Header.TLabel').grid(row=3, column=0, sticky=tk.W, padx=5, pady=2)
        self.house_var = tk.StringVar()
        self.house_var.trace('w', self.on_data_changed)
        self.house_combo = ttk.Combobox(info_frame, textvariable=self.house_var, width=37)
        self.house_combo['values'] = ['1 - Starting House', '2 - Upgraded House']
        self.house_combo.grid(row=3, column=1, sticky=tk.W, padx=5, pady=2)
        
        # Statistics frame
        stats_frame = ttk.LabelFrame(frame, text="Game Statistics", padding=10)
        stats_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create treeview for statistics
        self.stats_tree = ttk.Treeview(stats_frame, columns=('Value',), height=15)
        self.stats_tree.heading('#0', text='Statistic')
        self.stats_tree.heading('Value', text='Value')
        self.stats_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbar for stats
        stats_scrollbar = ttk.Scrollbar(stats_frame, orient=tk.VERTICAL, command=self.stats_tree.yview)
        stats_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.stats_tree.configure(yscrollcommand=stats_scrollbar.set)
        
    def create_character_tab(self):
        """Create character tab with player data and skills"""
        frame = ttk.Frame(self.main_notebook)
        self.main_notebook.add(frame, text="Character")
        
        # Left frame for basic character info
        left_frame = ttk.LabelFrame(frame, text="Character Information", padding=10)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 5), pady=10)
        
        # Character name
        ttk.Label(left_frame, text="Name:", style='Header.TLabel').grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.char_name_var = tk.StringVar()
        self.char_name_var.trace('w', self.on_data_changed)
        self.char_name_entry = ttk.Entry(left_frame, textvariable=self.char_name_var, width=30)
        self.char_name_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        
        # Character stats
        stats_labels = ['Energy', 'Hunger', 'Social Life', 'Motivation']
        self.char_stats_vars = {}
        
        for i, stat in enumerate(stats_labels):
            ttk.Label(left_frame, text=f"{stat}:", style='Header.TLabel').grid(row=i+1, column=0, sticky=tk.W, padx=5, pady=2)
            var = tk.IntVar()
            var.trace('w', self.on_data_changed)
            self.char_stats_vars[stat.lower().replace(' ', '_')] = var
            scale = ttk.Scale(left_frame, from_=0, to=100, orient=tk.HORIZONTAL, variable=var, length=200)
            scale.grid(row=i+1, column=1, sticky=tk.W, padx=5, pady=2)
            
            # Value label
            value_label = ttk.Label(left_frame, textvariable=var)
            value_label.grid(row=i+1, column=2, padx=5, pady=2)
        
        # Skills section
        skills_label = ttk.Label(left_frame, text="Skills:", style='Header.TLabel')
        skills_label.grid(row=6, column=0, columnspan=3, sticky=tk.W, padx=5, pady=(15, 5))
        
        skill_names = ['Scripting', 'Acting', 'Sound', 'Editing', 'Effects']
        self.skill_vars = {}
        
        for i, skill in enumerate(skill_names):
            ttk.Label(left_frame, text=f"{skill}:", style='Header.TLabel').grid(row=i+7, column=0, sticky=tk.W, padx=5, pady=2)
            var = tk.DoubleVar()
            var.trace('w', self.on_data_changed)
            self.skill_vars[skill.lower()] = var
            entry = ttk.Entry(left_frame, textvariable=var, width=10)
            entry.grid(row=i+7, column=1, sticky=tk.W, padx=5, pady=2)
        
        # Right frame for experience and progression
        right_frame = ttk.LabelFrame(frame, text="Experience & Progression", padding=10)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 10), pady=10)
        
        # Experience treeview
        self.exp_tree = ttk.Treeview(right_frame, columns=('Level', 'Experience'), height=20)
        self.exp_tree.heading('#0', text='Category')
        self.exp_tree.heading('Level', text='Level')
        self.exp_tree.heading('Experience', text='Experience')
        self.exp_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbar
        exp_scrollbar = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=self.exp_tree.yview)
        exp_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.exp_tree.configure(yscrollcommand=exp_scrollbar.set)
        
    def create_channel_tab(self):
        """Create channel management tab"""
        frame = ttk.Frame(self.main_notebook)
        self.main_notebook.add(frame, text="Channel")
        
        # Channel info frame
        info_frame = ttk.LabelFrame(frame, text="Channel Information", padding=10)
        info_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Channel details
        ttk.Label(info_frame, text="Channel Name:", style='Header.TLabel').grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.channel_name_var = tk.StringVar()
        self.channel_name_var.trace('w', self.on_data_changed)
        self.channel_name_entry = ttk.Entry(info_frame, textvariable=self.channel_name_var, width=40)
        self.channel_name_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(info_frame, text="Subscribers:", style='Header.TLabel').grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.subscribers_var = tk.IntVar()
        self.subscribers_var.trace('w', self.on_data_changed)
        self.subscribers_entry = ttk.Entry(info_frame, textvariable=self.subscribers_var, width=20)
        self.subscribers_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(info_frame, text="Total Views:", style='Header.TLabel').grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        self.total_views_var = tk.IntVar()
        self.total_views_var.trace('w', self.on_data_changed)
        self.total_views_entry = ttk.Entry(info_frame, textvariable=self.total_views_var, width=20)
        self.total_views_entry.grid(row=2, column=1, sticky=tk.W, padx=5, pady=2)
        
        # Channel stats frame
        stats_frame = ttk.LabelFrame(frame, text="Channel Statistics", padding=10)
        stats_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Channel stats treeview
        self.channel_tree = ttk.Treeview(stats_frame, height=15)
        self.channel_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        channel_scrollbar = ttk.Scrollbar(stats_frame, orient=tk.VERTICAL, command=self.channel_tree.yview)
        channel_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.channel_tree.configure(yscrollcommand=channel_scrollbar.set)
        
    def create_videos_tab(self):
        """Create video management tab"""
        frame = ttk.Frame(self.main_notebook)
        self.main_notebook.add(frame, text="Videos")
        
        # Video list frame
        list_frame = ttk.LabelFrame(frame, text="Video List", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Video treeview
        self.videos_tree = ttk.Treeview(list_frame, columns=('Title', 'Type', 'Views', 'Likes', 'Dislikes', 'Money'), height=20)
        self.videos_tree.heading('#0', text='ID')
        self.videos_tree.heading('Title', text='Title')
        self.videos_tree.heading('Type', text='Type')
        self.videos_tree.heading('Views', text='Views')
        self.videos_tree.heading('Likes', text='Likes')
        self.videos_tree.heading('Dislikes', text='Dislikes')
        self.videos_tree.heading('Money', text='Money')
        
        # Column widths
        self.videos_tree.column('#0', width=50)
        self.videos_tree.column('Title', width=200)
        self.videos_tree.column('Type', width=100)
        self.videos_tree.column('Views', width=100)
        self.videos_tree.column('Likes', width=80)
        self.videos_tree.column('Dislikes', width=80)
        self.videos_tree.column('Money', width=80)
        
        self.videos_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        videos_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.videos_tree.yview)
        videos_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.videos_tree.configure(yscrollcommand=videos_scrollbar.set)
        
    def create_gaming_tab(self):
        """Create gaming-related data tab"""
        frame = ttk.Frame(self.main_notebook)
        self.main_notebook.add(frame, text="Gaming")
        
        # Gaming platforms frame
        platforms_frame = ttk.LabelFrame(frame, text="Gaming Platforms Owned", padding=10)
        platforms_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.platforms_tree = ttk.Treeview(platforms_frame, columns=('Active',), height=8)
        self.platforms_tree.heading('#0', text='Platform')
        self.platforms_tree.heading('Active', text='Active')
        self.platforms_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        platforms_scrollbar = ttk.Scrollbar(platforms_frame, orient=tk.VERTICAL, command=self.platforms_tree.yview)
        platforms_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.platforms_tree.configure(yscrollcommand=platforms_scrollbar.set)
        
        # Gaming games frame
        games_frame = ttk.LabelFrame(frame, text="Games Owned", padding=10)
        games_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.games_tree = ttk.Treeview(games_frame, columns=('Platform', 'State', 'Rating', 'Price'), height=12)
        self.games_tree.heading('#0', text='Game')
        self.games_tree.heading('Platform', text='Platform')
        self.games_tree.heading('State', text='State')
        self.games_tree.heading('Rating', text='Rating')
        self.games_tree.heading('Price', text='Price')
        
        self.games_tree.column('#0', width=250)
        self.games_tree.column('Platform', width=150)
        self.games_tree.column('State', width=100)
        self.games_tree.column('Rating', width=80)
        self.games_tree.column('Price', width=80)
        
        self.games_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        games_scrollbar = ttk.Scrollbar(games_frame, orient=tk.VERTICAL, command=self.games_tree.yview)
        games_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.games_tree.configure(yscrollcommand=games_scrollbar.set)
        
    def create_social_tab(self):
        """Create social network and friends tab"""
        frame = ttk.Frame(self.main_notebook)
        self.main_notebook.add(frame, text="Social")
        
        # Friends frame
        friends_frame = ttk.LabelFrame(frame, text="Friends & Relationships", padding=10)
        friends_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 5))
        
        self.friends_tree = ttk.Treeview(friends_frame, columns=('Relation', 'Level', 'Affinity'), height=15)
        self.friends_tree.heading('#0', text='Friend')
        self.friends_tree.heading('Relation', text='Relation')
        self.friends_tree.heading('Level', text='Level')
        self.friends_tree.heading('Affinity', text='Affinity')
        
        self.friends_tree.column('#0', width=150)
        self.friends_tree.column('Relation', width=100)
        self.friends_tree.column('Level', width=80)
        self.friends_tree.column('Affinity', width=80)
        
        self.friends_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        friends_scrollbar = ttk.Scrollbar(friends_frame, orient=tk.VERTICAL, command=self.friends_tree.yview)
        friends_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.friends_tree.configure(yscrollcommand=friends_scrollbar.set)
        
        # Social network posts frame
        social_frame = ttk.LabelFrame(frame, text="Social Network Posts", padding=10)
        social_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(5, 10))
        
        self.social_tree = ttk.Treeview(social_frame, columns=('Date', 'Likes', 'Dislikes'), height=10)
        self.social_tree.heading('#0', text='Message')
        self.social_tree.heading('Date', text='Date')
        self.social_tree.heading('Likes', text='Likes')
        self.social_tree.heading('Dislikes', text='Dislikes')
        
        self.social_tree.column('#0', width=400)
        self.social_tree.column('Date', width=100)
        self.social_tree.column('Likes', width=80)
        self.social_tree.column('Dislikes', width=80)
        
        self.social_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        social_scrollbar = ttk.Scrollbar(social_frame, orient=tk.VERTICAL, command=self.social_tree.yview)
        social_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.social_tree.configure(yscrollcommand=social_scrollbar.set)
        
    def create_inventory_tab(self):
        """Create inventory and items tab"""
        frame = ttk.Frame(self.main_notebook)
        self.main_notebook.add(frame, text="Inventory")
        
        # Technology owned frame
        tech_frame = ttk.LabelFrame(frame, text="Technology & Equipment", padding=10)
        tech_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.tech_tree = ttk.Treeview(tech_frame, columns=('Active', 'Lifetime', 'Config'), height=20)
        self.tech_tree.heading('#0', text='Item')
        self.tech_tree.heading('Active', text='Active')
        self.tech_tree.heading('Lifetime', text='Lifetime')
        self.tech_tree.heading('Config', text='Config')
        
        self.tech_tree.column('#0', width=200)
        self.tech_tree.column('Active', width=80)
        self.tech_tree.column('Lifetime', width=100)
        self.tech_tree.column('Config', width=80)
        
        self.tech_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        tech_scrollbar = ttk.Scrollbar(tech_frame, orient=tk.VERTICAL, command=self.tech_tree.yview)
        tech_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tech_tree.configure(yscrollcommand=tech_scrollbar.set)
        
    def create_progression_tab(self):
        """Create progression and achievements tab"""
        frame = ttk.Frame(self.main_notebook)
        self.main_notebook.add(frame, text="Progress")
        
        # Missions frame
        missions_frame = ttk.LabelFrame(frame, text="Missions & Objectives", padding=10)
        missions_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 5))
        
        self.missions_tree = ttk.Treeview(missions_frame, columns=('Progress', 'Complete', 'Milestone'), height=12)
        self.missions_tree.heading('#0', text='Mission')
        self.missions_tree.heading('Progress', text='Progress')
        self.missions_tree.heading('Complete', text='Complete')
        self.missions_tree.heading('Milestone', text='Milestone')
        
        self.missions_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        missions_scrollbar = ttk.Scrollbar(missions_frame, orient=tk.VERTICAL, command=self.missions_tree.yview)
        missions_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.missions_tree.configure(yscrollcommand=missions_scrollbar.set)
        
        # Talent tree frame
        talent_frame = ttk.LabelFrame(frame, text="Talent Tree", padding=10)
        talent_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(5, 10))
        
        self.talent_tree = ttk.Treeview(talent_frame, columns=('Rank',), height=12)
        self.talent_tree.heading('#0', text='Talent')
        self.talent_tree.heading('Rank', text='Rank')
        
        self.talent_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        talent_scrollbar = ttk.Scrollbar(talent_frame, orient=tk.VERTICAL, command=self.talent_tree.yview)
        talent_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.talent_tree.configure(yscrollcommand=talent_scrollbar.set)
        
    def create_raw_data_tab(self):
        """Create raw data view tab"""
        frame = ttk.Frame(self.main_notebook)
        self.main_notebook.add(frame, text="Raw Data")
        
        # Table selection frame
        selection_frame = ttk.LabelFrame(frame, text="Select Table", padding=10)
        selection_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(selection_frame, text="Table:", style='Header.TLabel').pack(side=tk.LEFT, padx=5)
        
        self.table_var = tk.StringVar()
        self.table_combo = ttk.Combobox(selection_frame, textvariable=self.table_var, width=40, state='readonly')
        self.table_combo.pack(side=tk.LEFT, padx=5)
        self.table_combo.bind('<<ComboboxSelected>>', self.on_table_selected)
        
        # Refresh button
        ttk.Button(selection_frame, text="Refresh", command=self.refresh_table_data).pack(side=tk.LEFT, padx=10)
        
        # Raw data frame
        raw_frame = ttk.LabelFrame(frame, text="Raw Table Data", padding=10)
        raw_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create treeview for raw data
        self.raw_tree = ttk.Treeview(raw_frame)
        self.raw_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        raw_scrollbar_v = ttk.Scrollbar(raw_frame, orient=tk.VERTICAL, command=self.raw_tree.yview)
        raw_scrollbar_v.pack(side=tk.RIGHT, fill=tk.Y)
        self.raw_tree.configure(yscrollcommand=raw_scrollbar_v.set)
        
        raw_scrollbar_h = ttk.Scrollbar(frame, orient=tk.HORIZONTAL, command=self.raw_tree.xview)
        raw_scrollbar_h.pack(side=tk.BOTTOM, fill=tk.X)
        self.raw_tree.configure(xscrollcommand=raw_scrollbar_h.set)
        
    def open_save_file(self):
        """Open a .yls save file"""
        filename = filedialog.askopenfilename(
            title="Open Youtubers Life Save File",
            filetypes=[("Youtubers Life Save", "*.yls"), ("All files", "*.*")]
        )
        
        if filename:
            self.status_bar.config(text="Loading save file...")
            self.root.update()
            
            try:
                if tse:
                    # Decode the file first
                    with open(filename, 'r', encoding='utf-8') as f:
                        encoded_data = f.read()
                    
                    # Use the correct function from tse module
                    decoded_bytes = tse.decode_base64_gzip(encoded_data)
                    decoded_data = decoded_bytes.decode('utf-8')
                    self.load_decoded_data(decoded_data)
                    self.current_file = filename
                    self.status_bar.config(text=f"Loaded: {os.path.basename(filename)}")
                else:
                    messagebox.showerror("Error", "TSE module not available. Cannot decode .yls files.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load save file: {str(e)}")
                self.status_bar.config(text="Load failed")
    
    def open_decoded_file(self):
        """Open a decoded .txt file"""
        filename = filedialog.askopenfilename(
            title="Open Decoded Save File",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            self.status_bar.config(text="Loading decoded file...")
            self.root.update()
            
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    decoded_data = f.read()
                
                self.load_decoded_data(decoded_data)
                self.current_file = filename
                self.status_bar.config(text=f"Loaded: {os.path.basename(filename)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load decoded file: {str(e)}")
                self.status_bar.config(text="Load failed")
    
    def on_data_changed(self, *args):
        """Called when any data field is modified"""
        if hasattr(self, 'tables') and self.tables:  # Only track changes if data is loaded
            self.modified = True
            self.update_window_title()
    
    def update_window_title(self):
        """Update window title to show file name and modified status"""
        title = "Youtubers Life Save Editor"
        if self.current_file:
            filename = os.path.basename(self.current_file)
            title += f" - {filename}"
        if self.modified:
            title += " *"
        self.root.title(title)
    
    def load_decoded_data(self, data: str):
        """Parse and load decoded save data"""
        try:
            self.tables = self.parse_save_data(data)
            self.populate_all_tabs()
            self.modified = False
            self.update_table_combo()
            self.update_window_title()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to parse save data: {str(e)}")
    
    def parse_save_data(self, data: str) -> Dict[str, List[Dict[str, Any]]]:
        """Parse the decoded save data into structured format"""
        tables = {}
        table_headers = {}  # Store original header order
        current_table = None
        current_headers = []
        
        lines = data.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check if this is a table header (starts with ###)
            if line.startswith('###'):
                current_table = line[3:]
                tables[current_table] = []
                current_headers = []
                continue
            
            # Skip lines that are just numbers or don't have proper structure
            if current_table is None:
                continue
            
            # Split by tabs
            parts = line.split('\t')
            
            # If we don't have headers yet and this looks like a header row
            if not current_headers and len(parts) > 1:
                current_headers = parts
                table_headers[current_table] = parts  # Store original order
                continue
            
            # If we have headers and this is a data row
            if current_headers and len(parts) <= len(current_headers):
                # Pad with empty strings if some columns are missing
                while len(parts) < len(current_headers):
                    parts.append('')
                
                row = {}
                for i, header in enumerate(current_headers):
                    value = parts[i] if i < len(parts) else ''
                    # Try to convert to appropriate type
                    try:
                        if '.' in value and value.replace('.', '').replace('-', '').isdigit():
                            row[header] = float(value)
                        elif value.isdigit() or (value.startswith('-') and value[1:].isdigit()):
                            row[header] = int(value)
                        else:
                            row[header] = value
                    except:
                        row[header] = value
                
                tables[current_table].append(row)
        
        # Store the header order for use in saving
        self.table_headers = table_headers
        return tables
    
    def populate_all_tabs(self):
        """Populate all tabs with data"""
        self.populate_overview_tab()
        self.populate_character_tab()
        self.populate_channel_tab()
        self.populate_videos_tab()
        self.populate_gaming_tab()
        self.populate_social_tab()
        self.populate_inventory_tab()
        self.populate_progression_tab()
    
    def populate_overview_tab(self):
        """Populate overview tab with save game data"""
        if 'Savegame' in self.tables and self.tables['Savegame']:
            savegame = self.tables['Savegame'][0]
            self.save_name_var.set(savegame.get('Name', ''))
            self.current_date_var.set(str(savegame.get('Current_date', '')))
            self.money_var.set(str(savegame.get('Money', '')))
            self.house_var.set(str(savegame.get('House', '')))
        
        # Clear and populate stats tree
        for item in self.stats_tree.get_children():
            self.stats_tree.delete(item)
        
        # Add various statistics from different tables
        if 'Player_data' in self.tables:
            self.stats_tree.insert('', 'end', text='Player Data', open=True)
            for row in self.tables['Player_data']:
                name = row.get('Name_field', 'Unknown')
                value = row.get('Value_field', '')
                self.stats_tree.insert('', 'end', text=f"  {name}", values=(value,))
    
    def populate_character_tab(self):
        """Populate character tab with youtuber data"""
        if 'Youtuber' in self.tables:
            # Find the player character (player_controlled = 0)
            player_data = None
            for youtuber in self.tables['Youtuber']:
                if youtuber.get('Player_controlled') == 0:
                    player_data = youtuber
                    break
            
            if player_data:
                self.char_name_var.set(player_data.get('Name', ''))
                
                # Set character stats
                stat_fields = {
                    'energy': 'Energy',
                    'hunger': 'Hunger',
                    'social_life': 'Social_life',
                    'motivation': 'Motivation'
                }
                
                for var_name, field_name in stat_fields.items():
                    if var_name in self.char_stats_vars:
                        self.char_stats_vars[var_name].set(player_data.get(field_name, 0))
                
                # Set skills
                skill_fields = {
                    'scripting': 'Scripting',
                    'acting': 'Acting',
                    'sound': 'Sound',
                    'editing': 'Editing',
                    'effects': 'Effects'
                }
                
                for var_name, field_name in skill_fields.items():
                    if var_name in self.skill_vars:
                        self.skill_vars[var_name].set(player_data.get(field_name, 0.0))
        
        # Populate experience tree
        for item in self.exp_tree.get_children():
            self.exp_tree.delete(item)
        
        if 'Youtuber' in self.tables:
            for youtuber in self.tables['Youtuber']:
                if youtuber.get('Player_controlled') == 0:  # Player character
                    # Add experience categories
                    categories = {
                        'Gaming': ('Gaming', 'Gaming_exp'),
                        'Cooking': ('Cooking', 'Cooking_exp'),
                        'Life': ('Life', 'Life_exp'),
                        'Music': ('Music', 'Music_exp'),
                        'Fashion': ('Fashion', 'Fashion_exp'),
                        'Main': ('Main_level', 'Main_exp')
                    }
                    
                    for cat_name, (level_field, exp_field) in categories.items():
                        level = youtuber.get(level_field, 0)
                        exp = youtuber.get(exp_field, 0)
                        self.exp_tree.insert('', 'end', text=cat_name, values=(level, exp))
    
    def populate_channel_tab(self):
        """Populate channel tab with channel data"""
        if 'Channel' in self.tables:
            # Find the player's channel by matching youtuber ID
            player_channel = None
            player_youtuber_id = None
            
            # First, find the player's youtuber ID
            if 'Youtuber' in self.tables:
                for youtuber in self.tables['Youtuber']:
                    if youtuber.get('Player_controlled') == 0:  # Player character
                        player_youtuber_id = youtuber.get('Id', 1)  # Default to 1 if not found
                        break
            
            # If we didn't find player youtuber ID, assume it's 1
            if player_youtuber_id is None:
                player_youtuber_id = 1
            
            # Now find the channel that belongs to this youtuber
            for channel in self.tables['Channel']:
                if str(channel.get('Id_youtuber', '')) == str(player_youtuber_id):
                    player_channel = channel
                    break
            
            # If still no channel found, use the first one as fallback
            if not player_channel and self.tables['Channel']:
                player_channel = self.tables['Channel'][0]
            
            if player_channel:
                self.channel_name_var.set(player_channel.get('Name', ''))
                self.subscribers_var.set(int(player_channel.get('Subscribers', 0)))
                self.total_views_var.set(int(player_channel.get('Views', 0)))
        
        # Clear and populate channel stats tree with proper columns
        for item in self.channel_tree.get_children():
            self.channel_tree.delete(item)
        
        # Configure columns for channel stats
        self.channel_tree['columns'] = ('Day', 'Views', 'Subs', 'Likes', 'Dislikes', 'Money')
        self.channel_tree.heading('#0', text='Channel ID')
        self.channel_tree.heading('Day', text='Day')
        self.channel_tree.heading('Views', text='Views')
        self.channel_tree.heading('Subs', text='Subs')
        self.channel_tree.heading('Likes', text='Likes')
        self.channel_tree.heading('Dislikes', text='Dislikes')
        self.channel_tree.heading('Money', text='Money')
        
        # Set column widths
        self.channel_tree.column('#0', width=100)
        self.channel_tree.column('Day', width=60)
        self.channel_tree.column('Views', width=80)
        self.channel_tree.column('Subs', width=80)
        self.channel_tree.column('Likes', width=60)
        self.channel_tree.column('Dislikes', width=60)
        self.channel_tree.column('Money', width=80)
        
        if 'Channel_stats' in self.tables and player_channel:
            # Show stats only for the player's channel
            player_channel_id = player_channel.get('Id', '')
            channel_stats = []
            
            for stats in self.tables['Channel_stats']:
                if str(stats.get('Id_channel', '')) == str(player_channel_id):
                    channel_stats.append(stats)
            
            if channel_stats:
                # Sort by day and take last 20 entries
                channel_stats.sort(key=lambda x: int(x.get('Day', 0)))
                recent_stats = channel_stats[-20:] if len(channel_stats) > 20 else channel_stats
                
                # Insert parent node for the player's channel
                parent = self.channel_tree.insert('', 'end', text=f'Channel {player_channel_id} ({player_channel.get("Name", "")})', open=True)
                
                for stats in recent_stats:
                    day = stats.get('Day', 0)
                    views = stats.get('Views', 0)
                    subs = stats.get('Subs', 0)
                    likes = stats.get('Likes', 0)
                    dislikes = stats.get('Dislikes', 0)
                    money = float(stats.get('Money', 0))
                    
                    self.channel_tree.insert(parent, 'end', text=f'Day {day}',
                                           values=(day, views, subs, likes, dislikes, f'{money:.2f}'))
    
    def populate_videos_tab(self):
        """Populate videos tab with video data"""
        for item in self.videos_tree.get_children():
            self.videos_tree.delete(item)
        
        if 'Video' in self.tables:
            video_types = {
                1: 'Tutorial',
                4: 'Gameplay',
                7: 'Walkthrough',
                10: 'Unboxing'
            }
            
            for video in self.tables['Video']:
                video_id = video.get('Id', '')
                title = video.get('Title', '')
                video_type = video_types.get(video.get('Video_type', 0), 'Unknown')
                views = video.get('Views', 0)
                likes = video.get('Likes', 0)
                dislikes = video.get('Dislikes', 0)
                money = video.get('Money', 0)
                
                self.videos_tree.insert('', 'end', text=video_id, 
                                      values=(title, video_type, views, likes, dislikes, money))
    
    def populate_gaming_tab(self):
        """Populate gaming tab with gaming data"""
        # Populate platforms
        for item in self.platforms_tree.get_children():
            self.platforms_tree.delete(item)
        
        if 'Gaming_platforms_owned' in self.tables:
            platform_names = {
                13: 'Mantendo D-ESS',
                14: 'Mantendo D-ESS',
                16: 'Honey PeeEsPee',
                24: 'Honey PlayStudios 2',
                32: 'HAL PC'
            }
            
            for platform in self.tables['Gaming_platforms_owned']:
                platform_id = platform.get('Id_platform', 0)
                platform_name = platform_names.get(platform_id, f'Platform {platform_id}')
                active = 'Yes' if platform.get('Active', 0) == 1 else 'No'
                
                self.platforms_tree.insert('', 'end', text=platform_name, values=(active,))
        
        # Populate games
        for item in self.games_tree.get_children():
            self.games_tree.delete(item)
        
        if 'Gaming_game_owned' in self.tables and 'Gaming_game' in self.tables:
            # Create a lookup for game details
            game_lookup = {}
            for game in self.tables['Gaming_game']:
                game_lookup[game.get('Id', 0)] = game
            
            for owned_game in self.tables['Gaming_game_owned']:
                game_id = owned_game.get('Id_game', 0)
                if game_id in game_lookup:
                    game = game_lookup[game_id]
                    name = game.get('Name', 'Unknown Game')
                    platform = f"Platform {game.get('Id_platform', 0)}"
                    state = f"State {owned_game.get('Purchasestate', 0)}"
                    rating = game.get('Rating', 0)
                    price = game.get('Price', 0)
                    
                    self.games_tree.insert('', 'end', text=name, 
                                         values=(platform, state, rating, price))
    
    def populate_social_tab(self):
        """Populate social tab with friends and social data"""
        # Populate friends
        for item in self.friends_tree.get_children():
            self.friends_tree.delete(item)
        
        if 'Friend_data' in self.tables and 'Youtuber' in self.tables:
            # Create youtuber name lookup
            youtuber_names = {}
            for youtuber in self.tables['Youtuber']:
                youtuber_names[youtuber.get('Id', 0)] = youtuber.get('Name', 'Unknown')
            
            relation_types = {0: 'Acquaintance', 1: 'Friend', 2: 'Best Friend', 3: 'Girlfriend', 4: 'Collaborator'}
            
            for friend in self.tables['Friend_data']:
                youtuber_id = friend.get('Youtuber', 0)
                name = youtuber_names.get(youtuber_id, f'Youtuber {youtuber_id}')
                relation = relation_types.get(friend.get('Relation', 0), 'Unknown')
                level = friend.get('Level', 0)
                affinity = friend.get('Affinity', 0)
                
                self.friends_tree.insert('', 'end', text=name, 
                                       values=(relation, level, affinity))
        
        # Populate social network posts
        for item in self.social_tree.get_children():
            self.social_tree.delete(item)
        
        if 'Social_network' in self.tables:
            for post in self.tables['Social_network']:
                message = post.get('Message', '')[:50] + ('...' if len(post.get('Message', '')) > 50 else '')
                date = post.get('Date', 0)
                likes = post.get('Likes', 0)
                dislikes = post.get('Dislikes', 0)
                
                self.social_tree.insert('', 'end', text=message, values=(date, likes, dislikes))
    
    def populate_inventory_tab(self):
        """Populate inventory tab with technology and items"""
        for item in self.tech_tree.get_children():
            self.tech_tree.delete(item)
        
        if 'Technology_owned' in self.tables:
            for tech in self.tables['Technology_owned']:
                tech_id = tech.get('Id_technology', 0)
                active = 'Yes' if tech.get('Active', 0) == 1 else 'No'
                lifetime = tech.get('Remaining_lifetime', 0)
                config = tech.get('Last_config_selected', 0)
                
                self.tech_tree.insert('', 'end', text=f'Technology {tech_id}', 
                                     values=(active, lifetime, config))
    
    def populate_progression_tab(self):
        """Populate progression tab with missions and talents"""
        # Populate missions
        for item in self.missions_tree.get_children():
            self.missions_tree.delete(item)
        
        if 'Mission' in self.tables:
            for mission in self.tables['Mission']:
                mission_id = mission.get('Id_mission', 0)
                progress = mission.get('Progress', 0)
                complete = 'Yes' if mission.get('Completed', 0) == 1 else 'No'
                milestone = mission.get('Milestone', 0)
                
                self.missions_tree.insert('', 'end', text=f'Mission {mission_id}', 
                                        values=(progress, complete, milestone))
        
        # Populate talents
        for item in self.talent_tree.get_children():
            self.talent_tree.delete(item)
        
        if 'Talent_tree_owned' in self.tables:
            for talent in self.tables['Talent_tree_owned']:
                talent_id = talent.get('Id_talent', 0)
                rank = talent.get('Rank', 0)
                
                self.talent_tree.insert('', 'end', text=f'Talent {talent_id}', values=(rank,))
    
    def update_table_combo(self):
        """Update the table selection combobox"""
        if self.tables:
            table_names = sorted(self.tables.keys())
            self.table_combo['values'] = table_names
    
    def on_table_selected(self, event=None):
        """Handle table selection in raw data tab"""
        self.refresh_table_data()
    
    def refresh_table_data(self):
        """Refresh the raw table data display"""
        selected_table = self.table_var.get()
        
        # Clear existing data
        for item in self.raw_tree.get_children():
            self.raw_tree.delete(item)
        
        # Clear existing columns
        self.raw_tree['columns'] = ()
        
        if selected_table and selected_table in self.tables:
            table_data = self.tables[selected_table]
            
            if table_data:
                # Get columns from first row
                columns = list(table_data[0].keys())
                
                # Configure treeview
                self.raw_tree['columns'] = columns
                self.raw_tree.heading('#0', text='Row')
                
                # Setup column headings and widths
                for col in columns:
                    self.raw_tree.heading(col, text=col)
                    self.raw_tree.column(col, width=100)
                
                # Add data rows
                for i, row in enumerate(table_data):
                    values = [str(row.get(col, '')) for col in columns]
                    self.raw_tree.insert('', 'end', text=str(i+1), values=values)
    
    def save_file(self):
        """Save the current file"""
        if self.current_file:
            try:
                self.update_data_from_gui()
                
                # Determine file type and save accordingly
                if self.current_file.endswith('.yls'):
                    self.save_as_yls(self.current_file)
                else:  # Assume it's a .txt file
                    self.save_as_text(self.current_file)
                
                self.modified = False
                self.status_bar.config(text=f"Saved: {os.path.basename(self.current_file)}")
                self.update_window_title()
                messagebox.showinfo("Save Complete", f"File saved successfully")
            except Exception as e:
                messagebox.showerror("Save Error", f"Failed to save file: {str(e)}")
        else:
            self.save_file_as()
    
    def save_file_as(self):
        """Save as new file"""
        if not self.tables:
            messagebox.showwarning("No Data", "No data to save")
            return
        
        filename = filedialog.asksaveasfilename(
            title="Save As",
            filetypes=[
                ("Youtubers Life Save", "*.yls"),
                ("Text files", "*.txt"),
                ("All files", "*.*")
            ]
        )
        
        if filename:
            try:
                self.update_data_from_gui()
                
                # Determine file type by extension
                if filename.endswith('.yls'):
                    self.save_as_yls(filename)
                else:
                    self.save_as_text(filename)
                
                self.current_file = filename
                self.modified = False
                self.status_bar.config(text=f"Saved: {os.path.basename(filename)}")
                self.update_window_title()
                messagebox.showinfo("Save Complete", f"File saved as: {filename}")
            except Exception as e:
                messagebox.showerror("Save Error", f"Failed to save file: {str(e)}")
    
    def save_as_text(self, filename):
        """Save data as decoded text file"""
        with open(filename, 'w', encoding='utf-8') as f:
            for table_name, table_data in self.tables.items():
                f.write(f"###{table_name}\n")
                if table_data:
                    headers = list(table_data[0].keys())
                    f.write('\t'.join(headers) + '\n')
                    
                    for row in table_data:
                        values = [str(row.get(col, '')) for col in headers]
                        f.write('\t'.join(values) + '\n')
                f.write('\n')
    
    def save_as_yls(self, filename):
        """Save data as encoded YLS file"""
        # First generate text data
        text_data = ""
        for table_name, table_data in self.tables.items():
            text_data += f"###{table_name}\n"
            if table_data:
                # Use original header order if available, otherwise use keys from first row
                if hasattr(self, 'table_headers') and table_name in self.table_headers:
                    headers = self.table_headers[table_name]
                else:
                    headers = list(table_data[0].keys())
                
                text_data += '\t'.join(headers) + '\n'
                
                for row in table_data:
                    values = [str(row.get(col, '')) for col in headers]
                    text_data += '\t'.join(values) + '\n'
            text_data += '\n'
        
        # Encode using gzip and base64 (same as in encode_to_yls)
        import gzip
        import base64
        import io
        
        # Compress with gzip
        buf = io.BytesIO()
        with gzip.GzipFile(fileobj=buf, mode='wb') as gz:
            gz.write(text_data.encode('utf-8'))
        
        # Encode with base64
        encoded_data = base64.b64encode(buf.getvalue()).decode('ascii')
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(encoded_data)
    
    def update_data_from_gui(self):
        """Update the data tables from GUI input fields"""
        try:
            # Update Savegame table from overview tab
            if 'Savegame' in self.tables and self.tables['Savegame']:
                savegame = self.tables['Savegame'][0]
                
                # Update basic save info
                if self.save_name_var.get():
                    savegame['Name'] = self.save_name_var.get()
                
                try:
                    if self.current_date_var.get():
                        savegame['Current_date'] = float(self.current_date_var.get())
                except ValueError:
                    pass
                
                try:
                    if self.money_var.get():
                        savegame['Money'] = int(self.money_var.get())
                except ValueError:
                    pass
                
                try:
                    if self.house_var.get():
                        # Extract number from house selection
                        house_num = self.house_var.get().split(' - ')[0]
                        savegame['House'] = int(house_num)
                except (ValueError, IndexError):
                    pass
            
            # Update Youtuber table from character tab
            if 'Youtuber' in self.tables:
                for youtuber in self.tables['Youtuber']:
                    if youtuber.get('Player_controlled') == 0:  # Player character
                        # Update character name
                        if self.char_name_var.get():
                            youtuber['Name'] = self.char_name_var.get()
                        
                        # Update character stats
                        stat_fields = {
                            'energy': 'Energy',
                            'hunger': 'Hunger',
                            'social_life': 'Social_life',
                            'motivation': 'Motivation'
                        }
                        
                        for var_name, field_name in stat_fields.items():
                            if var_name in self.char_stats_vars:
                                youtuber[field_name] = self.char_stats_vars[var_name].get()
                        
                        # Update skills
                        skill_fields = {
                            'scripting': 'Scripting',
                            'acting': 'Acting',
                            'sound': 'Sound',
                            'editing': 'Editing',
                            'effects': 'Effects'
                        }
                        
                        for var_name, field_name in skill_fields.items():
                            if var_name in self.skill_vars:
                                youtuber[field_name] = self.skill_vars[var_name].get()
                        break
            
            # Update Channel table from channel tab
            if 'Channel' in self.tables:
                # Find the player's channel by matching youtuber ID (same logic as populate)
                player_youtuber_id = None
                
                # Find the player's youtuber ID
                if 'Youtuber' in self.tables:
                    for youtuber in self.tables['Youtuber']:
                        if youtuber.get('Player_controlled') == 0:  # Player character
                            player_youtuber_id = youtuber.get('Id', 1)
                            break
                
                if player_youtuber_id is None:
                    player_youtuber_id = 1
                
                # Find and update the player's channel
                for channel in self.tables['Channel']:
                    if str(channel.get('Id_youtuber', '')) == str(player_youtuber_id):
                        if self.channel_name_var.get():
                            channel['Name'] = self.channel_name_var.get()
                        
                        try:
                            if self.subscribers_var.get() is not None:
                                channel['Subscribers'] = str(self.subscribers_var.get())
                        except:
                            pass
                        
                        try:
                            if self.total_views_var.get() is not None:
                                channel['Views'] = str(self.total_views_var.get())
                        except:
                            pass
                        break
            
            # Mark as modified
            self.modified = True
            
        except Exception as e:
            print(f"Error updating data from GUI: {e}")  # Debug info
            raise
    
    def export_to_text(self):
        """Export current data to text file"""
        filename = filedialog.asksaveasfilename(
            title="Export to Text",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    for table_name, table_data in self.tables.items():
                        f.write(f"###{table_name}\n")
                        if table_data:
                            headers = list(table_data[0].keys())
                            f.write('\t'.join(headers) + '\n')
                            
                            for row in table_data:
                                values = [str(row.get(col, '')) for col in headers]
                                f.write('\t'.join(values) + '\n')
                        f.write('\n')
                
                messagebox.showinfo("Export Complete", f"Data exported to: {filename}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export: {str(e)}")
    
    def decode_yls_file(self):
        """Decode a YLS file to text"""
        if not tse:
            messagebox.showerror("Error", "TSE module not available")
            return
        
        input_file = filedialog.askopenfilename(
            title="Select YLS file to decode",
            filetypes=[("YLS files", "*.yls"), ("All files", "*.*")]
        )
        
        if input_file:
            output_file = filedialog.asksaveasfilename(
                title="Save decoded file as",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            
            if output_file:
                try:
                    with open(input_file, 'r', encoding='utf-8') as f:
                        encoded_data = f.read()
                    
                    # Use the correct function from tse module
                    decoded_bytes = tse.decode_base64_gzip(encoded_data)
                    decoded_data = decoded_bytes.decode('utf-8')
                    
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(decoded_data)
                    
                    messagebox.showinfo("Decode Complete", f"File decoded to: {output_file}")
                except Exception as e:
                    messagebox.showerror("Decode Error", f"Failed to decode file: {str(e)}")
    
    def encode_to_yls(self):
        """Encode a text file to YLS"""
        if not tse:
            messagebox.showerror("Error", "TSE module not available")
            return
        
        input_file = filedialog.askopenfilename(
            title="Select text file to encode",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if input_file:
            output_file = filedialog.asksaveasfilename(
                title="Save encoded file as",
                filetypes=[("YLS files", "*.yls"), ("All files", "*.*")]
            )
            
            if output_file:
                try:
                    with open(input_file, 'r', encoding='utf-8') as f:
                        plain_data = f.read()
                    
                    # Encode using gzip and base64 (reverse of decode_base64_gzip)
                    import gzip
                    import base64
                    import io
                    
                    # Compress with gzip
                    buf = io.BytesIO()
                    with gzip.GzipFile(fileobj=buf, mode='wb') as gz:
                        gz.write(plain_data.encode('utf-8'))
                    
                    # Encode with base64
                    encoded_data = base64.b64encode(buf.getvalue()).decode('ascii')
                    
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(encoded_data)
                    
                    messagebox.showinfo("Encode Complete", f"File encoded to: {output_file}")
                except Exception as e:
                    messagebox.showerror("Encode Error", f"Failed to encode file: {str(e)}")
    
    def validate_save_data(self):
        """Validate the current save data"""
        if not self.tables:
            messagebox.showwarning("No Data", "No save data loaded to validate")
            return
        
        issues = []
        
        # Check for required tables
        required_tables = ['Savegame', 'Youtuber', 'Channel']
        for table in required_tables:
            if table not in self.tables:
                issues.append(f"Missing required table: {table}")
        
        if issues:
            messagebox.showwarning("Validation Issues", "\n".join(issues))
        else:
            messagebox.showinfo("Validation", "Save data appears valid")
    
    def backup_file(self):
        """Create a backup of the current file"""
        if self.current_file:
            backup_name = self.current_file + '.backup'
            try:
                import shutil
                shutil.copy2(self.current_file, backup_name)
                messagebox.showinfo("Backup Created", f"Backup saved as: {backup_name}")
            except Exception as e:
                messagebox.showerror("Backup Error", f"Failed to create backup: {str(e)}")
        else:
            messagebox.showwarning("No File", "No file is currently loaded")
    
    def refresh_all_tabs(self):
        """Refresh all tabs with current data"""
        self.populate_all_tabs()
        self.refresh_table_data()
    
    def expand_all_trees(self):
        """Expand all treeview items"""
        trees = [self.stats_tree, self.exp_tree, self.channel_tree, self.videos_tree,
                self.platforms_tree, self.games_tree, self.friends_tree, self.social_tree,
                self.tech_tree, self.missions_tree, self.talent_tree, self.raw_tree]
        
        for tree in trees:
            for item in tree.get_children():
                tree.item(item, open=True)
    
    def collapse_all_trees(self):
        """Collapse all treeview items"""
        trees = [self.stats_tree, self.exp_tree, self.channel_tree, self.videos_tree,
                self.platforms_tree, self.games_tree, self.friends_tree, self.social_tree,
                self.tech_tree, self.missions_tree, self.talent_tree, self.raw_tree]
        
        for tree in trees:
            for item in tree.get_children():
                tree.item(item, open=False)
    
    def show_about(self):
        """Show about dialog"""
        about_text = """
Youtubers Life Save Editor v1.0

A specialized save editor for Youtubers Life save files.

Features:
- View and edit character stats and skills
- Manage channel information and videos
- View gaming collection and platforms
- Manage friends and social network
- View inventory and technology
- Track missions and talents
- Raw data table viewer

Created for editing Youtubers Life save files with 
support for both encoded (.yls) and decoded (.txt) formats.
        """
        
        messagebox.showinfo("About", about_text.strip())
    
    def on_closing(self):
        """Handle application closing"""
        if self.modified:
            if messagebox.askokcancel("Quit", "You have unsaved changes. Quit anyway?"):
                self.root.destroy()
        else:
            self.root.destroy()
    
    def run(self):
        """Start the application"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

def main():
    """Main function"""
    app = YoutubersLifeSaveEditor()
    app.run()

if __name__ == "__main__":
    main()