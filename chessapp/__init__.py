from chessapp.screens.main_screen import MainScreen
from chessapp.screens.imagecrop_screen import ImageCropScreen
from chessapp.screens.camera_screen import CameraScreen
from chessapp.screens.cv2preprocessed_screen import Cv2PreProcessedScreen
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition, FallOutTransition, RiseInTransition, WipeTransition, NoTransition

from kivy_reloader.app import App

from kivy.utils import platform
if platform == "android":
    from android.permissions import request_permissions, Permission
    request_permissions([Permission.INTERNET, Permission.CAMERA, Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])

TRANSITION_DURATION = 0.25
TRANSITION_LEFT = WipeTransition(duration=TRANSITION_DURATION)# left right?
TRANSITION_RIGHT = WipeTransition(duration=TRANSITION_DURATION)

screen_manager = ScreenManager(transition=TRANSITION_RIGHT)
class MainApp(App):
    def on_start(self):
        from kivy.base import EventLoop
        
        # Attach keyboard hook when app starts (Mainly for backbutton on Android)
        EventLoop.window.bind(on_keyboard=self.hook_keyboard)

    def hook_keyboard(self, window, key, *largs):
        # key == 27 means ESC but on android it is the back button
        if key == 27:
            if self.screen_manager.current != 'main_screen': # No action if we are at mainscreen
                self.screen_manager.transition = TRANSITION_LEFT # testing transitions
                self.screen_manager.current = self.screen_manager.previous()
                self.screen_manager.transition = TRANSITION_RIGHT
                # self.screen_manager.switch_to(self.screen_manager.previous()) # Doesnt work because its expects scene not name
        return True 

    def build(self):
        #return MainScreen()
        # # Create the screen manager
        self.screen_manager = screen_manager
        self.screen_manager.add_widget(MainScreen(name='main_screen'))
        self.screen_manager.add_widget(CameraScreen(name='camera_screen'))
        self.screen_manager.add_widget(Cv2PreProcessedScreen(name='cv2preprocessed_screen'))
        self.screen_manager.add_widget(ImageCropScreen(name='imagecrop_screen'))

        # screens = [MainScreen(name='main'), CameraScreen(name='camera')]
        # self.screen_manager.switch_to(screens[0])

        return self.screen_manager
