import os
import cv2
import webbrowser

from kivy.uix.screenmanager import Screen

from kivy_reloader.utils import load_kv_path

main_screen_kv = os.path.join("chessapp", "screens", "main_screen.kv")
load_kv_path(main_screen_kv)


class MainScreen(Screen):
    def openWebsite(self, text):
        webbrowser.open('https://lichess.org/editor/rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR_w_KQkq_-_0_1?color=white')
        
