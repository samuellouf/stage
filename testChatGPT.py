import tkinter as tk
import random
import time

CELL_SIZE = 50
GRID_SIZE = 6

# Données des dés
dice_values = [
    ['A1', 'C1', 'D1', 'D2', 'E2', 'F3'],
    ['A4', 'B5', 'C5', 'C6', 'D6', 'F6'],
    ['D5', 'E4', 'E5', 'E6', 'F4', 'F5'],
    ['A5', 'F2', 'A5', 'F2', 'B6', 'E1'],
    ['A2', 'A3', 'B1', 'B2', 'B3', 'C2'],
    ['B4', 'C3', 'C4', 'D3', 'D4', 'E3'],
    ['A6', 'A6', 'A6', 'F1', 'F1', 'F1']
]

def coord_to_grid(coord):
    letters = "ABCDEF"
    if len(coord) != 2:
        return None
    col = letters.index(coord[0])
    row = int(coord[1]) - 1
    return row, col

# Formes des pièces (9), chaque liste de tuples représente les offsets de la forme
PIECE_SHAPES = [
    [(0,0), (1,0), (2,0), (2,1)],       # cyan
    [(0,0)],                            # blue
    [(0,0), (1,0), (1,1), (2,1)],       # red
    [(0,0), (0,1), (0,2), (0,3)],       # grey
    [(0,0), (0,1)],                     # brown
    [(0,0), (1,0), (2,0), (1,1)],       # yellow
    [(0,0), (1,0), (0,1)],              # purple
    [(0,0), (1,0), (0,1), (1,1)],       # green (carré)
    [(0,0), (1,0), (2,0)],              # orange (barre 3)
]

PIECE_COLORS = [
    "cyan", "blue", "red", "gray", "brown",
    "yellow", "purple", "green", "orange"
]

class PuzzlePiece:
    def __init__(self, canvas, shape, color, x, y):
        self.canvas = canvas
        self.color = color
        self.shape = shape
        self.x = x
        self.y = y
        self.rotation = 0
        self.mirrored = False
        self.rects = []
        self.isOnGrid = False
        self.create_piece()
        self.bind_events()

    def create_piece(self):
        self.rects.clear()
        self.canvas_piece_ids = []
        for dx, dy in self.get_transformed_shape():
            rect = self.canvas.create_rectangle(
                self.x + dx * CELL_SIZE,
                self.y + dy * CELL_SIZE,
                self.x + dx * CELL_SIZE + CELL_SIZE,
                self.y + dy * CELL_SIZE + CELL_SIZE,
                fill=self.color,
                tags="draggable"
            )
            self.canvas_piece_ids.append(rect)

    def get_transformed_shape(self):
        transformed = []
        for dx, dy in self.shape:
            if self.mirrored:
                dy = -dy
            for _ in range(self.rotation % 4):
                dx, dy = -dy, dx
            transformed.append((dx, dy))
        return transformed

    def bind_events(self):
        for rect in self.canvas_piece_ids:
            self.canvas.tag_bind(rect, "<Button-3>", self.on_right_click)
            self.canvas.tag_bind(rect, "<B1-Motion>", self.do_drag)
            self.canvas.tag_bind(rect, "<ButtonRelease-1>", self.snap_to_grid)

    def on_click(self, event):
        if self.isOnGrid: return
        self.mirrored = not self.mirrored
        self.redraw()

    def on_right_click(self, event):
        if self.isOnGrid: return
        self.rotation += 1
        self.redraw()

    def do_drag(self, event):
        dx = event.x - self.x
        dy = event.y - self.y
        for rect in self.canvas_piece_ids:
            self.canvas.move(rect, dx, dy)
        self.x = event.x
        self.y = event.y

    def snap_to_grid(self, event):
        grid_origin_x = 300
        grid_origin_y = 0
        grid_x = (event.x - grid_origin_x) // CELL_SIZE
        grid_y = (event.y - grid_origin_y) // CELL_SIZE
        if 0 <= grid_x < GRID_SIZE and 0 <= grid_y < GRID_SIZE:
            self.x = grid_origin_x + grid_x * CELL_SIZE
            self.y = grid_origin_y + grid_y * CELL_SIZE
            self.redraw()
            self.isOnGrid = True
        else:
            self.isOnGrid = False

    def redraw(self):
        for rect in self.canvas_piece_ids:
            self.canvas.delete(rect)
        self.create_piece()
        self.bind_events()

class GeniusSquare:
    def __init__(self, root):
        self.root = root
        self.root.title("Genius Square – Version complète")

        self.canvas = tk.Canvas(root, width=700, height=400, bg="white")
        self.canvas.pack(side="left")

        self.sidebar = tk.Frame(root)
        self.sidebar.pack(side="right", padx=10, pady=10)

        self.draw_grid()
        self.blockers = []
        self.place_buttons()
        self.create_all_pieces()

    def draw_grid(self):
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                x1 = 300 + col * CELL_SIZE
                y1 = row * CELL_SIZE
                x2 = x1 + CELL_SIZE
                y2 = y1 + CELL_SIZE
                self.canvas.create_rectangle(x1, y1, x2, y2, outline="black", fill="white")

    def clear_blockers(self):
        for rect in self.blockers:
            self.canvas.delete(rect)
        self.blockers = []

    def place_blockers(self):
        for i in range(10):
          self.reset()
          self.clear_blockers()
          rolled_coords = [random.choice(die) for die in dice_values]
          
        for coord in rolled_coords:
            r, c = coord_to_grid(coord)
            x1 = 300 + c * CELL_SIZE
            y1 = r * CELL_SIZE
            x2 = x1 + CELL_SIZE
            y2 = y1 + CELL_SIZE
            blocker = self.canvas.create_rectangle(x1, y1, x2, y2, fill="black")
            self.blockers.append(blocker)

    def place_buttons(self):
        tk.Label(self.sidebar, text="Genius Square").pack(pady=10)

        btn1 = tk.Button(self.sidebar, text="Nouvelle partie", command=self.place_blockers)
        btn1.pack(pady=5)

        btn2 = tk.Button(self.sidebar, text="Réinitialiser", command=self.reset)
        btn2.pack(pady=5)

    def reset(self):
        self.canvas.delete("all")
        self.draw_grid()
        self.blockers = []
        self.create_all_pieces()

    def create_all_pieces(self):
        start_y = 10
        for i, (shape, color) in enumerate(zip(PIECE_SHAPES, PIECE_COLORS)):
            x = 20
            y = start_y + i * 40
            PuzzlePiece(self.canvas, shape, color, x, y)

if __name__ == "__main__":
    root = tk.Tk()
    app = GeniusSquare(root)
    root.mainloop()
