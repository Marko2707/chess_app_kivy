from kivy.uix.camera import Camera
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.graphics import Rectangle, Line, Color, Ellipse, PushMatrix, Rotate, Scale, PopMatrix
import numpy as np
import cv2
import os
from kivy.uix.screenmanager import Screen
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy_reloader.utils import load_kv_path
from kivy.core.window import Window
from kivy.core.text import Label as CoreLabel
from kivy.uix.boxlayout import BoxLayout
from kivy.app import App
from kivy.core.image import Image as CoreImage
from kivy.uix.image import Image




from corner_based_approach import get_square_corners_on_original, draw_chessboard

imagecrop_screen = os.path.join("chessapp", "screens", "imagecrop_screen.kv")
load_kv_path(imagecrop_screen)


class AndroidCamera(Camera):
    camera_resolution = (640, 480)
    cam_ratio = camera_resolution[0] / camera_resolution[1]


class ImageCropScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.camera = self.ids.camera

    def on_enter(self):
        self.camera.play = True

    def on_leave(self):
        self.camera.play = False

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
        print("Image Res: ", image.shape[:2])
        
        print("Image Res: ", image.shape[:2])
        
        # Display the captured image
        buf1 = image.tobytes()  # Use the original image without flipping 
        texture = Texture.create(size=(image.shape[1], image.shape[0]), colorfmt='rgb')
        texture.blit_buffer(buf1, colorfmt='rgb', bufferfmt='ubyte')
        img_widget = Widget()
        with img_widget.canvas:
            Rectangle(texture=texture, pos=(0, 0), size=(image.shape[1], image.shape[0]))
            Rectangle(texture=texture, pos=(0, 0), size=(image.shape[1], image.shape[0]))

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
        save_button = Button(text='Save Positions', size_hint=(None, None), size=(450, 150),
                            pos_hint={'center_x': 0.5, 'y': 0.05})
        save_button.bind(on_press=self.save_positions)
        
        # This is important to not mess up the pixel detection later to get the squares:
        save_button.padding = [0, 0]  # Remove any internal padding
        save_button.margin = [0, 0]   # Remove any margin if set

        
        # This is important to not mess up the pixel detection later to get the squares:
        save_button.padding = [0, 0]  # Remove any internal padding
        save_button.margin = [0, 0]   # Remove any margin if set

        self.add_widget(save_button)

        
    def save_positions(self, instance):
        if not hasattr(self, 'captured_image'):
            print("No image captured yet!")
            return
        
        # Retrieve and print the coordinates for each dot based on its label.
        coords = {dot["label"]: dot["pos"] for dot in self.crop_widget.dots}
        print(coords)

        button_height = 150  # Your button's height
        coords = {label: [x, y - button_height] for label, (x, y) in coords.items()}

        # Make sure all 4 corners are set
        if all(label in coords for label in ["A1", "A8", "H1", "H8"]):
            ordered_corners = [coords["A1"], coords["A8"], coords["H1"], coords["H8"]]
            print(ordered_corners)

            print(ordered_corners)

            # Call function to compute square positions
            fields = get_square_corners_on_original(self.captured_image, ordered_corners)
            
            # Print or store the results
            print("Computed field positions:", fields)
            

            img_copy = draw_chessboard(self.captured_image, fields)

            #save_path = "/storage/emulated/0/Download/test_output.jpg"  # Save in Downloads folder
            #cv2.imwrite(save_path, img_copy)

            # Convert BGR to RGB
            img_rgb = cv2.cvtColor(img_copy, cv2.COLOR_BGR2RGB)

            # Flip image vertically to align with Kivy's coordinate system
            img_rgb = cv2.flip(img_rgb, 0)

            # Convert to texture
            texture = Texture.create(size=(img_rgb.shape[1], img_rgb.shape[0]), colorfmt='rgb')
            texture.blit_buffer(img_rgb.tobytes(), colorfmt='rgb', bufferfmt='ubyte')

            # Display the image in the app
            if hasattr(self, 'image_widget'):
                self.image_widget.texture = texture  # Update existing image
            else:
                self.image_widget = Image(texture=texture)
                self.add_widget(self.image_widget)  # Add to layoutut

        else:
            print("Not all 4 corners have been set!")
        
        # Fields are the coordinates of the task
        return fields


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
        offset = 400  
        offset = 400  
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








