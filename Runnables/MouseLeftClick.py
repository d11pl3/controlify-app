from PyQt5.QtCore import QRunnable
import logging
import pyautogui

logging.basicConfig(format="%(message)s", level=logging.INFO)

# 1. Subclass QRunnable
class MouseLeftClickRunnable(QRunnable):
    def __init__(self):
        super().__init__()

    def run(self):
        # Your long-running task goes here ...
        logging.info("Left Click received!")
        pyautogui.leftClick()