from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QTextBrowser,
    QPushButton
)
from PyQt6.QtGui import QIcon
from importlib.resources import files

class InstructionsWindow(QDialog):
    def __init__(self, html_text: str, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Instructions")
        icon = str(files("neuroarcade.ui.icons").joinpath("help_question_flight.svg"))
        self.setWindowIcon(QIcon(icon))
        self.resize(600, 500)

        layout = QVBoxLayout(self)

        # Scrollable rich text viewer
        self.text_browser = QTextBrowser()
        self.text_browser.setOpenExternalLinks(True)
        self.text_browser.setHtml(html_text)

        layout.addWidget(self.text_browser)

        # Close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)

        self.setLayout(layout)
