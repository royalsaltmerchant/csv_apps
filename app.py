import sys
import tkinter as tk
from tkinter import ttk, filedialog
import csv
import os
import math
import uuid

from lib import detect_delimiter, detect_encoding


# Colors
class Style:
    BACKGROUND_DARK = "#222222"
    BACKGROUND_LIGHT = "#555555"
    WHITE = "#dddddd"
    FONT_MAIN = "Courier New"
    FONT_SIZE_MAIN = 15

class CSVState:
    """Tracks CSV-related state variables with type annotations."""
    current_file_path: str | None
    encoding: str
    delimiter: str
    headers: list[str]
    data: dict[dict[str]]
    display_data: dict[dict[str]]
    sidebar_visible: bool

    def __init__(self):
        self.current_file_path = None  # Path to the CSV file
        self.encoding = "utf-8"  # Default encoding
        self.delimiter = ","  # Default CSV delimiter
        self.headers = []  # List of column headers
        self.data = {}  # Dict of rows
        self.display_data = {}  # Dict of rows
        self.sidebar_visible = False  # Track sidebar visibility

class CSVViewerApp(CSVState):
    def __init__(self, root: tk.Tk):
        super().__init__()
        self.root = root
        self.root.title("CSV Zero")

        # Set a uniform font and treeview background color
        self.font = (Style.FONT_MAIN, Style.FONT_SIZE_MAIN)  # Monospace font

        self.style = ttk.Style()
        self.style.theme_use("clam")  # Use the "clam" theme for better customization
        self.style.configure(
            "Treeview",
            background=Style.BACKGROUND_DARK,
            foreground=Style.WHITE,
            fieldbackground=Style.BACKGROUND_LIGHT,
            borderwidth=0,
            font=self.font,
        )
        self.style.layout(
            "Treeview",
            [
                ("Treeview.treearea", {"sticky": "nswe"})
            ],  # Simplify layout to remove borders
        )
        self.style.configure(
            "Treeview.Heading",
            font=self.font,
            foreground=Style.WHITE,
            background=Style.BACKGROUND_LIGHT,
        )
        self.style.map(
            "Treeview",
            background=[
                ("selected", Style.BACKGROUND_LIGHT)
            ],  # Background color for selected rows
        )

        self.app_name = "CSV Zero"
        self.app_support_dir = os.path.join(
            os.path.expanduser("~"), "Library", "Application Support", self.app_name
        )
        os.makedirs(self.app_support_dir, exist_ok=True)
        self.last_file_path = os.path.join(self.app_support_dir, "last_file.txt")

        self.create_widgets()

        # Load last opened file if it exists
        self.load_last_file()
        self.root.focus_force()

    def create_widgets(self):
        # File menu
        menu_bar = tk.Menu(self.root)
        self.root.config(menu=menu_bar)

        file_menu = tk.Menu(menu_bar, tearoff=0)
        edit_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="File", menu=file_menu)
        menu_bar.add_cascade(label="Edit", menu=edit_menu)

        file_menu.add_command(label="Open File", command=self.load_csv, )
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        edit_menu.add_command(label="Insert Row", command=self.new_row)
        edit_menu.add_command(label="Edit Row", command=lambda: self.open_edit_window(create_new=False))
        edit_menu.add_command(label="Remove Row", command=self.remove_row)

        # Frame for search
        search_frame = tk.Frame(self.root, bg=Style.BACKGROUND_DARK)
        search_frame.pack(fill=tk.X)

        search_label = tk.Label(
            search_frame, text="Search:", bg=Style.BACKGROUND_DARK, fg=Style.WHITE, font=self.font
        )
        search_label.pack(side=tk.LEFT, padx=5)

        self.search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=self.search_var, font=self.font)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        search_entry.bind("<Return>", self.search_data)  # Bind Enter key

        search_button = tk.Button(
            search_frame, text="Search", command=self.search_data, font=self.font
        )
        search_button.pack(side=tk.RIGHT, padx=5)

        # Frame for table and sidebar
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)
        # main_frame.pack_propagate(False)
        

        # Table Frame
        table_frame = tk.Frame(main_frame)
        table_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        table_frame.pack_propagate(False)

        self.tree = ttk.Treeview(table_frame, show="headings")
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Commands
        self.tree.bind("<<TreeviewSelect>>", self.update_sidebar_info)
        self.tree.bind("<Double-1>", lambda e: self.open_edit_window(event=e, create_new=False))
        self.tree.bind("<Command-i>", self.new_row)
        self.tree.bind("<Command-r>", self.remove_row)

        # Add vertical scrollbar
        vsb = ttk.Scrollbar(main_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        # Sidebar for row details (initially hidden)
        self.sidebar = tk.Frame(
            main_frame, width=400, bg=Style.BACKGROUND_DARK, highlightthickness=2
        )
        self.sidebar.pack_propagate(False)

        self.sidebar_label = tk.Label(
            self.sidebar,
            text="Row Details",
            bg=Style.BACKGROUND_DARK,
            fg=Style.WHITE,
            font=self.font,
        )
        self.sidebar_label.pack(anchor="n", pady=5)

        self.row_details = tk.Text(
            self.sidebar,
            wrap=tk.WORD,
            bg=Style.BACKGROUND_DARK,
            fg=Style.WHITE,
            highlightthickness=0,  # Remove the focus border
            bd=0,  # Remove the border width
            state="disabled",
            font=self.font,
        )
        self.row_details.pack(fill=tk.BOTH, expand=True)

        close_button = tk.Label(
            self.sidebar,
            text="[<]",
            bg=Style.BACKGROUND_DARK,
            fg=Style.WHITE,
            font=("Mono", 20, "bold"),
            cursor="hand2",
        )
        close_button.pack(anchor="nw", padx=5, pady=5)
        close_button.bind("<Button-1>", lambda e: self.hide_sidebar(e))

    def update_display_data(self):
        self.display_data = self.data

    def search_data(self, event=None):
        query = self.search_var.get().strip().lower()
        
        if not query:
            self.update_display_data()  # Reset to full dataset
        else:
            # Filter rows where any column contains the query
            self.display_data = {
                uuid: row for uuid, row in self.data.items() if any(query in str(value).lower() for value in row)
            }

        self.populate_table()


    def load_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if not file_path:
            return

        self.load_file(file_path)

        with open(self.last_file_path, "w") as file:
            file.write(file_path)

        self.root.focus_force()

    def load_last_file(self):
        if os.path.exists(self.last_file_path):
            with open(self.last_file_path, "r") as file:
                file_path = file.read().strip()
                if os.path.exists(file_path):
                    self.load_file(file_path)

    def load_file(self, file_path):
        self.current_file_path = file_path
        self.encoding = detect_encoding(file_path)
        self.delimiter = detect_delimiter(self.current_file_path, self.encoding)
        
        try:
            with open(file_path, mode="r", encoding=self.encoding) as file:
                reader = csv.reader(file, quotechar='"', delimiter=self.delimiter)
                list_from_reader = list(reader)

            if list_from_reader:
                # Update data
                self.headers = list_from_reader[0]
                self.data = {str(uuid.uuid4()): row for row in list_from_reader[1:]}
                # Update UI
                self.update_display_data()
                self.populate_table()
        except Exception as e:
            tk.messagebox.showerror("Error", f"Failed to load CSV: {str(e)}")

    def save_to_file(self):
        if not self.current_file_path:
            return

        with open(
            self.current_file_path, mode="w", newline="", encoding=self.encoding
        ) as file:
            writer = csv.writer(file, delimiter=self.delimiter, quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(self.headers)
            writer.writerows(self.data.values())

    def new_row(self, event=None):
        if not self.data:
            return
        
        new_uuid = uuid.uuid4()
        new_data = []
        for _ in self.headers:
            new_data.append('')
        new_tree_entry = self.tree.insert("", "end", iid=new_uuid, values=new_data)
        self.tree.selection_set(new_tree_entry)
        self.open_edit_window(create_new=True)

    def remove_row(self, event=None):
        if not self.data:
            return
        
        # First remove from UI
        selected_item = self.tree.selection()
        if not selected_item:
            return None
        selected_item_uuid = selected_item[0]
        self.tree.delete(selected_item)

        self.hide_sidebar()

        # Remove from real data if it has been saved
        if self.data.get(selected_item_uuid):
            del self.data[selected_item_uuid]
            self.save_to_file()
            self.update_display_data()
            self.populate_table()
        
    def open_edit_window(self, create_new: bool=False, event=None):
        def handle_cancel():
            if create_new:
                self.remove_row()
            popup.destroy()

        selected_item = self.tree.selection()
        if not selected_item:
            return

        row_data = self.tree.item(selected_item, "values")

        popup = tk.Toplevel(self.root)
        popup.title("Edit Row")
        popup.config(bg=Style.BACKGROUND_DARK)
        # Bind for on close
        popup.protocol("WM_DELETE_WINDOW", handle_cancel)

        edit_entries = []

        for _, (header, value) in enumerate(zip(self.headers, row_data)):
            frame = tk.Frame(popup, bg=Style.BACKGROUND_DARK)
            frame.pack(fill=tk.X, pady=5, expand=True)

            label = tk.Label(
                frame, text=header, bg=Style.BACKGROUND_DARK, fg=Style.WHITE, font=self.font
            )
            label.pack(side=tk.LEFT, padx=5)

            text_widget = tk.Text(
                frame,
                font=self.font,
                bg=Style.BACKGROUND_LIGHT,
                fg=Style.WHITE,
                wrap=tk.WORD,
                height=2,
                width=40,
            )
            text_widget.insert("1.0", value)
            text_widget.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=5)

            edit_entries.append(text_widget)

        def save_changes():
            updated_values = [text_widget.get("1.0", "end-1c") for text_widget in edit_entries]
            self.data[selected_item[0]] = updated_values  # Correctly update existing row
            self.tree.item(selected_item, values=updated_values)  # Reflect the update in the UI

            if self.sidebar_visible:
                self.update_sidebar_info() # None instead of an 'event'

            popup.destroy()
            self.save_to_file()
            if not create_new:
                self.update_display_data()

        save_button = tk.Button(
            popup,
            text="Save",
            command=save_changes,
            font=self.font,
        )
        save_button.pack(pady=10)

        cancel_button = tk.Button(
            popup,
            text="Cancel",
            command=handle_cancel,
            font=self.font,
        )
        cancel_button.pack(pady=5)

    def populate_table(self):
        if self.tree["columns"]:
            column_widths = {
                col: self.tree.column(col, width=None) for col in self.tree["columns"]
            }
        else:
            column_widths = {}
        # Clear existing data
        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = self.headers

        for col in self.headers:
            self.tree.heading(
                col, text=col, anchor="w", command=lambda c=col: self.sort_by_column(c)
            )
            self.tree.column(col, anchor="w", width=column_widths.get(col, 100))

        for uuid, row in self.display_data.items():
            self.tree.insert("", "end", iid=uuid, values=row)

    def update_sidebar_info(self, event=None):
        self.sidebar_visible = True
        selected_item = self.tree.selection()
        if not selected_item:
            return

        row_data = self.tree.item(selected_item, "values")

        self.sidebar.pack(side=tk.RIGHT, fill=tk.Y)

        self.row_details.configure(state="normal", padx=10, pady=10)
        self.row_details.delete(1.0, tk.END)

        for header, value in zip(self.headers, row_data):
            self.row_details.insert(tk.END, f"{header}: {value}\n\n")

        self.row_details.configure(state="disabled")

    def hide_sidebar(self, event=False):
        self.sidebar_visible = False
        self.sidebar.pack_forget()

    def sort_by_column(self, column):
        col_index = self.headers.index(column)

        try:
            # Convert dictionary to list of tuples [(uuid, row_list)]
            sorted_list = sorted(self.display_data.items(), key=lambda x: float(x[1][col_index]))  # Numeric sort
        except ValueError:
            sorted_list = sorted(self.display_data.items(), key=lambda x: x[1][col_index])  # String sort

        # Convert back to dictionary
        self.display_data = dict(sorted_list)

        # Repopulate the table
        self.populate_table()



if __name__ == "__main__":
    root = tk.Tk()

    icon_path = os.path.join(os.path.abspath("."), "logo.ico")

    if sys.platform.startswith("win"):
        # When running from a PyInstaller EXE, use sys._MEIPASS
        if getattr(sys, 'frozen', False):
            icon_path = os.path.join(sys._MEIPASS, "logo.ico")
        root.iconbitmap(icon_path)

    # Get the screen width and height
    screen_width = math.floor(root.winfo_screenwidth() * 0.8)
    screen_height = math.floor(root.winfo_screenheight() * 0.8)

    app = CSVViewerApp(root)
    root.geometry(f"{screen_width}x{screen_height}")

        # Handle "Open With" file arguments
    if len(sys.argv) > 1:  # If a file is passed as an argument
        file_path = sys.argv[1]
        if os.path.exists(file_path):
            app.load_file(file_path)  # Open the file immediately
            
    root.mainloop()
