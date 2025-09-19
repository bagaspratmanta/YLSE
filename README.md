# 🎮 Youtubers Life Save Editor

A powerful and safe save editor for Youtubers Life that lets you modify your game progress without corrupting NPC appearances or game data.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)
![Python](https://img.shields.io/badge/python-3.13-green.svg)

## ✨ Features

### 📊 Complete Save Editing
- **Channel Management**: Edit channel name, subscribers, and total views
- **Character Stats**: Modify energy, hunger, social life, and motivation
- **Skills System**: Adjust scripting, acting, sound, editing, and effects skills
- **Game Progress**: Change money, house, and experience points
- **Video Analytics**: View detailed video and gaming statistics

### 🛡️ Safety & Reliability
- **NPC Appearance Preservation**: Fixes the "yellow hair bug" found in other save editors
- **Exact Format Compatibility**: Maintains original file structure and encoding
- **Change Tracking**: Visual indicators show when files are modified
- **Error Handling**: Graceful recovery from parsing issues

### 💻 User Experience
- **Tabbed Interface**: Clean, organized layout for easy navigation
- **No Installation**: Standalone executable with no dependencies
- **Real-time Validation**: Immediate feedback on changes
- **Backup Reminders**: Built-in safety warnings

## 🚀 Quick Start

### Option 1: Download Pre-built Executable
1. Go to [Releases](../../releases)
2. Download `Youtubers_Life_Save_Editor.exe`
3. Run the executable (no installation required)

### Option 2: Run from Source
```bash
# Clone the repository
git clone https://github.com/yourusername/youtubers-life-save-editor.git
cd youtubers-life-save-editor

# Install dependencies (optional, only for building)
pip install -r requirements.txt

# Run the editor
python youtubers_life_save_editor.py
```

## 📖 How to Use

1. **Launch** the save editor
2. **Open** your save file: `File → Open` (select your `.yls` file)
3. **Navigate** through the tabs to edit different aspects:
   - **Overview**: Basic save info, money, current date
   - **Character**: Stats, skills, and character properties
   - **Channel**: Channel name, subscribers, views
   - **Videos**: Video statistics and performance
   - **Gaming**: Gaming-related progress
   - **Social**: Social media and friend data
   - **Inventory**: Items and possessions
   - **Progress**: Experience and level progression
   - **Raw Data**: Advanced view of all save data
4. **Save** your changes: `Ctrl+S` or `File → Save`
5. **Load** your save in Youtubers Life

## 📂 Save File Location

Your Youtubers Life save files are typically located at:
```
%USERPROFILE%\Documents\U-Play online\Youtubers Life\
```

## 🛠️ Building from Source

### Prerequisites
- Python 3.7+ (tested with 3.13)
- tkinter (usually included with Python)

### Building Executable
```bash
# Install PyInstaller
pip install pyinstaller

# Build standalone executable
pyinstaller --onefile --windowed --name "Youtubers_Life_Save_Editor" youtubers_life_save_editor.py
```

The executable will be created in the `dist/` folder.

## 🔧 Technical Details

- **Language**: Python 3.13
- **GUI Framework**: tkinter (cross-platform)
- **File Format**: Base64 + gzip encoding (same as game)
- **Data Preservation**: Maintains all 777 avatar pieces and 13+ hair color variants
- **Architecture**: Modular design with separate encoding/decoding module

## 🐛 Known Issues & Solutions

### "Yellow Hair Bug" in Other Editors
**Problem**: NPCs all have yellow hair after using other save editors  
**Solution**: This editor preserves avatar piece data correctly, maintaining original NPC appearances

### Antivirus False Positives
**Problem**: Some antivirus software flags the executable  
**Reason**: Compiled Python scripts can trigger heuristic detection  
**Solution**: The source code is available for transparency; you can build from source

## ⚠️ Important Notes

- **Always backup your original save files** before editing
- This is an unofficial tool created for educational purposes
- Youtubers Life is a trademark of U-Play Online
- Use at your own risk - we're not responsible for save file corruption

## 🤝 Contributing

Contributions are welcome! Please feel free to:
- Report bugs by opening an issue
- Suggest features or improvements
- Submit pull requests with enhancements

### Development Setup
```bash
git clone https://github.com/yourusername/youtubers-life-save-editor.git
cd youtubers-life-save-editor
pip install -r requirements.txt
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- U-Play Online for creating Youtubers Life
- The Python community for excellent libraries
- Users who reported the NPC appearance bug that led to this improved editor

## 📞 Support

If you encounter any issues:
1. Check the [Issues](../../issues) page for existing solutions
2. Create a new issue with detailed information about your problem
3. Include your save file (if comfortable sharing) for better debugging

---

**Disclaimer**: This is an unofficial save editor. Youtubers Life is a trademark of U-Play Online. This software is provided "as is" without warranty for educational and personal use only.