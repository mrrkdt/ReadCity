import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

class OrdersWindow:
    def __init__(self, parent, role):
        self.parent = parent
        self.role = role
        self.edit_window = None
        
        self.window = tk.Toplevel(parent)
        self.window.title("Управление заказами")
        self.window.geometry("1100x600")
        self.window.state('zoomed')
        
        # Основной фрейм
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Заголовок
        title_label = tk.Label(main_frame, text="ЗАКАЗЫ", font=("Arial", 18, "bold"))
        title_label.pack(pady=(0, 10))
        
        # Кнопки для администратора
        if role == "Администратор":
            btn_frame = ttk.Frame(main_frame)
            btn_frame.pack(fill=tk.X, pady=(0, 10))
            
            add_btn = ttk.Button(btn_frame, text="+ Добавить заказ", command=self.add_order)
            add_btn.pack(side=tk.LEFT, padx=5)
            
            delete_btn = ttk.Button(btn_frame, text="🗑 Удалить заказ", command=self.delete_order)
            delete_btn.pack(side=tk.LEFT, padx=5)
        
        # Таблица заказов
        table_frame = ttk.Frame(main_frame)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ("order_id", "article", "status", "pickup_address", "order_date", "issue_date")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=20)
        
        self.tree.heading("order_id", text="ID заказа")
        self.tree.heading("article", text="Артикул")
        self.tree.heading("status", text="Статус")
        self.tree.heading("pickup_address", text="Адрес пункта выдачи")
        self.tree.heading("order_date", text="Дата заказа")
        self.tree.heading("issue_date", text="Дата выдачи")
        
        self.tree.column("order_id", width=80)
        self.tree.column("article", width=120)
        self.tree.column("status", width=150)
        self.tree.column("pickup_address", width=300)
        self.tree.column("order_date", width=120)
        self.tree.column("issue_date", width=120)
        
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Двойной клик для редактирования (только администратор)
        if role == "Администратор":
            self.tree.bind("<Double-1>", self.edit_order)
        
        # Кнопка закрытия
        close_btn = ttk.Button(main_frame, text="Закрыть", command=self.window.destroy)
        close_btn.pack(pady=10)
        
        # Загружаем заказы
        self.load_orders()

                # Кнопка для изменения статуса (для менеджера)
        if role == "Менеджер":
            status_frame = ttk.Frame(main_frame)
            status_frame.pack(fill=tk.X, pady=(0, 10))
            
            ttk.Label(status_frame, text="Изменить статус заказа:").pack(side=tk.LEFT, padx=5)
            self.status_combo = ttk.Combobox(status_frame, values=["Новый", "В обработке", "Готов к выдаче", "Выдан", "Отменен"], width=20)
            self.status_combo.pack(side=tk.LEFT, padx=5)
            
            change_status_btn = ttk.Button(status_frame, text="Применить", command=self.change_status)
            change_status_btn.pack(side=tk.LEFT, padx=5)
    
    def load_orders(self):
        """Загрузка заказов из БД"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        conn = sqlite3.connect('database/bookstore.db')
        cursor = conn.cursor()
        cursor.execute("""
            SELECT o.order_id, o.article, os.status_name, o.pickup_address, 
                   o.order_date, o.issue_date
            FROM orders o
            JOIN order_statuses os ON o.status_id = os.status_id
            ORDER BY o.order_id
        """)
        orders = cursor.fetchall()
        conn.close()
        
        for order in orders:
            order_id, article, status, address, order_date, issue_date = order
            self.tree.insert("", tk.END, values=(
                order_id, article or "", status, address, 
                order_date, issue_date or "Не выдано"
            ), tags=("order_row",))
            
            # Сохраняем ID
            self.tree.set(self.tree.get_children()[-1], "order_id", order_id)
    
    def add_order(self):
        """Добавление нового заказа"""
        if hasattr(self, 'edit_window') and self.edit_window and self.edit_window.winfo_exists():
            messagebox.showwarning("Внимание", "Закройте сначала текущее окно редактирования")
            return
        
        from ui.add_edit_order_window import AddEditOrderWindow
        self.edit_window = AddEditOrderWindow(self.window, callback=self.load_orders)
    
    def edit_order(self, event):
        """Редактирование заказа"""
        selected = self.tree.selection()
        if not selected:
            return
        
        if hasattr(self, 'edit_window') and self.edit_window and self.edit_window.winfo_exists():
            messagebox.showwarning("Внимание", "Закройте сначала текущее окно редактирования")
            return
        
        order_id = self.tree.set(selected[0], "order_id")
        from ui.add_edit_order_window import AddEditOrderWindow
        self.edit_window = AddEditOrderWindow(self.window, order_id=order_id, callback=self.load_orders)
    
    def delete_order(self):
        """Удаление заказа"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите заказ для удаления")
            return
        
        order_id = self.tree.set(selected[0], "order_id")
        article = self.tree.set(selected[0], "article")
        
        if messagebox.askyesno("Подтверждение", f"Удалить заказ #{order_id} (артикул: {article})?"):
            conn = sqlite3.connect('database/bookstore.db')
            cursor = conn.cursor()
            
            # Сначала удаляем связанные товары в заказе
            cursor.execute("DELETE FROM order_products WHERE order_id = ?", (order_id,))
            # Затем удаляем сам заказ
            cursor.execute("DELETE FROM orders WHERE order_id = ?", (order_id,))
            
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Успех", "Заказ удалён")
            self.load_orders()