import sqlite3
import os

def create_database():
    # Создаём папку database если её нет
    if not os.path.exists('database'):
        os.makedirs('database')
    
    connection = sqlite3.connect('database/bookstore.db')
    cursor = connection.cursor()
    
    # 1. Роли пользователей
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS roles (
        role_id INTEGER PRIMARY KEY AUTOINCREMENT,
        role_name TEXT NOT NULL UNIQUE
    )
    ''')
    
    # 2. Пользователи
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        surname TEXT NOT NULL,
        name TEXT NOT NULL,
        patronymic TEXT,
        login TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        role_id INTEGER NOT NULL,
        FOREIGN KEY (role_id) REFERENCES roles(role_id)
    )
    ''')
    
    # 3. Категории товаров
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS categories (
        category_id INTEGER PRIMARY KEY AUTOINCREMENT,
        category_name TEXT NOT NULL UNIQUE
    )
    ''')
    
    # 4. Поставщики
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS suppliers (
        supplier_id INTEGER PRIMARY KEY AUTOINCREMENT,
        supplier_name TEXT NOT NULL UNIQUE
    )
    ''')
    
    # 5. Товары
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        product_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        manufacturer TEXT,
        price REAL NOT NULL,
        unit TEXT,
        quantity INTEGER NOT NULL,
        discount REAL DEFAULT 0,
        image_path TEXT,
        category_id INTEGER NOT NULL,
        supplier_id INTEGER NOT NULL,
        FOREIGN KEY (category_id) REFERENCES categories(category_id),
        FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id)
    )
    ''')
    
    # 6. Статусы заказов
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS order_statuses (
        status_id INTEGER PRIMARY KEY AUTOINCREMENT,
        status_name TEXT NOT NULL UNIQUE
    )
    ''')
    
    # 7. Заказы
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        order_id INTEGER PRIMARY KEY AUTOINCREMENT,
        article TEXT UNIQUE,
        pickup_address TEXT NOT NULL,
        order_date TEXT NOT NULL,
        issue_date TEXT,
        status_id INTEGER NOT NULL,
        FOREIGN KEY (status_id) REFERENCES order_statuses(status_id)
    )
    ''')
    
    # 8. Связь заказов и товаров
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS order_products (
        order_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        PRIMARY KEY (order_id, product_id),
        FOREIGN KEY (order_id) REFERENCES orders(order_id),
        FOREIGN KEY (product_id) REFERENCES products(product_id)
    )
    ''')
    
    # Заполнение начальными данными
    # Роли
    cursor.execute("INSERT OR IGNORE INTO roles (role_id, role_name) VALUES (1, 'Администратор')")
    cursor.execute("INSERT OR IGNORE INTO roles (role_id, role_name) VALUES (2, 'Менеджер')")
    cursor.execute("INSERT OR IGNORE INTO roles (role_id, role_name) VALUES (3, 'Клиент')")
    
    # Статусы заказов
    cursor.execute("INSERT OR IGNORE INTO order_statuses (status_id, status_name) VALUES (1, 'Новый')")
    cursor.execute("INSERT OR IGNORE INTO order_statuses (status_id, status_name) VALUES (2, 'В обработке')")
    cursor.execute("INSERT OR IGNORE INTO order_statuses (status_id, status_name) VALUES (3, 'Готов к выдаче')")
    cursor.execute("INSERT OR IGNORE INTO order_statuses (status_id, status_name) VALUES (4, 'Выдан')")
    cursor.execute("INSERT OR IGNORE INTO order_statuses (status_id, status_name) VALUES (5, 'Отменен')")
    
    # Администратор
    cursor.execute("""
    INSERT OR IGNORE INTO users (surname, name, patronymic, login, password, role_id)
    VALUES ('Администратор', 'Системный', NULL, 'admin', 'admin', 1)
    """)
    
    # Менеджер (для теста)
    cursor.execute("""
    INSERT OR IGNORE INTO users (surname, name, patronymic, login, password, role_id)
    VALUES ('Иванов', 'Петр', 'Сидорович', 'manager', 'manager', 2)
    """)
    
    # Клиент (для теста)
    cursor.execute("""
    INSERT OR IGNORE INTO users (surname, name, patronymic, login, password, role_id)
    VALUES ('Петрова', 'Анна', 'Ивановна', 'client', 'client', 3)
    """)
    
    # Тестовые категории
    cursor.execute("INSERT OR IGNORE INTO categories (category_id, category_name) VALUES (1, 'Художественная литература')")
    cursor.execute("INSERT OR IGNORE INTO categories (category_id, category_name) VALUES (2, 'Научная литература')")
    cursor.execute("INSERT OR IGNORE INTO categories (category_id, category_name) VALUES (3, 'Детская литература')")
    
    # Тестовые поставщики
    cursor.execute("INSERT OR IGNORE INTO suppliers (supplier_id, supplier_name) VALUES (1, 'ООО Книжный Мир')")
    cursor.execute("INSERT OR IGNORE INTO suppliers (supplier_id, supplier_name) VALUES (2, 'ИП Иванов А.А.')")
    
    # Тестовые товары
    cursor.execute("""
    INSERT OR IGNORE INTO products (product_id, name, description, manufacturer, price, unit, quantity, discount, image_path, category_id, supplier_id)
    VALUES (1, 'Война и мир', 'Роман-эпопея Льва Толстого', 'Эксмо', 500.00, 'шт', 10, 0, NULL, 1, 1)
    """)
    cursor.execute("""
    INSERT OR IGNORE INTO products (product_id, name, description, manufacturer, price, unit, quantity, discount, image_path, category_id, supplier_id)
    VALUES (2, 'Python для начинающих', 'Учебник по программированию', 'Питер', 1200.00, 'шт', 0, 30, NULL, 2, 2)
    """)
    cursor.execute("""
    INSERT OR IGNORE INTO products (product_id, name, description, manufacturer, price, unit, quantity, discount, image_path, category_id, supplier_id)
    VALUES (3, 'Колобок', 'Русская народная сказка', 'Росмэн', 200.00, 'шт', 25, 15, NULL, 3, 1)
    """)

    # Добавь после существующих товаров:
    (4, 'Мастер и Маргарита', 'Роман Михаила Булгакова', 'АСТ', 650.00, 'шт', 15, 10, None, 1, 1),
    (5, 'Программирование на Python', 'Полное руководство', 'О\'Рейли', 2500.00, 'шт', 5, 20, None, 2, 2),
    (6, 'Маленький принц', 'Философская сказка', 'Эксмо', 350.00, 'шт', 30, 5, None, 3, 1)
    
    connection.commit()
    connection.close()
    print("База данных успешно создана!")

if __name__ == "__main__":
    create_database()