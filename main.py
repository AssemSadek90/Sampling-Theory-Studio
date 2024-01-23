import sys
from Defs import COLOR5
from app import *

if __name__ == "__main__":
    # Initialize Our Window App
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    win = Window()
    win.setStyleSheet(f"background-color:{COLOR5}")
    win.show()

    # Run the application
    sys.exit(app.exec_())
