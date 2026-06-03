import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

class AddEditOrderWindow:
    def __init__(self, parent, order_id=None, callback=None):
        self.parent = parent
        self.order_id = order_id
        self.callback = callback
        
        self.window = tk.Toplevel(parent)
        if order_id:
            self.window.title(f"Редактирование заказа №{order_id}")
        else:
            self.window.title("Добавление нового заказа")
        self.window.geometry("500x500")
        self.window.resizable(False, False)
        
        self.window.transient(parent)
        self.window.grab_set()
        
        self.create_widgets()
        
        if order_id:
            self.load_order_data()
    
    def create_widgets(self):
        form_frame = ttk.Frame(self.window, padding="20")
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Артикул
        tk.Label(form_frame, text="Артикул:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky=tk.W, pady=10)
        self.article_entry = ttk.Entry(form_frame, width=30)
        self.article_entry.grid(row=0, column=1, sticky=tk.W, pady=10)
        
        # Статус заказа
        tk.Label(form_frame, text="Статус заказа:*", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky=tk.W, pady=10)
        self.status_combo = ttk.Combobox(form_frame, width=27)
        self.status_combo.grid(row=1, column=1, sticky=tk.W, pady=10)
        self.load_statuses()
        
        # Адрес пункта выдачи
        tk.Label(form_frame, text="Адрес пункта выдачи:*", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky=tk.W, pady=10)
        self.address_entry = ttk.Entry(form_frame, width=30)
        self.address_entry.grid(row=2, column=1, sticky=tk.W, pady=10)
        
        # Дата заказа
        tk.Label(form_frame, text="Дата заказа:*", font=("Arial", 10, "bold")).grid(row=3, column=0, sticky=tk.W, pady=10)
        self.order_date_entry = ttk.Entry(form_frame, width=30)
        self.order_date_entry.grid(row=3, column=1, sticky=tk.W, pady=10)
        self.order_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        tk.Label(form_frame, text="(Формат: ГГГГ-ММ-ДД)", font=("Arial", 8), fg="gray").grid(row=4, column=1, sticky=tk.W)
        
        # Дата выдачи
        tk.Label(form_frame, text="Дата выдачи:", font=("Arial", 10, "bold")).grid(row=5, column=0, sticky=tk.W, pady=10)
        self.issue_date_entry = ttk.Entry(form_frame, width=30)
        self.issue_date_entry.grid(row=5, column=1, sticky=tk.W, pady=10)
        tk.Label(form_frame, text="(Оставьте пустым, если не выдано)", font=("Arial", 8), fg="gray").grid(row=6, column=1, sticky=tk.W)
        
        # ID заказа (только для редактирования)
        if self.order_id:
            tk.Label(form_frame, text="ID заказа:", font=("Arial", 10, "bold")).grid(row=7, column=0, sticky=tk.W, pady=10)
            self.id_label = tk.Label(form_frame, text=str(self.order_id), fg="gray")
            self.id_label.grid(row=7, column=1, sticky=tk.W, pady=10)
        
        # Кнопки
        btn_frame = ttk.Frame(self.window)
        btn_frame.pack(pady=20)
        
        save_btn = ttk.Button(btn_frame, text="Сохранить", command=self.save_order)
        save_btn.pack(side=tk.LEFT, padx=10)
        
        cancel_btn = ttk.Button(btn_frame, text="Отмена", command=self.window.destroy)
        cancel_btn.pack(side=tk.LEFT, padx=10)
        
        tk.Label(self.window, text="* - обязательные поля", font=("Arial", 8), fg="red").pack(pady=5)
    
    def load_statuses(self):
        """Загрузка статусов из БД"""
        conn = sqlite3.connect('database/bookstore.db')
        cursor = conn.cursor()
        cursor.execute("SELECT status_id, status_name FROM order_statuses")
        statuses = cursor.fetchall()
        conn.close()
        
        self.statuses = {name: id for id, name in statuses}
        self.status_combo['values'] = list(self.statuses.keys())
        if self.status_combo['values']:
            self.status_combo.set(self.status_combo['values'][0])
    
    def load_order_data(self):
        """Загрузка данных заказа для редактирования"""
        conn = sqlite3.connect('database/bookstore.db')
        cursor = conn.cursor()
        cursor.execute("""
            SELECT article, status_id, pickup_address, order_date, issue_date
            FROM orders
            WHERE order_id = ?
        """, (self.order_id,))
        order = cursor.fetchone()
        conn.close()
        
        if order:
            article, status_id, address, order_date, issue_date = order
            
            if article:
                self.article_entry.insert(0, article)
            
            # Находим название статуса по ID
            for name, sid in self.statuses.items():
                if sid == status_id:
                    self.status_combo.set(name)
                    break
            
            self.address_entry.insert(0, address)
            self.order_date_entry.delete(0, tk.END)
            self.order_date_entry.insert(0, order_date)
            if issue_date:
                self.issue_date_entry.insert(0, issue_date)

    def change_status(self):
        """Изменение статуса заказа (для менеджера)"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите заказ")
            return
        
        new_status = self.status_combo.get()
        if not new_status:
            messagebox.showwarning("Внимание", "Выберите новый статус")
            return
        
        order_id = self.tree.set(selected[0], "order_id")
        
        # Получаем ID статуса
        conn = sqlite3.connect('database/bookstore.db')
        cursor = conn.cursor()
        cursor.execute("SELECT status_id FROM order_statuses WHERE status_name = ?", (new_status,))
        status_id = cursor.fetchone()[0]
        
        # Обновляем статус заказа
        cursor.execute("UPDATE orders SET status_id = ? WHERE order_id = ?", (status_id, order_id))
        conn.commit()
        conn.close()
        
        messagebox.showinfo("Успех", f"Статус заказа #{order_id} изменён на '{new_status}'")
        self.load_orders()
    
    def save_order(self):
        """Сохранение заказа в БД"""
        # Проверка обязательных полей
        status_name = self.status_combo.get()
        if not status_name or status_name not in self.statuses:
            messagebox.showerror("Ошибка", "Выберите статус заказа")
            return
        
        address = self.address_entry.get().strip()
        if not address:
            messagebox.showerror("Ошибка", "Введите адрес пункта выдачи")
            return
        
        order_date = self.order_date_entry.get().strip()
        if not order_date:
            messagebox.showerror("Ошибка", "Введите дату заказа")
            return
        
        # Простая проверка формата даты
        try:
            datetime.strptime(order_date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Ошибка", "Неверный формат даты. Используйте ГГГГ-ММ-ДД")
            return
        
        issue_date = self.issue_date_entry.get().strip()
        if issue_date:
            try:
                datetime.strptime(issue_date, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Ошибка", "Неверный формат даты выдачи. Используйте ГГГГ-ММ-ДД")
                return
        else:
            issue_date = None
        
        article = self.article_entry.get().strip()
        if not article:
            article = None
        
        status_id = self.statuses[status_name]
        
        conn = sqlite3.connect('database/bookstore.db')
        cursor = conn.cursor()
        
        if self.order_id:
            # Обновление
            cursor.execute("""
                UPDATE orders 
                SET article=?, pickup_address=?, order_date=?, issue_date=?, status_id=?
                WHERE order_id=?
            """, (article, address, order_date, issue_date, status_id, self.order_id))
        else:
            # Добавление
            cursor.execute("""
                INSERT INTO orders (article, pickup_address, order_date, issue_date, status_id)
                VALUES (?, ?, ?, ?, ?)
            """, (article, address, order_date, issue_date, status_id))
        
        conn.commit()
        conn.close()
        
        messagebox.showinfo("Успех", "Заказ успешно сохранён!")
        
        if self.callback:
            self.callback()
        
        self.window.destroy()