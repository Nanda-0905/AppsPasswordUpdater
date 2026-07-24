import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import shutil

class AppsPasswordUpdater:
    def __init__(self, root):
        self.root = root
        self.root.title("AppsPasswordUpdater")
        self.root.geometry("800x600")

        # Top Panel
        panel = ttk.Frame(root, padding="10")
        panel.pack(fill=tk.X)

        # Folder selection
        ttk.Label(panel, text="Folder:").grid(row=0, column=0, sticky=tk.W)
        self.folder_path = tk.StringVar()
        ttk.Entry(panel, textvariable=self.folder_path, width=50).grid(row=0, column=1, padx=5)
        ttk.Button(panel, text="Browse", command=self.browse_folder).grid(row=0, column=2)

        # Find and Replace fields
        ttk.Label(panel, text="Find:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.find_str = tk.StringVar()
        ttk.Entry(panel, textvariable=self.find_str).grid(row=1, column=1, fill=tk.X, padx=5)

        ttk.Label(panel, text="Replace:").grid(row=2, column=0, sticky=tk.W)
        self.replace_str = tk.StringVar()
        ttk.Entry(panel, textvariable=self.replace_str).grid(row=2, column=1, fill=tk.X, padx=5)

        # Buttons
        btn_frame = ttk.Frame(panel)
        btn_frame.grid(row=3, column=1, sticky=tk.E, pady=10)
        ttk.Button(btn_frame, text="Find", command=self.find_files).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Replace", command=self.replace_strings).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Close", command=root.destroy).pack(side=tk.LEFT, padx=2)

        # Grid (Treeview)
        cols = ("Folder Name", "File Name", "Strings Found")
        self.tree = ttk.Treeview(root, columns=cols, show="headings")
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=200)
        
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_path.set(folder)

    def find_files(self):
        search_dir = self.folder_path.get()
        search_text = self.find_str.get()
        if not search_dir or not search_text:
            messagebox.showwarning("Warning", "Please select a folder and enter text to find.")
            return

        self.tree.delete(*self.tree.get_children())
        for root, dirs, files in os.walk(search_dir):
            for file in files:
                if file.endswith(".config"):
                    path = os.path.join(root, file)
                    try:
                        with open(path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            if search_text in content:
                                self.tree.insert("", tk.END, values=(root, file, search_text))
                    except Exception as e:
                        print(f"Error reading {path}: {e}")

    def replace_strings(self):
        search_text = self.find_str.get()
        replace_text = self.replace_str.get()
        items = self.tree.get_children()
        
        if not items:
            messagebox.showinfo("Info", "No files to update.")
            return

        if not messagebox.askyesno("Confirm", "Do you want to replace strings and create backups?"):
            return

        for item in items:
            folder, filename, _ = self.tree.item(item, "values")
            path = os.path.join(folder, filename)
            backup_path = path + ".bak"
            
            try:
                shutil.copy2(path, backup_path)
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                new_content = content.replace(search_text, replace_text)
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update {filename}: {e}")
        
        messagebox.showinfo("Success", "Replacement complete. Backups created.")

if __name__ == "__main__":
    root = tk.Tk()
    app = AppsPasswordUpdater(root)
    root.mainloop()
