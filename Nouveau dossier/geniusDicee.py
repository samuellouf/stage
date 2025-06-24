import tkinter as tk
import json
import time
import random
import os
import configparser
from tkinter import messagebox

GRID_SIZE = 6

# --- Solver intégré ---

PIECES = {
    'L': [(0,0),(1,0),(2,0),(2,1)],
    'N': [(0,1),(1,1),(1,0),(2,0)],
    'T': [(0,0),(0,1),(0,2),(1,1)],
    'U': [(0,0),(0,2),(1,0),(1,1),(1,2)],
    'V': [(0,0),(1,0),(2,0),(2,1)],
    'W': [(0,0),(1,0),(1,1),(2,1)],
    'X': [(0,1),(1,0),(1,1),(1,2),(2,1)],
    'Y': [(0,1),(1,1),(2,1),(3,1),(3,0)],
    'Z': [(0,0),(0,1),(1,1),(1,2)]
}

def all_orientations(shape):
    shapes = set()
    coords = shape
    for flip in (False, True):
        for rot in range(4):
            pts = coords
            if flip:
                pts = [(-x,y) for x,y in pts]
            for _ in range(rot):
                pts = [(y, -x) for x,y in pts]
            minx = min(x for x,y in pts)
            miny = min(y for x,y in pts)
            norm = tuple(sorted(((x - minx, y - miny) for x,y in pts)))
            shapes.add(norm)
    return shapes

ALL_PIECES = {k: list(all_orientations(v)) for k,v in PIECES.items()}

def solve(board, remaining, placement=None):
    if placement is None:
        placement = {}
    if not remaining:
        return placement
    piece = remaining[0]
    for orient in ALL_PIECES[piece]:
        max_x = max(x for x,y in orient)
        max_y = max(y for x,y in orient)
        for i in range(GRID_SIZE - max_x):
            for j in range(GRID_SIZE - max_y):
                coords = [(i + x, j + y) for x,y in orient]
                if all(board[x][y] == '' for x,y in coords):
                    for x,y in coords:
                        board[x][y] = piece
                    placement[piece] = coords
                    sol = solve(board, remaining[1:], placement)
                    if sol is not None:
                        return sol
                    for x,y in coords:
                        board[x][y] = ''
                    del placement[piece]
    return None

# --- Jeu principal ---

ALL_BLOCKS = list(PIECES.keys())

class GeniusSquare:
    def __init__(self, root):
        self.root = root
        self.root.title("Genius Square")

        # Interface
        self.canvas = tk.Canvas(root, width=600, height=600, bg='white')
        self.canvas.grid(row=0, column=1, rowspan=8, padx=10, pady=10)

        tk.Button(root, text="Nouvelle partie", command=self.new_game).grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        tk.Button(root, text="Undo (Ctrl+Z)", command=self.undo).grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        tk.Button(root, text="Abandonner", command=self.give_up).grid(row=2, column=0, sticky="ew", padx=5, pady=5)
        tk.Button(root, text="Replay", command=self.load_replay).grid(row=3, column=0, sticky="ew", padx=5, pady=5)

        self.timer_label = tk.Label(root, text="Temps: 0")
        self.timer_label.grid(row=4, column=0, sticky="w", padx=5, pady=5)
        self.roll_label = tk.Label(root, text="Dés: ")
        self.roll_label.grid(row=5, column=0, sticky="w", padx=5, pady=5)
        self.player_label = tk.Label(root, text="Joueur: ")
        self.player_label.grid(row=6, column=0, sticky="w", padx=5, pady=5)

        # Bindings
        self.root.bind("<Control-z>", lambda e: self.undo())
        self.canvas.bind("<Button-1>", self.click)

        self.selected_piece = None
        self.moves = []
        self.placed = []
        self.start_time = None
        self.timer_running = False

        # Chargement des paramètres
        self._ensure_settings()
        self._load_settings()

        self.cell_size = 100
        self.board = [['' for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

        self.draw_grid()
        self.new_game()

    def _ensure_settings(self):
        if not os.path.exists("settings.ini"):
            cfg = configparser.ConfigParser()
            cfg["Player"] = {"name": "Player1"}
            cfg["Colors"] = {b: "#%06x" % random.randint(0, 0xFFFFFF) for b in ALL_BLOCKS}
            with open("settings.ini", "w") as f:
                cfg.write(f)

    def _load_settings(self):
        cfg = configparser.ConfigParser()
        cfg.read("settings.ini")

        # Lecture nom joueur
        if cfg.has_section("Player") and cfg.has_option("Player", "name"):
            self.player = cfg.get("Player", "name")
        else:
            self.player = "Player1"
        self.player_label.config(text="Joueur: " + self.player)

        # Lecture couleurs pièces
        if cfg.has_section("Colors"):
            self.colors = {b: cfg["Colors"].get(b, "#CCCCCC") for b in ALL_BLOCKS}
        else:
            self.colors = {b: "#CCCCCC" for b in ALL_BLOCKS}

    def draw_grid(self):
        self.cells = {}
        self.canvas.delete("all")
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                x1 = j * self.cell_size
                y1 = i * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                cid = self.canvas.create_rectangle(x1, y1, x2, y2, outline="black", fill="white")
                self.cells[(i,j)] = cid

    def new_game(self):
        self.draw_grid()
        self.board = [['' for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.placed.clear()
        self.moves.clear()

        # Tirage aléatoire des 6 dés (cases noires)
        self.roll = random.sample([(i,j) for i in range(GRID_SIZE) for j in range(GRID_SIZE)], 6)
        for i,j in self.roll:
            self.board[i][j] = "#"
            self.canvas.itemconfig(self.cells[(i,j)], fill="black")

        self.roll_label.config(text="Dés: " + str(self.roll))
        self.start_time = time.time()
        self.timer_running = True
        self.update_timer()

    def update_timer(self):
        if self.timer_running:
            elapsed = int(time.time() - self.start_time)
            self.timer_label.config(text="Temps: " + str(elapsed))
            self.root.after(500, self.update_timer)

    def click(self, event):
        row = event.y // self.cell_size
        col = event.x // self.cell_size

        if row >= GRID_SIZE or col >= GRID_SIZE:
            return

        if self.selected_piece is None:
            piece = self._pick_piece()
            if piece:
                self.selected_piece = piece
                messagebox.showinfo("Pièce sélectionnée", f"Pièce sélectionnée : {piece}")
        else:
            if self.try_place(self.selected_piece, (row, col)):
                self.moves.append((self.selected_piece, (row, col), time.time()))
                self.placed.append(self.selected_piece)
                self.selected_piece = None
                if len(self.placed) == len(ALL_BLOCKS):
                    self.win()

    def _pick_piece(self):
        available = [b for b in ALL_BLOCKS if b not in self.placed]
        if not available:
            return None
        # Ici, sélection aléatoire, tu peux modifier pour choix manuel
        return random.choice(available)

    def try_place(self, piece, topleft):
        # Teste si la pièce peut être placée
        for orient in ALL_PIECES[piece]:
            max_x = max(x for x, y in orient)
            max_y = max(y for x, y in orient)
            # On ne teste que la première orientation (simplification)
            if max_x + topleft[0] >= GRID_SIZE or max_y + topleft[1] >= GRID_SIZE:
                return False
            for x,y in orient:
                i,j = topleft[0] + x, topleft[1] + y
                if i < 0 or j < 0 or i >= GRID_SIZE or j >= GRID_SIZE:
                    return False
                if self.board[i][j] != '':
                    return False
            # Placement valide
            for x,y in orient:
                i,j = topleft[0] + x, topleft[1] + y
                self.board[i][j] = piece
                self.canvas.itemconfig(self.cells[(i,j)], fill=self.colors[piece])
            return True
        return False

    def win(self):
        self.timer_running = False
        duration = int(time.time() - self.start_time)
        messagebox.showinfo("Victoire", f"Bravo {self.player} ! Temps : {duration} secondes.")
        log_entry = {
            "player": self.player,
            "dice": self.roll,
            "moves": [{"piece": b, "position": p, "timestamp": t} for b, p, t in self.moves],
            "duration": duration
        }
        with open("games.log", "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")

    def undo(self):
        if not self.moves:
            return
        last_move = self.moves.pop()
        piece, pos, _ = last_move
        if piece in self.placed:
            self.placed.remove(piece)
        self.new_game()
        # Rejoue tous les coups sauf le dernier
        for b, p, _ in self.moves:
            self.try_place(b, p)

    def give_up(self):
        board = [['' if self.board[i][j] != "#" else "#" for j in range(GRID_SIZE)] for i in range(GRID_SIZE)]
        remaining = [b for b in ALL_BLOCKS if b not in self.placed]
        sol = solve(board, remaining)
        if sol is None:
            messagebox.showinfo("Solver", "Pas de solution trouvée. Vous pouvez retirer une pièce et réessayer.")
            return
        for piece, coords in sol.items():
            for i, j in coords:
                self.canvas.itemconfig(self.cells[(i, j)], fill=self.colors[piece])
        self.timer_running = False

    def load_replay(self):
        if not os.path.exists("games.log"):
            messagebox.showerror("Replay", "Fichier games.log introuvable.")
            return
        with open("games.log", encoding="utf-8") as f:
            lines = f.readlines()
        if not lines:
            messagebox.showinfo("Replay", "Aucune partie enregistrée.")
            return
        replay = json.loads(lines[-1])
        self.draw_grid()
        for i,j in replay["dice"]:
            self.canvas.itemconfig(self.cells[(i,j)], fill="black")
        for move in replay["moves"]:
            piece = move["piece"]
            x,y = move["position"]
            for xx, yy in ALL_PIECES[piece][0]:
                self.canvas.itemconfig(self.cells[(x+xx, y+yy)], fill=self.colors.get(piece, "#CCCCCC"))
        messagebox.showinfo("Replay", f"Rejeu de {replay['player']} en {replay['duration']} secondes.")

if __name__ == "__main__":
    root = tk.Tk()
    GeniusSquare(root)
    root.mainloop()
