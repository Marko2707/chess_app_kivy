import os
import cv2
import numpy as np

from kivy.uix.screenmanager import Screen

from kivy_reloader.utils import load_kv_path

from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.graphics import Rectangle

cv2preprocessed_screen = os.path.join("chessapp", "screens", "cv2preprocessed_screen.kv")
load_kv_path(cv2preprocessed_screen)


class Cv2PreProcessedScreen(Screen):
    
    def on_pre_enter(self):
        print(self.manager.current)
        self.processImage()
    
    def enhanceEdges(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # Adaptive thresholding to handle varying lighting
        thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                    cv2.THRESH_BINARY, 11, 2)
        # Edge enhancement
        kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
        enhanced = cv2.filter2D(thresh, -1, kernel)
        return enhanced
    
    def processImage(self, *args):
        if self.manager.current != 'cv2preprocessed_screen':
            return
        cam = self.manager.get_screen('camera_screen').ids.a_cam
        image_object = cam.export_as_image(scale=round((cam.camera_resolution[1] / int(cam.height)), 2))
        w, h = image_object._texture.size
        frame = np.frombuffer(image_object._texture.pixels, 'uint8').reshape(h, w, 4)
        gray = cv2.cvtColor(frame, cv2.COLOR_RGBA2GRAY)

        # Apply bilateral filter to reduce noise while preserving edges
        filtered = cv2.bilateralFilter(gray, 9, 75, 75)
        
        # Otsu's thresholding
        _, thresh = cv2.threshold(filtered, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Edge detection
        edges = cv2.Canny(thresh, 50, 150)
        
        # Probabilistic Hough Transform
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, 50, 
                            minLineLength=200,  # Minimum line length
                            maxLineGap=50)      # Maximum gap between line segments
        if lines is not None:
            black = gray#np.zeros_like(gray)
            # Convert to point format and calculate angles
            point_lines = []
            angles = []
            for line in lines:
                x1, y1, x2, y2 = line[0]
                #x1, y1, x2, y2 = line.reshape(4)
                length = np.sqrt((x2-x1)**2 + (y2-y1)**2)
                angle = np.degrees(np.arctan2(y2-y1, x2-x1)) % 180

                cv2.line(black, (x1, y1), (x2, y2), (0, 0, 255), 1)
                
                # Only keep longer lines
                if length > gray.shape[0]/5:  # At least 1/4 of image height
                    point_lines.append(((x1,y1), (x2,y2)))
                    angles.append(angle)
                    cv2.line(black, (x1, y1), (x2, y2), (255, 0, 125), 1)
            image = black
        else:
            print(self.manager.current, ": No lines found")
            image = edges
            
        # # Convert gray back to RGBA for displaying
        # Convert to kivy texture to display on the canvas
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGBA)
        texture = Texture.create(size=(image.shape[1], image.shape[0]))
        texture.blit_buffer(image.tobytes(), colorfmt='rgba', bufferfmt='ubyte')
        self.ids.cv2_display.canvas.before.clear()
        with self.ids.cv2_display.canvas:
            Rectangle(texture=texture, size=self.ids.cv2_display.size, pos=self.ids.cv2_display.pos)
            #Callback(self.my_callback)

        Clock.schedule_once(self.processImage, 0.1)
        
