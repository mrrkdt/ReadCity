import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import shutil
import os
from PIL import Image, ImageTk

class AddEditProductWindow:
    def __init__(self, parent, product_id=None, callback=None):
        self.parent = parent
        self.product_id = product_id  # Если None - добавление, иначе - редактирование
        self.callback = callback  # Функция для обновления таблицы после сохранения
        self.image_path = None
        
        self.window = tk.Toplevel(parent)
        if product_id:
            self.window.title(f"Редактирование товара ID: {product_id}")
        else:
            self.window.title("Добавление нового товара")
        self.window.geometry("600x700")
        self.window.resizable(False, False)
        
        # Центрируем окно
        self.window.transient(parent)
        self.window.grab_set()
        
        self.create_widgets()
        
        if product_id:
            self.load_product_data()
    
    def create_widgets(self):
        # Основной фрейм с прокруткой
        canvas = tk.Canvas(self.window)
        scrollbar = ttk.Scrollbar(self.window, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Заголовок
        title = "Редактирование товара" if self.product_id else "Добавление нового товара"
        tk.Label(scrollable_frame, text=title, font=("Arial", 16, "bold")).pack(pady=10)
        
        # Форма
        form_frame = ttk.Frame(scrollable_frame, padding="20")
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Фото товара
        tk.Label(form_frame, text="Фото товара:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.photo_label = tk.Label(form_frame, text="Нет фото", width=20, height=10, relief="solid", bg="#f0f0f0")
        self.photo_label.grid(row=0, column=1, pady=5)
        self.photo_btn = ttk.Button(form_frame, text="Выбрать фото", command=self.select_photo)
        self.photo_btn.grid(row=0, column=2, padx=10)
        
        # Наименование товара
        tk.Label(form_frame, text="Наименование товара:*", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.name_entry = ttk.Entry(form_frame, width=40)
        self.name_entry.grid(row=1, column=1, columnspan=2, sticky=tk.W, pady=5)
        
        # Категория
        tk.Label(form_frame, text="Категория:*", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky=tk.W, pady=5)
        self.category_combo = ttk.Combobox(form_frame, width=37)
        self.category_combo.grid(row=2, column=1, columnspan=2, sticky=tk.W, pady=5)
        self.load_categories()
        
        # Описание
        tk.Label(form_frame, text="Описание:", font=("Arial", 10, "bold")).grid(row=3, column=0, sticky=tk.W, pady=5)
        self.desc_text = tk.Text(form_frame, width=40, height=5)
        self.desc_text.grid(row=3, column=1, columnspan=2, sticky=tk.W, pady=5)
        
        # Производитель
        tk.Label(form_frame, text="Производитель:", font=("Arial", 10, "bold")).grid(row=4, column=0, sticky=tk.W, pady=5)
        self.manufacturer_entry = ttk.Entry(form_frame, width=40)
        self.manufacturer_entry.grid(row=4, column=1, columnspan=2, sticky=tk.W, pady=5)
        
        # Поставщик
        tk.Label(form_frame, text="Поставщик:*", font=("Arial", 10, "bold")).grid(row=5, column=0, sticky=tk.W, pady=5)
        self.supplier_combo = ttk.Combobox(form_frame, width=37)
        self.supplier_combo.grid(row=5, column=1, columnspan=2, sticky=tk.W, pady=5)
        self.load_suppliers()
        
        # Цена
        tk.Label(form_frame, text="Цена:*", font=("Arial", 10, "bold")).grid(row=6, column=0, sticky=tk.W, pady=5)
        self.price_entry = ttk.Entry(form_frame, width=20)
        self.price_entry.grid(row=6, column=1, sticky=tk.W, pady=5)
        tk.Label(form_frame, text="руб.").grid(row=6, column=2, sticky=tk.W)
        
        # Единица измерения
        tk.Label(form_frame, text="Единица измерения:", font=("Arial", 10, "bold")).grid(row=7, column=0, sticky=tk.W, pady=5)
        self.unit_entry = ttk.Entry(form_frame, width=20)
        self.unit_entry.grid(row=7, column=1, sticky=tk.W, pady=5)
        self.unit_entry.insert(0, "шт")
        
        # Количество на складе
        tk.Label(form_frame, text="Количество на складе:*", font=("Arial", 10, "bold")).grid(row=8, column=0, sticky=tk.W, pady=5)
        self.quantity_entry = ttk.Entry(form_frame, width=20)
        self.quantity_entry.grid(row=8, column=1, sticky=tk.W, pady=5)
        self.quantity_entry.insert(0, "0")
        
        # Скидка
        tk.Label(form_frame, text="Действующая скидка (%):", font=("Arial", 10, "bold")).grid(row=9, column=0, sticky=tk.W, pady=5)
        self.discount_entry = ttk.Entry(form_frame, width=20)
        self.discount_entry.grid(row=9, column=1, sticky=tk.W, pady=5)
        self.discount_entry.insert(0, "0")
        
        # ID товара (только для редактирования)
        if self.product_id:
            tk.Label(form_frame, text="ID товара:", font=("Arial", 10, "bold")).grid(row=10, column=0, sticky=tk.W, pady=5)
            self.id_label = tk.Label(form_frame, text=str(self.product_id), fg="gray")
            self.id_label.grid(row=10, column=1, sticky=tk.W, pady=5)
        
        # Кнопки
        btn_frame = ttk.Frame(scrollable_frame)
        btn_frame.pack(pady=20)
        
        save_btn = ttk.Button(btn_frame, text="Сохранить", command=self.save_product)
        save_btn.pack(side=tk.LEFT, padx=10)
        
        cancel_btn = ttk.Button(btn_frame, text="Отмена", command=self.window.destroy)
        cancel_btn.pack(side=tk.LEFT, padx=10)
        
        # Примечание о обязательных полях
        tk.Label(scrollable_frame, text="* - обязательные поля", font=("Arial", 8), fg="red").pack(pady=5)
    
    def load_categories(self):
        """Загрузка категорий из БД"""
        conn = sqlite3.connect('database/bookstore.db')
        cursor = conn.cursor()
        cursor.execute("SELECT category_id, category_name FROM categories")
        categories = cursor.fetchall()
        conn.close()
        
        self.categories = {name: id for id, name in categories}
        self.category_combo['values'] = list(self.categories.keys())
    
    def load_suppliers(self):
        """Загрузка поставщиков из БД"""
        conn = sqlite3.connect('database/bookstore.db')
        cursor = conn.cursor()
        cursor.execute("SELECT supplier_id, supplier_name FROM suppliers")
        suppliers = cursor.fetchall()
        conn.close()
        
        self.suppliers = {name: id for id, name in suppliers}
        self.supplier_combo['values'] = list(self.suppliers.keys())
    
    def select_photo(self):
        """Выбор фото товара"""
        filetypes = [("Image files", "*.png *.jpg *.jpeg *.gif *.bmp")]
        filename = filedialog.askopenfilename(title="Выберите фото", filetypes=filetypes)
        if filename:
            self.image_path = filename
            # Показываем превью
            img = Image.open(filename)
            img = img.resize((100, 100), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            self.photo_label.config(image=photo, text="")
            self.photo_label.image = photo
    
    def load_product_data(self):
        """Загрузка данных товара для редактирования"""
        conn = sqlite3.connect('database/bookstore.db')
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.name, c.category_name, p.description, p.manufacturer, 
                   s.supplier_name, p.price, p.unit, p.quantity, p.discount, p.image_path
            FROM products p
            JOIN categories c ON p.category_id = c.category_id
            JOIN suppliers s ON p.supplier_id = s.supplier_id
            WHERE p.product_id = ?
        """, (self.product_id,))
        product = cursor.fetchone()
        conn.close()
        
        if product:
            name, category, desc, manufacturer, supplier, price, unit, quantity, discount, image_path = product
            
            self.name_entry.insert(0, name)
            self.category_combo.set(category)
            self.desc_text.insert("1.0", desc or "")
            self.manufacturer_entry.insert(0, manufacturer or "")
            self.supplier_combo.set(supplier)
            self.price_entry.insert(0, str(price))
            self.unit_entry.delete(0, tk.END)
            self.unit_entry.insert(0, unit or "шт")
            self.quantity_entry.delete(0, tk.END)
            self.quantity_entry.insert(0, str(quantity))
            self.discount_entry.delete(0, tk.END)
            self.discount_entry.insert(0, str(discount))
            
            if image_path and os.path.exists(image_path):
                self.image_path = image_path
                img = Image.open(image_path)
                img = img.resize((100, 100), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                self.photo_label.config(image=photo, text="")
                self.photo_label.image = photo
    
    def save_product(self):
        """Сохранение товара в БД"""
        # Проверка обязательных полей
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Ошибка", "Введите наименование товара")
            return
        
        category_name = self.category_combo.get()
        if not category_name or category_name not in self.categories:
            messagebox.showerror("Ошибка", "Выберите категорию")
            return
        
        supplier_name = self.supplier_combo.get()
        if not supplier_name or supplier_name not in self.suppliers:
            messagebox.showerror("Ошибка", "Выберите поставщика")
            return
        
        try:
            price = float(self.price_entry.get().strip())
            if price < 0:
                messagebox.showerror("Ошибка", "Цена не может быть отрицательной")
                return
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректную цену")
            return
        
        try:
            quantity = int(self.quantity_entry.get().strip())
            if quantity < 0:
                messagebox.showerror("Ошибка", "Количество не может быть отрицательным")
                return
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректное количество")
            return
        
        try:
            discount = float(self.discount_entry.get().strip())
            if discount < 0 or discount > 100:
                messagebox.showerror("Ошибка", "Скидка должна быть от 0 до 100")
                return
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректную скидку")
            return
        
        description = self.desc_text.get("1.0", tk.END).strip()
        manufacturer = self.manufacturer_entry.get().strip()
        unit = self.unit_entry.get().strip() or "шт"
        
        category_id = self.categories[category_name]
        supplier_id = self.suppliers[supplier_name]
        
        # Обработка фото
        saved_image_path = None
        if self.image_path:
            # Создаём папку для фото, если её нет
            if not os.path.exists('images'):
                os.makedirs('images')
            
            # Генерируем имя файла
            ext = os.path.splitext(self.image_path)[1]
            new_filename = f"product_{self.product_id if self.product_id else 'new'}{ext}"
            new_path = os.path.join('images', new_filename)
            
            # Копируем файл
            shutil.copy2(self.image_path, new_path)
            saved_image_path = new_path
            
            # Если редактирование и было старое фото - удаляем
            if self.product_id:
                conn = sqlite3.connect('database/bookstore.db')
                cursor = conn.cursor()
                cursor.execute("SELECT image_path FROM products WHERE product_id = ?", (self.product_id,))
                old_path = cursor.fetchone()
                conn.close()
                if old_path and old_path[0] and os.path.exists(old_path[0]) and old_path[0] != saved_image_path:
                    os.remove(old_path[0])
        
        # Сохраняем в БД
        conn = sqlite3.connect('database/bookstore.db')
        cursor = conn.cursor()
        
        if self.product_id:
            # Обновление
            cursor.execute("""
                UPDATE products 
                SET name=?, description=?, manufacturer=?, price=?, unit=?, 
                    quantity=?, discount=?, image_path=?, category_id=?, supplier_id=?
                WHERE product_id=?
            """, (name, description, manufacturer, price, unit, quantity, discount, saved_image_path, category_id, supplier_id, self.product_id))
        else:
            # Добавление
            cursor.execute("""
                INSERT INTO products (name, description, manufacturer, price, unit, quantity, discount, image_path, category_id, supplier_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (name, description, manufacturer, price, unit, quantity, discount, saved_image_path, category_id, supplier_id))
        
        conn.commit()
        conn.close()
        
        messagebox.showinfo("Успех", "Товар успешно сохранён!")
        
        if self.callback:
            self.callback()
        
        self.window.destroy()