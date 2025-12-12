import json
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from pathlib import Path
import uuid
import requests
from requests.exceptions import RequestException


DATA_FILE = Path(__file__).with_name("media.json")

# Modern color palette
COLOR_PRIMARY = "#1E88E5"
COLOR_SECONDARY = "#42A5F5"
COLOR_ACCENT = "#FF6F00"
COLOR_DARK = "#0D47A1"
COLOR_BG = "#ECEFF1"
COLOR_CARD = "#FFFFFF"
COLOR_TEXT = "#212121"
COLOR_TEXT_LIGHT = "#616161"
COLOR_SUCCESS = "#4CAF50"
COLOR_WARNING = "#FFC107"


class LibraryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Atharva Rakshe Library")
        self.root.geometry("1100x700")
        self.root.configure(bg=COLOR_BG)

        self.data = []
        self.sort_ascending = True
        self.view_mode = "table"  # Can be "table" or "grid"
        self.selected_item = None

        # Configure styles
        self.setup_styles()

        # Header frame with gradient effect
        header = tk.Frame(root, bg=COLOR_DARK, height=100)
        header.pack(side=tk.TOP, fill=tk.X)
        header.pack_propagate(False)

        # Logo and title in header
        title_frame = tk.Frame(header, bg=COLOR_DARK)
        title_frame.pack(fill=tk.X, padx=20, pady=(15, 10))

        title_label = tk.Label(title_frame, text="📚  Scholar's Digital Library", font=("Segoe UI", 28, "bold"), fg=COLOR_SECONDARY, bg=COLOR_DARK)
        title_label.pack(side=tk.LEFT)

        subtitle_label = tk.Label(header, text="Organize and manage your media collection", font=("Segoe UI", 12, "bold"), fg="#E3F2FD", bg=COLOR_DARK)
        subtitle_label.pack(pady=(0, 6))

        # Accent bar to make the header feel more polished
        accent = tk.Frame(header, bg=COLOR_ACCENT, height=4)
        accent.pack(fill=tk.X, padx=20, pady=(0, 12))

        # Filter and search bar - modernized
        toolbar = tk.Frame(root, bg=COLOR_BG, height=70)
        toolbar.pack(side=tk.TOP, fill=tk.X, padx=15, pady=(10, 5))
        toolbar.pack_propagate(False)

        # Left side - filters
        left_toolbar = tk.Frame(toolbar, bg=COLOR_BG)
        left_toolbar.pack(side=tk.LEFT, fill=tk.X, expand=True)

        ttk.Label(left_toolbar, text="📁 Category:", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=(0, 5))
        self.category_var = tk.StringVar()
        self.category_cb = ttk.Combobox(left_toolbar, textvariable=self.category_var, width=15, state='readonly', font=("Segoe UI", 10))
        self.category_cb.pack(side=tk.LEFT, padx=(0, 15))
        self.category_cb.bind('<<ComboboxSelected>>', lambda e: self.on_category_change())

        ttk.Label(left_toolbar, text="🔍 Search:", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(left_toolbar, textvariable=self.search_var, width=25, font=("Segoe UI", 10))
        self.search_entry.pack(side=tk.LEFT, padx=(0, 8))
        self.search_entry.bind('<Return>', lambda e: self.on_search())

        # Right side - action buttons
        right_toolbar = tk.Frame(toolbar, bg=COLOR_BG)
        right_toolbar.pack(side=tk.RIGHT, fill=tk.X)

        self.sort_btn = tk.Button(right_toolbar, text="↕ Sort Date", command=self.on_sort_toggle, 
                                   bg=COLOR_PRIMARY, fg="white", font=("Segoe UI", 9, "bold"), 
                                   padx=12, pady=6, relief=tk.FLAT, cursor="hand2")
        self.sort_btn.pack(side=tk.LEFT, padx=(0, 8))

        self.new_btn = tk.Button(right_toolbar, text="➕ Add Item", command=self.on_new,
                                 bg=COLOR_SUCCESS, fg="white", font=("Segoe UI", 9, "bold"),
                                 padx=12, pady=6, relief=tk.FLAT, cursor="hand2")
        self.new_btn.pack(side=tk.LEFT, padx=(0, 8))

        self.load_btn = tk.Button(right_toolbar, text="🔄 Refresh", command=self.on_load,
                                  bg=COLOR_SECONDARY, fg="white", font=("Segoe UI", 9, "bold"),
                                  padx=12, pady=6, relief=tk.FLAT, cursor="hand2")
        self.load_btn.pack(side=tk.LEFT, padx=(0, 8))

        self.erase_btn = tk.Button(right_toolbar, text="🗑 Delete", command=self.on_erase,
                                   bg="#E53935", fg="white", font=("Segoe UI", 9, "bold"),
                                   padx=12, pady=6, relief=tk.FLAT, cursor="hand2")
        self.erase_btn.pack(side=tk.LEFT)

        # Main content area with treeview
        content_frame = tk.Frame(root, bg=COLOR_BG)
        content_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=15, pady=(5, 15))

        # Treeview container with rounded appearance
        tree_container = tk.Frame(content_frame, bg=COLOR_CARD, relief=tk.FLAT, bd=1)
        tree_container.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Treeview
        columns = ("sno", "name", "author", "date", "category")
        self.tree = ttk.Treeview(tree_container, columns=columns, show='tree headings', height=20)
        
        self.tree.heading("#0", text="")
        self.tree.heading("sno", text="S.No")
        self.tree.heading("name", text="📖 Title")
        self.tree.heading("author", text="✍️ Author")
        self.tree.heading("date", text="📅 Year")
        self.tree.heading("category", text="🏷️ Type")

        self.tree.column("#0", width=0, stretch=False)
        self.tree.column("sno", anchor='center', width=50)
        self.tree.column("name", anchor='w', width=350)
        self.tree.column("author", anchor='w', width=200)
        self.tree.column("date", anchor='center', width=80)
        self.tree.column("category", anchor='center', width=100)

        # Configure row colors
        self.tree.tag_configure('oddrow', background='#FFFFFF', foreground=COLOR_TEXT)
        self.tree.tag_configure('evenrow', background='#F5F5F5', foreground=COLOR_TEXT)
        self.tree.tag_configure('selected_row', background=COLOR_PRIMARY, foreground='white')

        # Scrollbars
        vsb = ttk.Scrollbar(tree_container, orient=tk.VERTICAL, command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_container, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscroll=vsb.set, xscroll=hsb.set)

        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Bind right-click context menu
        self.tree.bind('<Button-3>', self.on_right_click)
        self.tree.bind('<Button-1>', self.on_tree_click)

        # Context menu
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="✏️  Edit", command=self.on_edit_selected)
        self.context_menu.add_command(label="👁️  View Details", command=self.on_view_details)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="🗑️  Delete", command=self.on_erase)

        # Status bar
        status_frame = tk.Frame(root, bg=COLOR_DARK, height=30)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        status_frame.pack_propagate(False)

        self.status_label = tk.Label(status_frame, text="Ready", font=("Segoe UI", 9), fg="white", bg=COLOR_DARK, justify=tk.LEFT)
        self.status_label.pack(side=tk.LEFT, padx=15, pady=5)

        # Empty state label
        # Empty state label
        self.empty_frame = tk.Frame(tree_container, bg=COLOR_CARD)
        self.empty_label = tk.Label(self.empty_frame, text="📚 Your library is empty\nStart by adding your first item!", 
                                   font=("Segoe UI", 16, "bold"), fg=COLOR_TEXT_LIGHT, bg=COLOR_CARD)
        self.empty_label.pack(pady=40)

        # Load initial data
        self.on_load()

    def setup_styles(self):
        """Configure modern ttk styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure button style
        style.configure('TButton', font=('Segoe UI', 9), padding=6)
        style.configure('TCombobox', font=('Segoe UI', 10), padding=3)
        style.configure('TLabel', font=('Segoe UI', 10), background=COLOR_BG)
        
        # Treeview style
        style.configure('Treeview', rowheight=32, font=('Segoe UI', 10), 
                       fieldbackground=COLOR_CARD, background=COLOR_CARD)
        style.configure('Treeview.Heading', font=('Segoe UI', 10, 'bold'),
                       background=COLOR_PRIMARY, foreground='white')
        style.map('Treeview.Heading', background=[('active', COLOR_SECONDARY)])
        style.map('Treeview', 
                 background=[('selected', COLOR_PRIMARY)],
                 foreground=[('selected', 'white')])

    def read_json(self):
        if not DATA_FILE.exists():
            return []
        try:
            with DATA_FILE.open('r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            messagebox.showerror("Error", f"Failed to read {DATA_FILE}")
            return []

    def write_json(self):
        try:
            with DATA_FILE.open('w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except Exception:
            messagebox.showerror("Error", f"Failed to write {DATA_FILE}")

    def on_load(self):
        # Prefer backend if available
        try:
            resp = requests.get('http://127.0.0.1:5000/media', timeout=1)
            if resp.status_code == 200:
                self.data = resp.json()
            else:
                self.data = self.read_json()
        except RequestException:
            self.data = self.read_json()
        # Ensure every book has a unique id; if missing, create one and persist
        updated = False
        for b in self.data:
            if 'id' not in b:
                b['id'] = str(uuid.uuid4())
                updated = True
        if updated:
            # persist locally if using local JSON
            try:
                self.write_json()
            except Exception:
                pass
        self.populate_categories()
        self.refresh_treeview()

    def populate_categories(self):
        # Gather categories from the data; ensure we always have an "All" option
        cats = sorted({item.get('category','') for item in self.data if item.get('category')})
        values = ["All"] + cats
        self.category_cb['values'] = values
        # If a category was previously selected, try to keep it; otherwise default to All
        current = self.category_var.get()
        if current and current in values:
            self.category_cb.set(current)
        else:
            self.category_cb.set("All")

        # If there are no categories (empty dataset), make sure combobox still has All
        if not cats:
            self.category_cb['values'] = ["All"]
            self.category_cb.set("All")

    def refresh_treeview(self, category=None, name_filter=None):
        for r in self.tree.get_children():
            self.tree.delete(r)

        # If no explicit category provided, use the currently selected category in the combobox
        if category is None:
            category = self.category_var.get() or "All"

        filtered = self.data
        if category and category != "All":
            filtered = [b for b in filtered if b.get('category') == category]
        if name_filter:
            q = name_filter.strip().lower()
            filtered = [b for b in filtered if q in b.get('name','').lower() or q in b.get('author','').lower()]

        # sort by date
        def get_year(b):
            try:
                return int(b.get('date') or 0)
            except Exception:
                return 0

        filtered = sorted(filtered, key=get_year, reverse=not self.sort_ascending)

        for idx, b in enumerate(filtered):
            serial = idx + 1
            tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
            item_id = b.get('id') or str(uuid.uuid4())
            if 'id' not in b:
                b['id'] = item_id
            
            self.tree.insert('', tk.END, iid=item_id, 
                           values=(serial, b.get('name',''), b.get('author',''), 
                                  b.get('date',''), b.get('category','')), tags=(tag,))

        # Update status
        total = len(self.data)
        shown = len(filtered)
        self.status_label.config(text=f"📊 Showing {shown} of {total} items")

        # Show/hide empty state
        if not filtered:
            self.empty_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        else:
            self.empty_frame.pack_forget()

    def on_search(self):
        cat = self.category_var.get()
        name = self.search_var.get()
        self.refresh_treeview(category=cat, name_filter=name)

    def on_category_change(self):
        """Called when the combobox selection changes; refresh table to show only that category."""
        cat = self.category_var.get() or "All"
        self.refresh_treeview(category=cat, name_filter=self.search_var.get())

    def on_new(self):
        NewBookWindow(self)

    def on_edit_selected(self):
        """Called when Edit is chosen from the context menu; opens edit dialog."""
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("No selection", "Please select a book to edit")
            return
        # Use the tree item's iid (which we set to the book's unique id) to find the book
        iid = sel[0]
        idx = None
        for i, b in enumerate(self.data):
            if str(b.get('id')) == str(iid):
                idx = i
                break
        if idx is None:
            messagebox.showerror("Not found", "Selected book was not found in data")
            return
        EditBookWindow(self, idx)

    def on_erase(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("No selection", "Please select a book to delete")
            return
        # Find the selected item's id (iid)
        iid = sel[0]
        # Find index in data by id
        to_remove = None
        for i, b in enumerate(self.data):
            if str(b.get('id')) == str(iid):
                to_remove = i
                name = b.get('name')
                break
        if not messagebox.askyesno("Confirm", f"Delete '{name}'?"):
            return
        if to_remove is not None:
            deleted = None
            # try backend delete first
            try:
                resp = requests.delete(f'http://127.0.0.1:5000/media/{iid}', timeout=1)
                if resp.status_code == 200:
                    deleted = True
            except RequestException:
                deleted = None

            if deleted:
                # reload from backend
                self.on_load()
            else:
                # fallback to local deletion
                del self.data[to_remove]
                self.write_json()
                self.on_load()

    def on_sort_toggle(self):
        self.sort_ascending = not self.sort_ascending
        arrow = '↕ Sort Date (↑ Ascending)' if self.sort_ascending else '↕ Sort Date (↓ Descending)'
        self.sort_btn.config(text=arrow)
        self.refresh_treeview(category=self.category_var.get(), name_filter=self.search_var.get())

    def on_tree_click(self, event):
        """Handle tree item click"""
        item = self.tree.identify('item', event.x, event.y)
        if item:
            self.selected_item = item

    def on_right_click(self, event):
        """Show context menu when user right-clicks a row."""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.selected_item = item
            try:
                self.context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                self.context_menu.grab_release()

    def on_view_details(self):
        """Show detailed view of selected item"""
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("No selection", "Please select an item to view")
            return
        
        iid = sel[0]
        book = None
        for b in self.data:
            if str(b.get('id')) == str(iid):
                book = b
                break
        
        if not book:
            return
        
        # Create details window
        details_window = tk.Toplevel(self.root)
        details_window.title(f"Details - {book.get('name','Unknown')}")
        details_window.geometry("500x400")
        details_window.configure(bg=COLOR_BG)
        
        # Header
        header = tk.Frame(details_window, bg=COLOR_PRIMARY, height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        title = tk.Label(header, text=book.get('name',''), font=("Segoe UI", 16, "bold"),
                        fg="white", bg=COLOR_PRIMARY, wraplength=450)
        title.pack(pady=15)
        
        # Content
        content = tk.Frame(details_window, bg=COLOR_BG)
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Details
        details = [
            ("Title:", book.get('name','')),
            ("Author:", book.get('author','')),
            ("Year:", book.get('date','')),
            ("Category:", book.get('category','')),
            ("ID:", book.get('id','')[:8] + '...'),
        ]
        
        for label, value in details:
            frame = tk.Frame(content, bg=COLOR_BG)
            frame.pack(fill=tk.X, pady=5)
            
            lbl = tk.Label(frame, text=label, font=("Segoe UI", 10, "bold"),
                          fg=COLOR_PRIMARY, bg=COLOR_BG, width=12, anchor='w')
            lbl.pack(side=tk.LEFT)
            
            val = tk.Label(frame, text=value, font=("Segoe UI", 10),
                          fg=COLOR_TEXT, bg=COLOR_BG, wraplength=350, justify=tk.LEFT)
            val.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))
        
        # Close button
        close_btn = tk.Button(details_window, text="Close", command=details_window.destroy,
                             bg=COLOR_PRIMARY, fg="white", font=("Segoe UI", 9, "bold"),
                             padx=20, pady=8, relief=tk.FLAT, cursor="hand2")
        close_btn.pack(pady=15)


class NewBookWindow:
    def __init__(self, app: LibraryApp):
        self.app = app
        self.top = tk.Toplevel(app.root)
        self.top.title("Add New Item")
        self.top.geometry("520x440")
        self.top.configure(bg=COLOR_BG)

        # Header
        header = tk.Frame(self.top, bg=COLOR_PRIMARY, height=70)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        title = tk.Label(header, text="➕ Add New Item to Your Library", 
                        font=("Segoe UI", 14, "bold"), fg="white", bg=COLOR_PRIMARY)
        title.pack(pady=15)

        # Main frame
        main = tk.Frame(self.top, bg=COLOR_BG)
        main.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Form fields
        self.name_var = tk.StringVar()
        self.create_form_field(main, "📖 Title:", 0, self.name_var)
        self.author_var = tk.StringVar()
        self.create_form_field(main, "✍️ Author:", 1, self.author_var)
        self.date_var = tk.StringVar()
        self.create_form_field(main, "📅 Year:", 2, self.date_var, width=20)

        # Category dropdown
        cat_lbl = tk.Label(main, text="🏷️ Category:", font=("Segoe UI", 10, "bold"),
                          fg=COLOR_PRIMARY, bg=COLOR_BG)
        cat_lbl.grid(row=3, column=0, sticky='w', pady=(10, 5))

        self.cat_var = tk.StringVar()
        cats = ["Book", "Film", "Magazine"]
        self.cat_cb = ttk.Combobox(main, textvariable=self.cat_var, values=cats, 
                                   width=45, state='readonly', font=("Segoe UI", 10))
        self.cat_cb.grid(row=3, column=1, sticky='ew', pady=(10, 5))
        self.cat_cb.current(0)

        # Buttons frame
        btn_frame = tk.Frame(main, bg=COLOR_BG)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=(20, 0), sticky='ew')

        save_btn = tk.Button(btn_frame, text="✓ Save", command=self.on_save,
                            bg=COLOR_SUCCESS, fg="white", font=("Segoe UI", 10, "bold"),
                            padx=30, pady=8, relief=tk.FLAT, cursor="hand2")
        save_btn.pack(side=tk.RIGHT, padx=(8, 0))

        cancel_btn = tk.Button(btn_frame, text="✕ Cancel", command=self.top.destroy,
                              bg="#BDBDBD", fg="white", font=("Segoe UI", 10, "bold"),
                              padx=30, pady=8, relief=tk.FLAT, cursor="hand2")
        cancel_btn.pack(side=tk.RIGHT)

    def create_form_field(self, parent, label, row, var, width=45):
        lbl = tk.Label(parent, text=label, font=("Segoe UI", 10, "bold"),
                      fg=COLOR_PRIMARY, bg=COLOR_BG)
        lbl.grid(row=row, column=0, sticky='w', pady=(0, 5))

        entry = ttk.Entry(parent, textvariable=var, width=width, font=("Segoe UI", 10))
        entry.grid(row=row, column=1, sticky='ew', pady=(0, 5))
        parent.grid_columnconfigure(1, weight=1)

        return entry

    def on_save(self):
        name = self.name_var.get().strip()
        author = self.author_var.get().strip()
        date = self.date_var.get().strip()
        cat = self.cat_var.get().strip() or 'Uncategorized'
        if not name:
            messagebox.showwarning("Validation", "Name is required")
            return
        # Try to create via backend if available
        try:
            resp = requests.post('http://127.0.0.1:5000/media', json={
                'name': name, 'author': author, 'date': date, 'category': cat
            }, timeout=1)
            if resp.status_code in (200, 201):
                self.app.on_load()
                self.top.destroy()
                return
        except RequestException:
            pass

        # Fallback to local create
        new = {"id": str(uuid.uuid4()), "name": name, "author": author, "date": date, "category": cat}
        self.app.data.append(new)
        self.app.write_json()
        self.app.on_load()
        self.top.destroy()


class EditBookWindow:
    def __init__(self, app: LibraryApp, index: int):
        self.app = app
        self.index = index
        self.top = tk.Toplevel(app.root)
        self.top.title("Edit Item")
        self.top.geometry("520x440")
        self.top.configure(bg=COLOR_BG)

        # Load current book data
        book = app.data[index]

        # Header
        header = tk.Frame(self.top, bg=COLOR_PRIMARY, height=70)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        title = tk.Label(header, text="✏️ Edit Item Details", 
                        font=("Segoe UI", 14, "bold"), fg="white", bg=COLOR_PRIMARY)
        title.pack(pady=15)

        # Main frame
        main = tk.Frame(self.top, bg=COLOR_BG)
        main.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Form fields
        self.name_var = tk.StringVar(value=book.get('name',''))
        self.create_form_field(main, "📖 Title:", 0, self.name_var)

        self.author_var = tk.StringVar(value=book.get('author',''))
        self.create_form_field(main, "✍️ Author:", 1, self.author_var)

        self.date_var = tk.StringVar(value=book.get('date',''))
        self.create_form_field(main, "📅 Year:", 2, self.date_var, width=20)

        # Category dropdown
        cat_lbl = tk.Label(main, text="🏷️ Category:", font=("Segoe UI", 10, "bold"),
                          fg=COLOR_PRIMARY, bg=COLOR_BG)
        cat_lbl.grid(row=3, column=0, sticky='w', pady=(10, 5))

        self.cat_var = tk.StringVar(value=book.get('category','Uncategorized'))
        cats = ["Book", "Film", "Magazine"]
        self.cat_cb = ttk.Combobox(main, textvariable=self.cat_var, values=cats, 
                                   width=45, state='readonly', font=("Segoe UI", 10))
        self.cat_cb.grid(row=3, column=1, sticky='ew', pady=(10, 5))
        
        if self.cat_var.get() in cats:
            self.cat_cb.current(cats.index(self.cat_var.get()))
        else:
            self.cat_cb.set(self.cat_var.get())

        # Buttons frame
        btn_frame = tk.Frame(main, bg=COLOR_BG)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=(20, 0), sticky='ew')

        save_btn = tk.Button(btn_frame, text="✓ Save Changes", command=self.on_save,
                            bg=COLOR_SUCCESS, fg="white", font=("Segoe UI", 10, "bold"),
                            padx=30, pady=8, relief=tk.FLAT, cursor="hand2")
        save_btn.pack(side=tk.RIGHT, padx=(8, 0))

        cancel_btn = tk.Button(btn_frame, text="✕ Cancel", command=self.top.destroy,
                              bg="#BDBDBD", fg="white", font=("Segoe UI", 10, "bold"),
                              padx=30, pady=8, relief=tk.FLAT, cursor="hand2")
        cancel_btn.pack(side=tk.RIGHT)

    def create_form_field(self, parent, label, row, var, width=45):
        lbl = tk.Label(parent, text=label, font=("Segoe UI", 10, "bold"),
                      fg=COLOR_PRIMARY, bg=COLOR_BG)
        lbl.grid(row=row, column=0, sticky='w', pady=(0, 5))

        entry = ttk.Entry(parent, textvariable=var, width=width, font=("Segoe UI", 10))
        entry.grid(row=row, column=1, sticky='ew', pady=(0, 5))
        parent.grid_columnconfigure(1, weight=1)

        return entry

    def on_save(self):
        # Update the book at self.index with new values
        name = self.name_var.get().strip()
        author = self.author_var.get().strip()
        date = self.date_var.get().strip()
        cat = self.cat_var.get().strip() or 'Uncategorized'
        if not name:
            messagebox.showwarning("Validation", "Name is required")
            return
        # preserve id when updating
        item = self.app.data[self.index]
        item_id = item.get('id')
        # Try backend update
        try:
            resp = requests.put(f'http://127.0.0.1:5000/media/{item_id}', json={
                'name': name, 'author': author, 'date': date, 'category': cat
            }, timeout=1)
            if resp.status_code == 200:
                self.app.on_load()
                self.top.destroy()
                return
        except RequestException:
            pass

        # Fallback: update local data while preserving id
        self.app.data[self.index] = {**item, 'name': name, 'author': author, 'date': date, 'category': cat}
        self.app.write_json()
        self.app.on_load()
        self.top.destroy()


def main():
    root = tk.Tk()
    # Modernize style a bit
    try:
        style = ttk.Style()
        style.theme_use('clam')
    except Exception:
        pass

    LibraryApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()
