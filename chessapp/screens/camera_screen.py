from kivy.utils import platform
if platform == "android":
    from android.storage import primary_external_storage_path
else:
    def primary_external_storage_path(): 
        print("primary_external_storage_path() not implemented for this platform")
        return ""

from kivy.uix.screenmanager import Screen

# from kivy.app import App
# from kivy.uix.boxlayout import BoxLayout
# from kivy.graphics.texture import Texture
# from kivy.lang import Builder
# import numpy as np
# import cv2
# import platform
# import os
# from kivy.uix.screenmanager import Screen
# from plyer import camera as Camera
# #from kivy.uix.camera import Camera

# from kivy_reloader.utils import load_kv_path

# camera_screen_kv = os.path.join("chessapp", "screens", "camera_screen.kv")
# load_kv_path(camera_screen_kv)

# # Only import camera module on Android
# if platform.system() == 'Linux' and 'ANDROID_ARGUMENT' in os.environ:
    
#     class AndroidCamera(Camera):
#         # pass
#         camera_resolution = (640, 480)
#         counter = 0

#         def _camera_loaded(self, *largs):
#             self.texture = Texture.create(size=np.flip(self.camera_resolution), colorfmt='rgb')
#             self.texture_size = list(self.texture.size)

#         def on_tex(self, *l):
#             if self._camera._buffer is None:
#                 return None
#             frame = self.frame_from_buf()
#             self.frame_to_screen(frame)
#             super(AndroidCamera, self).on_tex(*l)

#         def frame_from_buf(self):
#             w, h = self.resolution
#             frame = np.frombuffer(self._camera._buffer.tostring(), 'uint8').reshape((h + h // 2, w))
#             frame_bgr = cv2.cvtColor(frame, 93)
#             return np.rot90(frame_bgr, 3)

#         def frame_to_screen(self, frame):
#             frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#             cv2.putText(frame_rgb, str(self.counter), (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
#             self.counter += 1
#             flipped = np.flip(frame_rgb, 0)
#             buf = flipped.tostring()
#             self.texture.blit_buffer(buf, colorfmt='rgb', bufferfmt='ubyte')

# class CameraScreen(Screen):
#     pass

# """
# Basic camera example
# Default picture is saved as
# /sdcard/org.test.cameraexample/enter_file_name_here.jpg
# """

# from os import getcwd
# from os.path import exists
# import os

# from kivy.app import App

# from plyer import camera

# from kivy_reloader.utils import load_kv_path

# camera_screen_kv = os.path.join("chessapp", "screens", "camera_screen.kv")
# load_kv_path(camera_screen_kv)

# class CameraScreen(Screen):

#     def on_enter(self):
#         if platform == "android":
#             from android.permissions import request_permissions, Permission
#             request_permissions([Permission.CAMERA, Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])
#         print("CameraScreen.on_enter()")

#     def on_leave(self):
#         print("CameraScreen.on_leave()")

#     def do_capture(self):
#         #self.cwd = getcwd() + "/"
#         #self.ids.path_label.text = self.cwd
#         #filepath = self.cwd + self.ids.filename_text.text
#         filepath = primary_external_storage_path() + "/" + "test.jpg"

#         if exists(filepath):
#             # popup = MsgPopup("Picture with this name already exists!")
#             # popup.open()
#             print("Picture with this name already exists!")
#             return False

#         try:
#             camera.take_picture(filename=filepath,
#                                 on_complete=self.camera_callback)
#         except NotImplementedError:
#             # popup = MsgPopup(
#             #     "This feature has not yet been implemented for this platform.")
#             # popup.open()
#             print("This feature has not yet been implemented for this platform.")

#     def camera_callback(self, filepath):
#         if exists(filepath):
#             # popup = MsgPopup("Picture saved!")
#             # popup.open()
#             print("Picture saved!")
#         else:
#             # popup = MsgPopup("Could not save your picture!")
#             # popup.open()
#             print("Could not save your picture!")


# from kivy.lang import Builder
# from kivy.utils import platform
# from kivy.clock import Clock
# from plyer import camera

import os
from kivy_reloader.utils import load_kv_path

camera_screen_kv = os.path.join("chessapp", "screens", "camera_screen.kv")
load_kv_path(camera_screen_kv)


from kivy.uix.camera import Camera
from kivy.clock import Clock
import numpy as np
import cv2

class AndroidCamera(Camera):
    camera_resolution = (640, 480)
    cam_ratio = camera_resolution[0] / camera_resolution[1]
    
class CameraScreen(Screen):
#     """
#     Screen for camera functionality - displays live camera feed and captures photos
#     """

    def on_start(self):
        Clock.schedule_once(self.get_frame, 5)

    def get_frame(self, dt):
        self.test_opencv()
        
        Clock.schedule_once(self.get_frame, 0.25)

    def test_opencv(self):
        cam = self.root.ids.a_cam
        image_object = cam.export_as_image(scale=round((400 / int(cam.height)), 2))
        w, h = image_object._texture.size
        frame = np.frombuffer(image_object._texture.pixels, 'uint8').reshape(h, w, 4)
        gray = cv2.cvtColor(frame, cv2.COLOR_RGBA2GRAY)
        # # Convert gray back to RGBA for displaying
        # gray_rgba = cv2.cvtColor(gray, cv2.COLOR_GRAY2RGBA)
        # # Update the camera texture with the grayscale image
        # texture = cam.texture.create(size=(w, h), colorfmt='rgba')
        # texture.blit_buffer(gray_rgba.tobytes(), colorfmt='rgba', bufferfmt='ubyte')
        # cam.texture = texture
        print("test_opencv")