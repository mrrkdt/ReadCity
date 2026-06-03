import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import create_database

def main():
    create_database()
    from ui.login_window_tk import LoginWindow
    app = LoginWindow()
    app.run()

if __name__ == "__main__":
    main()