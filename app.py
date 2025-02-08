import tkinter as tk
from tkinter import ttk, filedialog
import csv
import os
import math


# Colors
class Style:
    BACKGROUND_DARK = "#222222"
    BACKGROUND_LIGHT = "#555555"
    WHITE = "#dddddd"
    FONT_MAIN = "Courier New"
    FONT_SIZE_MAIN = 15


class CSVViewerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CSV Viewer")

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

        self.sidebar_visible = False
        self.current_file_path = None
        self.data = []
        self.headers = []
        self.app_name = "CSVViewerApp"
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
        edit_menu.add_command(label="Remove Row", command=self.remove_row)

        # Frame for table and sidebar
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Table Frame
        table_frame = tk.Frame(main_frame)
        table_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(table_frame, show="headings")
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.update_row_details)
        self.tree.bind("<Double-1>", self.open_edit_window)

        # Add vertical scrollbar
        vsb = ttk.Scrollbar(main_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        # Sidebar for row details (initially hidden)
        self.sidebar = tk.Frame(
            main_frame, width=500, bg=Style.BACKGROUND_DARK, highlightthickness=2
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
        close_button.bind("<Button-1>", lambda e: self.hide_sidebar())

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
        with open(file_path, mode="r", encoding="utf-8") as file:
            reader = csv.reader(file)
            self.data = list(reader)

        if self.data:
            self.headers = self.data[0]
            self.data = self.data[1:]
            self.populate_table()

    def save_to_file(self):
        if not self.current_file_path:
            return

        with open(
            self.current_file_path, mode="w", newline="", encoding="utf-8"
        ) as file:
            writer = csv.writer(file)
            writer.writerow(self.headers)
            writer.writerows(self.data)

    def new_row(self):
        if not self.data:
            return
        
        new_data = []
        for _ in self.headers:
            new_data.append('')
        self.data.append(new_data)
        
        new_tree_entry = self.tree.insert("", "end", values=new_data)
        self.tree.selection_set(new_tree_entry)
        self.tree.focus(new_tree_entry)
        self.open_edit_window()

    def remove_row(self):
        if not self.data:
            return
        
        selected_item = self.tree.focus()
        if not selected_item:
            return

        item_index = self.tree.index(selected_item)
        del self.data[item_index]
        self.save_to_file()
        self.hide_sidebar()
        self.populate_table()
        
    def open_edit_window(self, event=None):
        selected_item = self.tree.focus()
        if not selected_item:
            return

        row_data = self.tree.item(selected_item, "values")

        popup = tk.Toplevel(self.root)
        popup.title("Edit Row")
        popup.geometry("500x400")
        popup.config(bg=Style.BACKGROUND_DARK)

        edit_entries = []

        for i, (header, value) in enumerate(zip(self.headers, row_data)):
            frame = tk.Frame(popup, bg=Style.BACKGROUND_DARK)
            frame.pack(fill=tk.X, pady=5)

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
                height=3,
                width=40,
            )
            text_widget.insert("1.0", value)
            text_widget.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=5)

            edit_entries.append(text_widget)

        def save_changes():
            updated_values = [text_widget.get("1.0", "end-1c") for text_widget in edit_entries]

            self.tree.item(selected_item, values=updated_values)

            item_index = self.tree.index(selected_item)
            self.data[item_index] = updated_values
            
            if self.sidebar_visible:
                self.update_row_details(None) # None instead of an 'event'

            self.save_to_file()

            popup.destroy()

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
            command=popup.destroy,
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

        for row in self.data:
            self.tree.insert("", "end", values=row)

    def update_row_details(self, event):
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

    def hide_sidebar(self):
        self.sidebar_visible = False
        self.sidebar.pack_forget()

    def sort_by_column(self, column):
        col_index = self.headers.index(column)

        try:
            self.data.sort(key=lambda x: float(x[col_index]))
        except ValueError:
            self.data.sort(key=lambda x: x[col_index])

        self.populate_table()


if __name__ == "__main__":
    root = tk.Tk()

    # Get the screen width and height
    screen_width = math.floor(root.winfo_screenwidth() * 0.8)
    screen_height = math.floor(root.winfo_screenheight() * 0.8)

    app = CSVViewerApp(root)
    root.geometry(f"{screen_width}x{screen_height}")
    root.mainloop()
