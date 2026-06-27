import sys
from PyQt6.QtWidgets import QApplication, QStackedWidget
from PyQt6.QtCore import Qt

from core.constants import APP_NAME
from core.styles import GLOBAL_STYLE
from ui.login_window import LoginWindow
from ui.main_window import MainWindow


class Application(QStackedWidget):
    def __init__(self):
        super().__init__()
        self._login = LoginWindow()
        self._main: MainWindow | None = None
        self.addWidget(self._login)
        self._login.login_success.connect(self._on_login)
        self.setWindowTitle(APP_NAME)
        self.resize(1100, 680)

    def _on_login(self, username: str) -> None:
        self._main = MainWindow(username)
        self.addWidget(self._main)
        self.setCurrentWidget(self._main)
        self.resize(self._main.size())
        self.setWindowTitle(self._main.windowTitle())


def main() -> int:
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setStyle("Fusion")
    app.setStyleSheet(GLOBAL_STYLE)

    window = Application()
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
