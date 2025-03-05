import cv2
import numpy as np


def get_square_corners_on_original(image, corners):
    """
    Computes the corners of the chessboard squares and projects them back onto the original image.

    :param image: The displayed image as a NumPy array.
    :param corners: List of 4 marked points [(A1), (A8), (H1), (H8)]
    :return: List of fields with their corners [(A1, [(x1, y1), (x2, y2), ...]), (A2, [...]), ...]
    """
    # Assign the input points to meaningful names
    A1, A8, H1, H8 = corners

    # Define target coordinates for top-down view (chessboard from bird's eye view)
    width = 640  
    height = 480  
    dst_points = np.float32([
        [0, 0],      # A1 (Top-left in the transformed view)
        [0, height-1],  # A8 (Bottom-left in the transformed view)
        [width-1, 0],   # H1 (Top-right in the transformed view)
        [width-1, height-1]  # H8 (Bottom-right in the transformed view)
    ])

    # Compute perspective transformation matrix
    matrix = cv2.getPerspectiveTransform(np.float32([A1, A8, H1, H8]), dst_points)

    # Compute inverse transformation matrix (for back-projection)
    inverse_matrix = cv2.getPerspectiveTransform(dst_points, np.float32([A1, A8, H1, H8]))

    # Calculate cell size for the corrected chessboard
    rows, cols = 8, 8
    cell_width = width // cols
    cell_height = height // rows

    fields = []

    for i in range(rows):
        for j in range(cols):
            top_left_corner = (j * cell_width, i * cell_height)
            top_right_corner = ((j + 1) * cell_width, i * cell_height)
            bottom_left_corner = (j * cell_width, (i + 1) * cell_height)
            bottom_right_corner = ((j + 1) * cell_width, (i + 1) * cell_height)

            # Back-project to original image space
            top_left_original = cv2.perspectiveTransform(np.array([[top_left_corner]], dtype=np.float32), inverse_matrix)[0][0]
            top_right_original = cv2.perspectiveTransform(np.array([[top_right_corner]], dtype=np.float32), inverse_matrix)[0][0]
            bottom_left_original = cv2.perspectiveTransform(np.array([[bottom_left_corner]], dtype=np.float32), inverse_matrix)[0][0]
            bottom_right_original = cv2.perspectiveTransform(np.array([[bottom_right_corner]], dtype=np.float32), inverse_matrix)[0][0]

            field_label = chr(65 + j) + str(8 - i)  # A1, B1, ..., H8
            field_corners = [
                (top_left_original[0], top_left_original[1]),
                (top_right_original[0], top_right_original[1]),
                (bottom_right_original[0], bottom_right_original[1]),
                (bottom_left_original[0], bottom_left_original[1])
            ]
            fields.append((field_label, field_corners))

    return fields

def draw_chessboard(image, fields):
    """
    Draws the chessboard grid and labels each square.

    :param image: The original image (NumPy array).
    :param fields: List of tuples [(label, [(x1, y1), (x2, y2), (x3, y3), (x4, y4)])].
                   Each tuple represents a chess square with its four corner coordinates.
    :return: Image with the chessboard drawn.
    """
    img_copy = image.copy()

    for field_label, corners in fields:
        print(f"Drawing field: {field_label} with corners: {corners}")
        
        # Convert corner coordinates to integer explicitly
        pts = np.array([(int(x), int(y)) for x, y in corners], dtype=np.int32)

        # Draw the square outline
        cv2.polylines(img_copy, [pts], isClosed=True, color=(0, 255, 0), thickness=2)

        # Compute the center of the square
        center_x = int(sum(x for x, y in corners) / 4)
        center_y = int(sum(y for x, y in corners) / 4)

        # Draw the label in the center
        print(f"Center: ({center_x}, {center_y})")
        cv2.putText(img_copy, field_label, (center_x - 10, center_y + 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2, cv2.LINE_AA)

    return img_copy
