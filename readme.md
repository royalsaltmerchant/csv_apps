# 📄 CSV Zero

**CSV Zero** is a fast, minimalist desktop CSV editor and viewer built with Python and Tkinter. Designed for simplicity and clarity, it lets you view, edit, search, and manage CSV files without the bloat of spreadsheets or clunky web tools.

---

## ✨ Features

- 🗂 **Open any CSV file** — auto-detects delimiter and encoding
- 🔍 **Search across all rows and columns**
- 📝 **Edit rows or insert new ones with ease**
- 🧹 **Remove rows instantly**
- 📁 **Remembers the last opened file**
- 🧠 **Clean, dark-themed interface with monospaced font**
- 📐 **Resizable window and responsive table view**
- 🖱 **Double-click or use shortcuts to interact**

---

## 🚀 Installation

This app is packaged using [Inno Setup](https://jrsoftware.org/isinfo.php). Simply download and run the installer:

👉 [Download CSV Zero Installer for Windows](https://github.com/royalsaltmerchant/csv_apps/raw/main/CSVZeroInstaller_windows.exe)

No Python installation required. Works out of the box on Windows 10+.

MacOS installer not currently available...

---

## 🔧 How to Use

1. Launch **CSV Zero** from the Start Menu or Desktop shortcut
2. Go to **File → Open File** to load a CSV
3. Click any row to inspect details in the sidebar
4. Use:
   - **Insert Row** to add a new blank entry
   - **Edit Row** to update values
   - **Remove Row** to delete entries
5. Use the search bar to filter rows live
6. Changes are automatically saved to the original file

💡 Your last opened file is remembered across sessions.

---

## 🧠 Keyboard Shortcuts

| Action         | Shortcut        |
|----------------|-----------------|
| Insert Row     | ⌘ Cmd + I       |
| Remove Row     | ⌘ Cmd + R       |
| Edit Row       | ⌘ Cmd + Double Click |
| Search         | Press **Enter** |

---

## 📁 File Support

- CSV files with:
  - Comma, semicolon, tab, or pipe delimiters
  - UTF-8, UTF-16, or other common encodings
- Supports multi-line text fields
- Long files handled efficiently

---

## 🛠 Tech Stack

- **Python 3**
- **Tkinter**
- **PyInstaller** for packaging
- **Inno Setup** for the installer

---

## ⚠️ Known Limitations

- Large CSVs (100,000+ rows) may load slowly
- No undo/redo yet — edits are immediately saved