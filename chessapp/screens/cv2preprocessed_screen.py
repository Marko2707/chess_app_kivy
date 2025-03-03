import os
import cv2
import numpy as np

from kivy.uix.screenmanager import Screen

from kivy_reloader.utils import load_kv_path
from kivy.graphics.texture import Texture
from kivy.graphics import Rectangle

cv2preprocessed_screen = os.path.join("chessapp", "screens", "cv2preprocessed_screen.kv")
load_kv_path(cv2preprocessed_screen)


class Cv2PreProcessedScreen(Screen):
    def on_pre_enter(self):
        image_object = self.manager.get_screen('camera_screen').ids.a_cam.export_as_image()
        w, h = image_object._texture.size
        frame = np.frombuffer(image_object._texture.pixels, 'uint8').reshape(h, w, 4)
        gray = cv2.cvtColor(frame, cv2.COLOR_RGBA2GRAY)

        # # Convert gray back to RGBA for displaying
        gray = cv2.cvtColor(gray, cv2.COLOR_GRAY2RGBA)
        # # Update the camera texture with the grayscale image
        # texture = cam.texture.create(size=(w, h), colorfmt='rgba')
        # texture.blit_buffer(gray_rgba.tobytes(), colorfmt='rgba', bufferfmt='ubyte')
        # cam.texture = texture

        # Convert to kivy texture to display on the canvas
        texture = Texture.create(size=(gray.shape[1], gray.shape[0]))
        texture.blit_buffer(gray.tobytes(), colorfmt='rgba', bufferfmt='ubyte')
        self.ids.cv2_display.canvas.before.clear()
        with self.ids.cv2_display.canvas:
            Rectangle(texture=texture, size=self.ids.cv2_display.size, pos=self.ids.cv2_display.pos)
        # print(gray)
        print("Cv2PreProcessedScreen.on_enter()")