import trio

from chessapp import MainApp

app = MainApp()
trio.run(app.async_run, "trio")
