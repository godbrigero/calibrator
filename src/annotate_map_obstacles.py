import cv2
import numpy as np
import json
import os


class MapAnnotator:
    def __init__(self):
        self.image_path = input("Enter the path to your map image: ")
        if not os.path.exists(self.image_path):
            print("Image file not found. Exiting...")
            return

        self.square_size = float(
            input("What is the square size in meters in the real world? ")
        )

        self.grid_size = int(input("What is the size of each grid square in pixels? "))

        self.pixels_per_meter = self.grid_size / self.square_size
        self.squares_per_meter = 1 / self.square_size

        self.image = cv2.imread(self.image_path)
        self.height, self.width = self.image.shape[:2]
        self.display_image = self.image.copy()
        self.original_image = self.image.copy()

        self.obstacles = set()
        self.is_dragging = False
        self.last_grid_pos = None
        self.draw_grid()

        cv2.namedWindow("Map Annotator")
        cv2.setMouseCallback("Map Annotator", self.on_click)

        print("Click and drag to select squares. Press 's' to save and exit.")

        while True:
            cv2.imshow("Map Annotator", self.display_image)
            key = cv2.waitKey(1) & 0xFF

            if key == ord("s"):
                self.save_annotations()
                break
            elif key == ord("q"):
                print("Exiting without saving...")
                break

        cv2.destroyAllWindows()

    def draw_grid(self):
        self.display_image = self.original_image.copy()
        for x in range(0, self.width, self.grid_size):
            cv2.line(self.display_image, (x, 0), (x, self.height), (128, 128, 128), 1)

        for y in range(0, self.height, self.grid_size):
            cv2.line(self.display_image, (0, y), (self.width, y), (128, 128, 128), 1)

        # Redraw all obstacles
        for grid_x, grid_y in self.obstacles:
            x1 = grid_x * self.grid_size
            y1 = grid_y * self.grid_size
            x2 = x1 + self.grid_size
            y2 = y1 + self.grid_size
            self.display_image[y1:y2, x1:x2] = (0, 0, 255)

    def toggle_square(self, grid_x, grid_y):
        if (grid_x, grid_y) in self.obstacles:
            self.obstacles.remove((grid_x, grid_y))
        else:
            self.obstacles.add((grid_x, grid_y))
        self.draw_grid()

    def on_click(self, event, x, y, flags, param):
        grid_x = x // self.grid_size
        grid_y = y // self.grid_size

        if event == cv2.EVENT_LBUTTONDOWN:
            self.is_dragging = True
            self.last_grid_pos = (grid_x, grid_y)
            self.toggle_square(grid_x, grid_y)
        elif event == cv2.EVENT_MOUSEMOVE and self.is_dragging:
            if self.last_grid_pos != (grid_x, grid_y):
                self.toggle_square(grid_x, grid_y)
                self.last_grid_pos = (grid_x, grid_y)
        elif event == cv2.EVENT_LBUTTONUP:
            self.is_dragging = False
            self.last_grid_pos = None

    def save_annotations(self):
        obstacles_list = [{"x": x, "y": y} for x, y in self.obstacles]

        annotation_data = {
            "image_path": self.image_path,
            "square_size_meters": self.square_size,
            "grid_size_pixels": self.grid_size,
            "pixels_per_meter": self.pixels_per_meter,
            "squares_per_meter": self.squares_per_meter,
            "obstacles": obstacles_list,
        }

        output_path = (
            "out/" + os.path.splitext(self.image_path)[0] + "_annotations.json"
        )
        with open(output_path, "w") as f:
            json.dump(annotation_data, f, indent=4)

        print(f"Annotations saved to {output_path}")


if __name__ == "__main__":
    annotator = MapAnnotator()
