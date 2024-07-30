import os
import sys
from PyQt6.QtGui import QFontDatabase, QFont
from PyQt6.QtWidgets import QApplication

class FontLoader:
    def __init__(self):
        self.get_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.lexendbold_path = os.path.join(self.get_path, "font", "Lexend-Bold.ttf")
        self.edu_path = os.path.join(self.get_path, "font", "EduAUVICWANTHand-Regular.ttf")
        
        self.lexendbold = self.load_font(self.lexendbold_path)
        self.edu = self.load_font(self.edu_path)

    def load_font(self, font_path):
        font_id = QFontDatabase.addApplicationFont(font_path)
        if font_id == -1:
            print(f"Failed to load font at {font_path}")
            return None
        font_family = QFontDatabase.applicationFontFamilies(font_id)
        if font_family:
            print(f"Successfully loaded font at {font_path}")
            return font_family[0]
        else:
            print(f"Failed to get font family for font at {font_path}")
            return None

# Example usage:
font_loader = FontLoader()

# Assuming you have a MainWindow class or similar where you want to set the font:
class MainWindow:
    def __init__(self):
        self.font_loader = FontLoader()
        self.setup_home_page()

    def setup_home_page(self):
        if self.font_loader.lexendbold:
            self.cover_image.setFont(QFont(self.font_loader.lexendbold))
        else:
            print("LexendBold font not loaded")

        if self.font_loader.edu:
            self.other_element.setFont(QFont(self.font_loader.edu))
        else:
            print("Edu font not loaded")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
