# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

class BookmarkClassifier:
    def __init__(self, root):
        self.root = root
        self.root.title("Bookmark Classifier")
        self.root.geometry("800x600")
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configure colors
        self.bg_color = "#2d2d2d"
        self.accent_color = "#4a9cff"
        self.text_color = "#ffffff"
        
        self.root.configure(bg=self.bg_color)
        self.create_db()
        self.create_widgets()
        self.load_bookmarks()

    def create_db(self):
        self.conn = sqlite3.connect('bookmarks.db')
        self.c = self.conn.cursor()
        self.c.execute('''CREATE TABLE IF NOT EXISTS bookmarks
                         (id INTEGER PRIMARY KEY AUTOINCREMENT,
                         url TEXT, title TEXT, category TEXT,
                         added_date DATETIME)''')
        self.conn.commit()

    def create_widgets(self):
        # Input Frame
        input_frame = ttk.Frame(self.root)
        input_frame.pack(pady=20, padx=20, fill=tk.X)

        self.url_entry = ttk.Entry(input_frame, width=50)
        self.url_entry.pack(side=tk.LEFT, padx=5)
        
        add_btn = ttk.Button(input_frame, text="Add Bookmark", 
                            command=self.add_bookmark)
        add_btn.pack(side=tk.LEFT, padx=5)

        # Categories
        self.categories = ['News', 'Sports', 'Education', 'Entertainment', 
                          'Technology', 'Shopping', 'Social Media', 'Other']
        
        # Notebook for categories
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill=tk.BOTH, padx=20, pady=10)
        
        # Create tabs for each category
        self.tabs = {}
        for category in self.categories:
            frame = ttk.Frame(self.notebook)
            self.tabs[category] = frame
            self.notebook.add(frame, text=category)
            
            # Treeview for bookmarks
            tree = ttk.Treeview(frame, columns=('url', 'title', 'date'), 
                              show='headings', selectmode='browse')
            tree.heading('url', text='URL')
            tree.heading('title', text='Title')
            tree.heading('date', text='Date Added')
            tree.column('url', width=300)
            tree.column('title', width=200)
            tree.column('date', width=150)
            tree.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
            
            # Context menu
            menu = tk.Menu(tree, tearoff=0)
            menu.add_command(label="Edit", command=lambda t=tree: self.edit_bookmark(t))
            menu.add_command(label="Delete", command=lambda t=tree: self.delete_bookmark(t))
            tree.bind("<Button-3>", lambda e, m=menu: m.post(e.x_root, e.y_root))

    def classify_bookmark(self, url):
        # Simple classification logic (can be enhanced with ML)
        url = url.lower()
        keywords = {
            'news': ['news', 'times', 'post', 'journal'],
            'sports': ['sports', 'nba', 'fifa', 'olympic'],
            'education': ['edu', 'course', 'academy', 'learning'],
            'technology': ['tech', 'gadget', 'software', 'ai'],
            'shopping': ['shop', 'store', 'buy', 'deal'],
            'social media': ['facebook', 'twitter', 'instagram', 'linkedin']
        }
        
        for category, terms in keywords.items():
            if any(term in url for term in terms):
                return category.capitalize()
        return 'Other'

    def add_bookmark(self):
        url = self.url_entry.get()
        if not url:
            messagebox.showerror("Error", "Please enter a URL")
            return
            
        category = self.classify_bookmark(url)
        title = url.split('//')[-1].split('/')[0]  # Simple title extraction
        date = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        # Add to database
        self.c.execute("INSERT INTO bookmarks (url, title, category, added_date) VALUES (?,?,?,?)",
                      (url, title, category, date))
        self.conn.commit()
        
        # Add to UI
        self.update_tab_content(category)
        self.url_entry.delete(0, tk.END)

    def load_bookmarks(self):
        for category in self.categories:
            self.update_tab_content(category)

    def update_tab_content(self, category):
        tree = self.tabs[category].winfo_children()[0]
        tree.delete(*tree.get_children())
        
        self.c.execute("SELECT url, title, added_date FROM bookmarks WHERE category=?", (category,))
        for row in self.c.fetchall():
            tree.insert('', tk.END, values=row)

    def edit_bookmark(self, tree):
        selected = tree.selection()
        if not selected:
            return
            
        item = tree.item(selected[0])
        old_url = item['values'][0]
        
        edit_win = tk.Toplevel(self.root)
        edit_win.title("Edit Bookmark")
        
        ttk.Label(edit_win, text="New URL:").pack(padx=10, pady=5)
        url_entry = ttk.Entry(edit_win, width=50)
        url_entry.insert(0, old_url)
        url_entry.pack(padx=10, pady=5)
        
        ttk.Label(edit_win, text="Category:").pack(padx=10, pady=5)
        category_var = tk.StringVar()
        category_drop = ttk.Combobox(edit_win, textvariable=category_var, 
                                    values=self.categories)
        category_drop.pack(padx=10, pady=5)
        
        def save_changes():
            new_url = url_entry.get()
            new_category = category_var.get()
            
            self.c.execute("UPDATE bookmarks SET url=?, category=? WHERE url=?",
                          (new_url, new_category, old_url))
            self.conn.commit()
            
            self.update_tab_content(new_category)
            if new_category != item['values'][2]:
                self.update_tab_content(item['values'][2])
            edit_win.destroy()

        ttk.Button(edit_win, text="Save", command=save_changes).pack(pady=10)

    def delete_bookmark(self, tree):
        selected = tree.selection()
        if not selected:
            return
            
        url = tree.item(selected[0])['values'][0]
        self.c.execute("DELETE FROM bookmarks WHERE url=?", (url,))
        self.conn.commit()
        tree.delete(selected[0])

if __name__ == "__main__":
    root = tk.Tk()
    app = BookmarkClassifier(root)
    root.mainloop()
