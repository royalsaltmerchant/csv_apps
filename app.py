import tkinter as tk
from tkinter import ttk, filedialog
import csv
import os


class CSVViewerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CSV Viewer")

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
        menu_bar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Load CSV", command=self.load_csv)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        # Frame for table and sidebar
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Table Frame
        table_frame = tk.Frame(main_frame)
        table_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(table_frame, show="headings")
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind("<ButtonRelease-1>", self.show_row_details)
        self.tree.bind("<Up>", self.show_row_details)
        self.tree.bind("<Down>", self.show_row_details)

        # Add vertical scrollbar
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        # Sidebar for row details (initially hidden)
        self.sidebar = tk.Frame(main_frame, width=200, bg="#333333")

        self.sidebar_label = tk.Label(
            self.sidebar,
            text="Row Details",
            bg="#333333",
            fg="white",
            font=("Arial", 12, "bold"),
        )
        self.sidebar_label.pack(anchor="n", pady=10)

        self.row_details = tk.Text(
            self.sidebar, wrap=tk.WORD, bg="#444444", fg="white", state="disabled"
        )
        self.row_details.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        close_button = tk.Label(
            self.sidebar,
            text="x",
            bg="#333333",
            fg="white",
            font=("Arial", 20, "bold"),
            cursor="hand2",
        )
        close_button.pack(anchor="ne", padx=5, pady=5)
        close_button.bind("<Button-1>", lambda e: self.hide_sidebar())

    def load_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if not file_path:
            return

        self.load_file(file_path)

        # Save last opened file path
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
        with open(file_path, mode="r", encoding="utf-8-sig") as file:
            reader = csv.reader(file)
            self.data = list(reader)

        if self.data:
            self.headers = self.data[0]
            self.data = self.data[1:]
            self.populate_table()

    def populate_table(self):
        # Clear existing data
        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = self.headers

        for col in self.headers:
            self.tree.heading(
                col, text=col, anchor="w", command=lambda c=col: self.sort_by_column(c)
            )
            self.tree.column(col, anchor="w")

        for row in self.data:
            self.tree.insert("", "end", values=row)

    def show_row_details(self, event):
        # Delay the update to ensure Treeview state is up-to-date ... Is there a better way?
        self.root.after(1, self.update_row_details)

    def update_row_details(self):
        selected_item = self.tree.focus()
        if not selected_item:
            return

        row_data = self.tree.item(selected_item, "values")

        self.sidebar.pack(side=tk.RIGHT, fill=tk.Y)

        self.row_details.configure(state="normal")
        self.row_details.delete(1.0, tk.END)

        for header, value in zip(self.headers, row_data):
            self.row_details.insert(tk.END, f"{header}: {value}\n")

        self.row_details.configure(state="disabled")

    def hide_sidebar(self):
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
    app = CSVViewerApp(root)
    root.geometry("800x600")
    root.mainloop()
