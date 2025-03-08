import trio

from chessapp import MainApp
app = MainApp()

# from chessapp.screens.camera2_screen import CameraApp
# app = CameraApp()

trio.run(app.async_run, "trio")
