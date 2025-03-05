import os
import cv2
import numpy as np
from kivy.uix.screenmanager import Screen
from kivy.uix.widget import Widget
from kivy.graphics import Line, Color, Ellipse, Rectangle
from kivy.graphics.texture import Texture
from kivy.uix.button import Button
from kivy_reloader.utils import load_kv_path
from kivy.uix.camera import Camera
from kivy.core.window import Window
from kivy.core.text import Label as CoreLabel
from kivy.uix.boxlayout import BoxLayout

from corner_based_approach import get_square_corners_on_original, draw_chessboard

imagecrop_screen = os.path.join("chessapp", "screens", "imagecrop_screen.kv")
load_kv_path(imagecrop_screen)

# class AndroidCamera(Camera):
#     camera_resolution = (640, 480)  # Lower fixed resolution
#     cam_ratio = camera_resolution[0] / camera_resolution[1]

#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#         self.resolution = self.camera_resolution  # Set lower resolution
#         self.keep_ratio = True  # Stretch to fit screen
#         self.allow_stretch = True  # Enable stretching

class AndroidCamera(Camera):
    camera_resolution = (640, 480)
    cam_ratio = camera_resolution[0] / camera_resolution[1]

from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button
from kivy.uix.camera import Camera
from kivy.graphics import PushMatrix, Rotate, Scale, PopMatrix
from kivy.core.window import Window
from kivy.app import App

class ImageCropScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.camera = self.ids.camera
        #self.camera.size = Window.size  # Stretch to full screen
        #self.camera.pos = (0, 0)
        #self.add_widget(self.camera)
        
        # self.capture_button = Button(text='Capture', size_hint=(None, None), size=(300, 150),
        #                              pos_hint={'center_x': 0.5, 'y': 0.05})
        # self.capture_button.bind(on_press=self.capture)
        #self.add_widget(self.capture_button)

    
    def capture(self, instance):
        # Capture the frame from the camera
        # texture = self.camera.texture
        texture = self.camera.export_as_image()
        texture = texture._texture
        if texture:
            size = texture.size
            pixels = texture.pixels
            image = np.frombuffer(pixels, dtype=np.uint8).reshape(size[1], size[0], 4)
            image = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)
            self.display_image(image)
        
    def display_image(self, image):
        self.clear_widgets()  # Remove previous widgets (camera, buttons, etc.)

        # Store the captured image for later use
        self.captured_image = image  # Store it in the instance for later access
        image = cv2.flip(image, 1)
        # Display the captured image
        buf1 = image.tobytes()  # Use the original image without flipping 
        texture = Texture.create(size=(image.shape[1], image.shape[0]), colorfmt='rgb')
        texture.blit_buffer(buf1, colorfmt='rgb', bufferfmt='ubyte')
        img_widget = Widget()
        with img_widget.canvas:
            Rectangle(texture=texture, pos=(0, 0), size=Window.size)

        with img_widget.canvas.before:
            PushMatrix()
            Rotate(
                angle=180,
                origin=self.center,
            ),
      
        # Apply PopMatrix after transformations are done
        with img_widget.canvas.after:
            PopMatrix()
        self.add_widget(img_widget)

        
        # Create the CropWidget overlay with draggable dots
        self.crop_widget = CropWidget(size=Window.size, pos=(0, 0))
        self.add_widget(self.crop_widget)

        # Add a button to save/get the dot positions
        save_button = Button(text='Save Positions', size_hint=(None, None), size=(300, 150),
                            pos_hint={'center_x': 0.5, 'y': 0.05})
        save_button.bind(on_press=self.save_positions)
        self.add_widget(save_button)

        
    def save_positions(self, instance):
        if not hasattr(self, 'captured_image'):
            print("No image captured yet!")
            return
        
        # Retrieve and print the coordinates for each dot based on its label.
        coords = {dot["label"]: dot["pos"] for dot in self.crop_widget.dots}
        

        image_width, image_height = 640, 480
        # Get the screen width and height
        screen_width, screen_height = Window.size
        print(f"Screen width: {screen_width}, Screen height: {screen_height}")

        # Calculate scaling factors for x and y
        scale_x = image_width / screen_width
        scale_y = image_height / screen_height
        print("TEST1")
        print(coords)
        # Scale the coordinates in the coords dictionary
        # Assuming scale_x and scale_y are calculated correctly
        coords = {label: [x * scale_x, y * scale_y] for label, [x, y] in coords.items()}

        print("TEST2")

        # Make sure all 4 corners are set
        if all(label in coords for label in ["A1", "A8", "H1", "H8"]):
            ordered_corners = [coords["A1"], coords["A8"], coords["H1"], coords["H8"]]
            
            # Call function to compute square positions
            fields = get_square_corners_on_original(self.captured_image, ordered_corners)
            
            # Print or store the results
            #print("Computed field positions:", fields)
            import pprint

            pprint.pprint(fields)

            img_copy = draw_chessboard(self.captured_image, fields)
            print("HALLO")
            save_path = "/storage/emulated/0/Download/test_output.jpg"  # Save in Downloads folder
            cv2.imwrite(save_path, img_copy)


            print(f"Saved annotated image to {save_path}")

        else:
            print("Not all 4 corners have been set!")


class CropWidget(Widget):
    def __init__(self, **kwargs):
        super(CropWidget, self).__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = kwargs.get('size', Window.size)
        # Define each dot with position, color, and label text.
        self.dots = [
            {"pos": [self.center_x - 50, self.center_y - 50], "color": (1, 0, 0, 1), "label": "A1"},  # Red
            {"pos": [self.center_x + 50, self.center_y - 50], "color": (0, 1, 0, 1), "label": "H1"},  # Green
            {"pos": [self.center_x + 50, self.center_y + 50], "color": (0, 0, 1, 1), "label": "H8"},  # Blue
            {"pos": [self.center_x - 50, self.center_y + 50], "color": (1, 1, 0, 1), "label": "A8"}   # Yellow
        ]
        self.selected_dot = None
        self.dot_radius = 20  # Drawn radius (dot will have a 40px diameter)
        self.bind(pos=self.update_positions, size=self.update_positions)
        self.update_positions()

    def update_positions(self, *args):
        offset = 150  # 150 is 100 pixels more than the original 50
        self.dots[0]["pos"] = [self.x + offset, self.y + offset]           # Bottom-left becomes 100px closer to center
        self.dots[1]["pos"] = [self.right - offset, self.y + offset]         # Bottom-right
        self.dots[2]["pos"] = [self.right - offset, self.top - offset]         # Top-right
        self.dots[3]["pos"] = [self.x + offset, self.top - offset]           # Top-left
        self.update_canvas()

    def update_canvas(self):
        self.canvas.clear()
        for dot in self.dots:
            with self.canvas:
                # Draw the dot.
                Color(*dot["color"])
                x, y = dot["pos"]
                Ellipse(pos=(x - self.dot_radius, y - self.dot_radius),
                        size=(self.dot_radius * 2, self.dot_radius * 2))
                # Create a CoreLabel for the dot's text.
                core_label = CoreLabel(text=dot.get("label", ""),
                                       font_size=100,
                                       color=(1, 1, 1, 1))
                core_label.refresh()
                text_texture = core_label.texture
                # Draw the text above the dot.
                Rectangle(texture=text_texture,
                          pos=(x - text_texture.width / 2, y + self.dot_radius + 5),
                          size=text_texture.size)

    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return False
        # Define extra hit tolerance.
        dot_hit_tolerance = 180
        for i, dot in enumerate(self.dots):
            x, y = dot["pos"]
            if abs(touch.x - x) < self.dot_radius + dot_hit_tolerance and \
               abs(touch.y - y) < self.dot_radius + dot_hit_tolerance:
                self.selected_dot = i
                return True
        return super(CropWidget, self).on_touch_down(touch)

    def on_touch_move(self, touch):
        if self.selected_dot is not None and self.collide_point(*touch.pos):
            self.dots[self.selected_dot]["pos"] = [touch.x, touch.y]
            self.update_canvas()
            return True
        return super(CropWidget, self).on_touch_move(touch)

    def on_touch_up(self, touch):
        self.selected_dot = None
        return super(CropWidget, self).on_touch_up(touch)






