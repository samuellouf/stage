def load_settings(self):
    config = configparser.ConfigParser()
    config.read("settings.ini")

    self.player_name = config.get("Player", "name", fallback="Player1")
    if "Colors" in config:
        self.colors = {k: v for k, v in config["Colors"].items()}
    else:
        self.colors = {p: "gray" for p in PIECES}
        print("⚠️ Section [Colors] manquante dans settings.ini. Couleurs par défaut utilisées.")
    
    self.player_label.config(text=f"Joueur: {self.player_name}")



import tkinter as tk
from tkinter import messagebox
import time
import json
import random
import configparser
import os

GRID_SIZE = 6
PIECES = ['A', 'B', 'C', 'D', 'E', 'F']
COORDS = [f"{row}{col}" for row in "ABCDEF" for col in "123456"]

class PuzzleGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Jeu de Puzzle")

        self.canvas = tk.Canvas(root, width=600, height=600, bg='white')
        self.canvas.grid(row=0, column=1, rowspan=6)

        self.timer_label = tk.Label(root, text="Temps: 0s")
        self.timer_label.grid(row=0, column=0)

        self.roll_label = tk.Label(root, text="Tirage: ")
        self.roll_label.grid(row=1, column=0)

        self.player_label = tk.Label(root, text="Joueur: ")
        self.player_label.grid(row=2, column=0)

        self.new_game_button = tk.Button(root, text="Nouvelle partie", command=self.new_game)
        self.new_game_button.grid(row=3, column=0)

        self.undo_button = tk.Button(root, text="Undo", command=self.undo)
        self.undo_button.grid(row=4, column=0)
        self.root.bind("<Control-z>", lambda e: self.undo())

        self.solve_button = tk.Button(root, text="Abandonner (Solver)", command=self.solve)
        self.solve_button.grid(row=5, column=0)

        self.start_time = None
        self.timer_running = False
        self.timer_id = None
        self.moves = []
        self.current_roll = None
        self.placed_pieces = {}
        self.selected_piece = None

        self.ensure_settings_file()
        self.load_settings()
        self.draw_grid()
        self.draw_pieces()
        self.update_timer()

    def ensure_settings_file(self):
        if not os.path.exists("settings.ini"):
            config = configparser.ConfigParser()
            config["Player"] = {"name": "Player1"}
            config["Colors"] = {
                "A": "red",
                "B": "blue",
                "C": "green",
                "D": "yellow",
                "E": "orange",
                "F": "purple"
            }
            with open("settings.ini", "w") as f:
                config.write(f)
            print("✅ settings.ini créé avec les valeurs par défaut.")

    def load_settings(self):
        config = configparser.ConfigParser()
        config.read("settings.ini")
        self.player_name = config.get("Player", "name", fallback="Player1")

        if "Colors" in config:
            self.colors = {k.upper(): v for k, v in config["Colors"].items()}
        else:
            self.colors = {p: "gray" for p in PIECES}
            print("⚠️ Section [Colors] manquante dans settings.ini. Couleurs par défaut utilisées.")
        
        self.player_label.config(text=f"Joueur: {self.player_name}")

    def draw_grid(self):
        self.cells = {}
        cell_size = 100
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                x1, y1 = j * cell_size, i * cell_size
                x2, y2 = x1 + cell_size, y1 + cell_size
                cell_id = self.canvas.create_rectangle(x1, y1, x2, y2, outline="black", fill="white")
                coord = f"{chr(65+i)}{j+1}"
                self.cells[coord] = cell_id

    def draw_pieces(self):
        self.piece_buttons = {}
        for i, piece in enumerate(PIECES):
            color = self.colors.get(piece, "gray")
            btn = tk.Button(self.root, text=piece, bg=color, width=6, command=lambda p=piece: self.select_piece(p))
            btn.grid(row=6 + i, column=0)
            self.piece_buttons[piece] = btn

    def select_piece(self, piece):
        self.selected_piece = piece
        self.canvas.bind("<Button-1>", self.place_piece)

    def place_piece(self, event):
        if not self.selected_piece:
            return
        col = event.x // 100 + 1
        row = event.y // 100
        coord = f"{chr(65+row)}{col}"
        if coord in self.placed_pieces:
            return
        self.canvas.itemconfig(self.cells[coord], fill=self.colors.get(self.selected_piece, "gray"))
        timestamp = time.time()
        self.moves.append({"piece": self.selected_piece, "coord": coord, "timestamp": timestamp})
        self.placed_pieces[coord] = self.selected_piece
        self.check_win()

    def check_win(self):
        if len(self.placed_pieces) == len(COORDS):
            self.timer_running = False
            self.save_game()

    def undo(self):
        if not self.moves:
            return
        last = self.moves.pop()
        coord = last["coord"]
        self.canvas.itemconfig(self.cells[coord], fill="white")
        del self.placed_pieces[coord]

    def new_game(self):
        self.canvas.delete("all")
        self.draw_grid()
        self.placed_pieces.clear()
        self.moves.clear()
        self.current_roll = self.roll_dice()
        self.roll_label.config(text=f"Tirage: {self.current_roll}")
        self.start_time = time.time()
        self.timer_running = True
        self.update_timer()

    def update_timer(self):
        if self.timer_running and self.start_time:
            elapsed = int(time.time() - self.start_time)
            self.timer_label.config(text=f"Temps: {elapsed}s")
        self.timer_id = self.root.after(1000, self.update_timer)

    def roll_dice(self):
        return random.sample(COORDS, 6)

    def save_game(self):
        duration = int(time.time() - self.start_time)
        log = {
            "player": self.player_name,
            "dice_roll": self.current_roll,
            "moves": self.moves,
            "duration": duration
        }
        with open("games.log", "a") as f:
            f.write(json.dumps(log) + "\n")
        messagebox.showinfo("Partie terminée", f"Bravo {self.player_name} ! Temps: {duration}s")

    def solve(self):
        messagebox.showinfo("Solver", "Aucune solution trouvée.\n(Retirer une petite pièce ou implémenter un vrai solver)")

    def replay_game(self, game_line):
        game = json.loads(game_line)
        self.canvas.delete("all")
        self.draw_grid()
        self.start_time = time.time()
        self.timer_running = False
        for move in game["moves"]:
            coord = move["coord"]
            piece = move["piece"]
            self.canvas.itemconfig(self.cells[coord], fill=self.colors.get(piece, "gray"))
        self.timer_label.config(text=f"Durée: {game['duration']}s")


if __name__ == "__main__":
    root = tk.Tk()
    game = PuzzleGame(root)
    root.mainloop()




