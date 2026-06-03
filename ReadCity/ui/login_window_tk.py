import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
import os

class ProductsWindow:
    def __init__(self, parent, user_id=None, role="Гость", full_name=""):
        self.parent = parent
        self.user_id = user_id
        self.role = role
        self.full_name = full_name
        self.current_sort = "Без сортировки"
        self.current_filter = "Все диапазоны"
        self.current_search = ""
        self.edit_window = None
        
        self.window = tk.Toplevel(parent)
        self.window.title("Список товаров")
        self.window.geometry("1200x700")
        self.window.state('zoomed')
        
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.X, pady=(0, 10))
        
        title_label = tk.Label(top_frame, text="КАТАЛОГ КНИГ", font=("Arial", 18, "bold"))
        title_label.pack(side=tk.LEFT)
        
        if full_name:
            name_label = tk.Label(top_frame, text=full_name, font=("Arial", 10), fg="gray")
            name_label.pack(side=tk.RIGHT, padx=10)
        
        logout_btn = ttk.Button(top_frame, text="Выйти", command=self.logout)
        logout_btn.pack(side=tk.RIGHT, padx=5)
        
        if role in ["Менеджер", "Администратор"]:
            orders_btn = ttk.Button(top_frame, text="Заказы", command=self.open_orders)
            orders_btn.pack(side=tk.RIGHT, padx=5)
        
        if role == "Администратор":
            add_btn = ttk.Button(top_frame, text="+ Добавить товар", command=self.add_product)
            add_btn.pack(side=tk.RIGHT, padx=5)
            delete_btn = ttk.Button(top_frame, text="🗑 Удалить товар", command=self.delete_product)
            delete_btn.pack(side=tk.RIGHT, padx=5)
        
        if role in ["Менеджер", "Администратор"]:
            control_frame = ttk.LabelFrame(main_frame, text="Управление", padding="10")
            control_frame.pack(fill=tk.X, pady=(0, 10))
            
            search_frame = ttk.Frame(control_frame)
            search_frame.pack(fill=tk.X, pady=5)
            ttk.Label(search_frame, text="🔍 Поиск:").pack(side=tk.LEFT)
            self.search_entry = ttk.Entry(search_frame, width=40)
            self.search_entry.pack(side=tk.LEFT, padx=5)
            self.search_entry.bind('<KeyRelease>', self.on_search)
            
            filter_frame = ttk.Frame(control_frame)
            filter_frame.pack(fill=tk.X, pady=5)
            ttk.Label(filter_frame, text="📊 Фильтр по скидке:").pack(side=tk.LEFT)
            self.filter_combo = ttk.Combobox(filter_frame, values=["Все диапазоны", "0-12.99%", "13-16.99%", "17% и более"], width=20)
            self.filter_combo.pack(side=tk.LEFT, padx=5)
            self.filter_combo.set("Все диапазоны")
            self.filter_combo.bind('<<ComboboxSelected>>', self.on_filter)
            
            sort_frame = ttk.Frame(control_frame)
            sort_frame.pack(fill=tk.X, pady=5)
            ttk.Label(sort_frame, text="📌 Сортировка:").pack(side=tk.LEFT)
            self.sort_combo = ttk.Combobox(sort_frame, values=["Без сортировки", "Цена ↑", "Цена ↓", "Количество ↑", "Количество ↓"], width=20)
            self.sort_combo.pack(side=tk.LEFT, padx=5)
            self.sort_combo.set("Без сортировки")
            self.sort_combo.bind('<<ComboboxSelected>>', self.on_sort)
        
        table_frame = ttk.Frame(main_frame)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ("id", "photo", "name", "category", "description", "manufacturer", "price", "unit", "quantity", "discount")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=25)
        
        self.tree.heading("id", text="ID")
        self.tree.heading("photo", text="Фото")
        self.tree.heading("name", text="Наименование")
        self.tree.heading("category", text="Категория")
        self.tree.heading("description", text="Описание")
        self.tree.heading("manufacturer", text="Производитель")
        self.tree.heading("price", text="Цена")
        self.tree.heading("unit", text="Ед.изм.")
        self.tree.heading("quantity", text="Кол-во")
        self.tree.heading("discount", text="Скидка")
        
        self.tree.column("id", width=50)
        self.tree.column("photo", width=80)
        self.tree.column("name", width=150)
        self.tree.column("category", width=100)
        self.tree.column("description", width=200)
        self.tree.column("manufacturer", width=120)
        self.tree.column("price", width=100)
        self.tree.column("unit", width=70)
        self.tree.column("quantity", width=80)
        self.tree.column("discount", width=80)
        
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        if role == "Администратор":
            self.tree.bind("<Double-1>", self.edit_product)
        
        self.load_products()
    
    def load_products(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        conn = sqlite3.connect('database/bookstore.db')
        cursor = conn.cursor()
        
        query = '''
        SELECT p.product_id, p.name, c.category_name, p.description, 
               p.manufacturer, p.price, p.unit, p.quantity, p.discount,
               p.image_path
        FROM products p
        JOIN categories c ON p.category_id = c.category_id
        WHERE 1=1
        '''
        params = []
        
        if self.role in ["Менеджер", "Администратор"] and self.current_search:
            query += " AND (p.name LIKE ? OR p.description LIKE ? OR p.manufacturer LIKE ?)"
            like = f"%{self.current_search}%"
            params.extend([like, like, like])
        
        if self.role in ["Менеджер", "Администратор"] and self.current_filter != "Все диапазоны":
            if self.current_filter == "0-12.99%":
                query += " AND p.discount BETWEEN 0 AND 12.99"
            elif self.current_filter == "13-16.99%":
                query += " AND p.discount BETWEEN 13 AND 16.99"
            elif self.current_filter == "17% и более":
                query += " AND p.discount >= 17"
        
        if self.current_sort != "Без сортировки":
            if self.current_sort == "Цена ↑":
                query += " ORDER BY p.price ASC"
            elif self.current_sort == "Цена ↓":
                query += " ORDER BY p.price DESC"
            elif self.current_sort == "Количество ↑":
                query += " ORDER BY p.quantity ASC"
            elif self.current_sort == "Количество ↓":
                query += " ORDER BY p.quantity DESC"
        else:
            query += " ORDER BY p.product_id"
        
        cursor.execute(query, params)
        products = cursor.fetchall()
        conn.close()
        
        for product in products:
            product_id, name, category, desc, manufacturer, price, unit, quantity, discount, image_path = product
            
            final_price = price * (100 - discount) / 100
            if discount > 0:
                price_text = f"{final_price:.2f}₽\n(было {price:.2f}₽)"
            else:
                price_text = f"{price:.2f}₽"
            
            tags = []
            if quantity == 0:
                tags.append("out_of_stock")
            elif discount > 25:
                tags.append("high_discount")
            
            item = self.tree.insert("", tk.END, values=(
                product_id, "📷", name, category, (desc or "")[:50], 
                manufacturer or "", price_text, unit or "шт", quantity, f"{discount}%"
            ), tags=tags)
            
            self.tree.set(item, "id", product_id)
        
        self.tree.tag_configure("out_of_stock", background="#D3D3D3")
        self.tree.tag_configure("high_discount", background="#23E1EF")
    
    def on_search(self, event):
        self.current_search = self.search_entry.get()
        self.load_products()
    
    def on_filter(self, event):
        self.current_filter = self.filter_combo.get()
        self.load_products()
    
    def on_sort(self, event):
        self.current_sort = self.sort_combo.get()
        self.load_products()
    
    def logout(self):
        self.window.destroy()
        from ui.login_window_tk import LoginWindow
        login_app = LoginWindow()
        login_app.run()
    
    def open_orders(self):
        from ui.orders_window import OrdersWindow
        OrdersWindow(self.window, self.role)
    
    def add_product(self):
        from ui.add_edit_product_window import AddEditProductWindow
        AddEditProductWindow(self.window, callback=self.load_products)
    
    def edit_product(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        
        if hasattr(self, 'edit_window') and self.edit_window and self.edit_window.winfo_exists():
            messagebox.showwarning("Внимание", "Закройте сначала текущее окно редактирования")
            return
        
        product_id = self.tree.set(selected[0], "id")
        from ui.add_edit_product_window import AddEditProductWindow
        self.edit_window = AddEditProductWindow(self.window, product_id=product_id, callback=self.load_products)
    
    def delete_product(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите товар для удаления")
            return
        
        product_id = self.tree.set(selected[0], "id")
        product_name = self.tree.set(selected[0], "name")
        
        conn = sqlite3.connect('database/bookstore.db')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM order_products WHERE product_id = ?", (product_id,))
        count = cursor.fetchone()[0]
        conn.close()
        
        if count > 0:
            messagebox.showerror("Ошибка", "Невозможно удалить товар, который присутствует в заказах")
            return
        
        if messagebox.askyesno("Подтверждение", f"Удалить товар '{product_name}'?"):
            conn = sqlite3.connect('database/bookstore.db')
            cursor = conn.cursor()
            cursor.execute("SELECT image_path FROM products WHERE product_id = ?", (product_id,))
            image_path = cursor.fetchone()
            if image_path and image_path[0] and os.path.exists(image_path[0]):
                os.remove(image_path[0])
            
            cursor.execute("DELETE FROM products WHERE product_id = ?", (product_id,))
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Успех", "Товар удалён")
            self.load_products()


class LoginWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Авторизация")
        self.root.geometry("350x250")
        self.root.resizable(False, False)
        
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="Логин:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.login_entry = ttk.Entry(main_frame, width=25)
        self.login_entry.grid(row=0, column=1, pady=5)
        
        ttk.Label(main_frame, text="Пароль:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.password_entry = ttk.Entry(main_frame, width=25, show="*")
        self.password_entry.grid(row=1, column=1, pady=5)
        
        login_btn = ttk.Button(main_frame, text="Войти", command=self.login)
        login_btn.grid(row=2, column=0, columnspan=2, pady=10)
        
        guest_btn = ttk.Button(main_frame, text="Войти как гость", command=self.enter_as_guest)
        guest_btn.grid(row=3, column=0, columnspan=2, pady=5)
        
        self.login_entry.bind("<Return>", lambda e: self.login())
        self.password_entry.bind("<Return>", lambda e: self.login())
    
    def login(self):
        login = self.login_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not login or not password:
            messagebox.showwarning("Ошибка", "Введите логин и пароль")
            return
        
        try:
            conn = sqlite3.connect('database/bookstore.db')
            cursor = conn.cursor()
            cursor.execute("""
                SELECT u.user_id, u.surname, u.name, u.patronymic, r.role_name
                FROM users u
                JOIN roles r ON u.role_id = r.role_id
                WHERE u.login = ? AND u.password = ?
            """, (login, password))
            user = cursor.fetchone()
            conn.close()
            
            if user:
                user_id = user[0]
                surname = user[1]
                name = user[2]
                patronymic = user[3] if user[3] else ""
                full_name = f"{surname} {name} {patronymic}".strip()
                role = user[4]
                
                messagebox.showinfo("Успех", f"Добро пожаловать, {full_name}!\nРоль: {role}")
                ProductsWindow(self.root, user_id, role, full_name)
            else:
                messagebox.showerror("Ошибка", "Неверный логин или пароль")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка БД:\n{str(e)}")
    
    def enter_as_guest(self):
        ProductsWindow(self.root, None, "Гость", "")
    
    def run(self):
        self.root.mainloop()