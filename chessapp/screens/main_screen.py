import os
import cv2
import webbrowser

from kivy.uix.screenmanager import Screen

from kivy_reloader.utils import load_kv_path

main_screen_kv = os.path.join("chessapp", "screens", "main_screen.kv")
load_kv_path(main_screen_kv)

class MainScreen(Screen):
    def openWebsite(self, url):
        webbrowser.open(url)
