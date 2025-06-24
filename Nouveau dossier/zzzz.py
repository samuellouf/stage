import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
import time
import random
import json
import configparser
import threading
import os

CELL_SIZE = 50
GRID_SIZE = 6

# Pièces Genius Square - coordonnées relatives (ligne, colonne)
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

DEFAULT_COLORS = {
    'L': '#FF5733',  # rouge orangé
    'N': '#33FF57',  # vert clair
    'T': '#3357FF',  # bleu
    'U': '#FF33A8',  # rose
    'V': '#FF8C33',  # orange
    'W': '#8C33FF',  # violet
    'X': '#33FFF5',  # cyan
    'Y': '#F5FF33',  # jaune
    'Z': '#FF3333',  # rouge vif
}

LOG_FILE = "games.log"
SETTINGS_FILE = "settings.ini"

class GeniusSquareApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Genius Square")

        # Chargement config
        self.configs = self.load_settings()

        self.player_name = self.configs.get('Player', 'name', fallback='Player1')

        # Couleurs pièces
        self.piece_colors = {}
        for p in PIECES.keys():
            c = self.configs.get('Colors', p, fallback=DEFAULT_COLORS.get(p, "#888888"))
            self.piece_colors[p] = c

        # Variables jeu
        self.board = [['' for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.dice_positions = []
        self.placed_pieces = {}
        self.moves = []  # (piece_id, (row,col), timestamp)

        self.timer_running = False
        self.start_time = None
        self.elapsed_time = 0

        self.drag_data = {"item": None, "piece_id": None, "start_x": 0, "start_y": 0}

        self.replay_mode = False
        self.replay_moves = []
        self.replay_index = 0

        self.create_widgets()
        self.bind_all("<Control-z>", lambda e: self.undo())

    def load_settings(self):
        cfg = configparser.ConfigParser()
        if not os.path.exists(SETTINGS_FILE):
            # Création fichier default
            cfg['Player'] = {'name': 'Player1'}
            cfg['Colors'] = DEFAULT_COLORS
            with open(SETTINGS_FILE, 'w') as f:
                cfg.write(f)
        else:
            cfg.read(SETTINGS_FILE)
        return cfg

    def create_widgets(self):
        # Structure générale
        main_frame = tk.Frame(self)
        main_frame.pack(padx=10, pady=10)

        # Grille canvas
        canvas_size = GRID_SIZE * CELL_SIZE
        self.canvas = tk.Canvas(main_frame, width=canvas_size, height=canvas_size, bg='white')
        self.canvas.grid(row=0, column=1, padx=20)

        # Cases et création
        self.cells = {}
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                x1, y1 = c*CELL_SIZE, r*CELL_SIZE
                x2, y2 = x1 + CELL_SIZE, y1 + CELL_SIZE
                rect = self.canvas.create_rectangle(x1, y1, x2, y2, fill='white', outline='black')
                self.cells[(r,c)] = rect

        # Zone pièces restantes à droite
        self.pieces_frame = tk.Frame(main_frame)
        self.pieces_frame.grid(row=0, column=2, sticky='n')

        # En bas: Timer + boutons + tirage + nom joueur
        bottom_frame = tk.Frame(main_frame)
        bottom_frame.grid(row=1, column=0, columnspan=3, pady=10)

        self.timer_label = tk.Label(bottom_frame, text="Temps : 0 s", font=("Arial", 14))
        self.timer_label.pack(side='left', padx=10)

        self.dice_label = tk.Label(bottom_frame, text="Dés : -", font=("Arial", 14))
        self.dice_label.pack(side='left', padx=10)

        self.player_label = tk.Label(bottom_frame, text=f"Joueur : {self.player_name}", font=("Arial", 14))
        self.player_label.pack(side='left', padx=10)

        self.btn_new = tk.Button(bottom_frame, text="Nouvelle partie", command=self.new_game)
        self.btn_new.pack(side='left', padx=10)

        self.btn_undo = tk.Button(bottom_frame, text="Annuler (Ctrl+Z)", command=self.undo)
        self.btn_undo.pack(side='left', padx=10)

        self.btn_abandon = tk.Button(bottom_frame, text="Abandonner (solver)", command=self.abandon)
        self.btn_abandon.pack(side='left', padx=10)

        self.btn_replay = tk.Button(bottom_frame, text="Charger replay", command=self.load_replay)
        self.btn_replay.pack(side='left', padx=10)

        # Drag & drop binding canvas
        self.canvas.bind("<ButtonPress-1>", self.canvas_click)
        self.canvas.bind("<B1-Motion>", self.canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.canvas_drop)

    def new_game(self):
        if self.replay_mode:
            self.stop_replay()

        self.board = [['' for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.placed_pieces.clear()
        self.moves.clear()
        self.elapsed_time = 0

        # Tirage 6 dés (cases noires)
        all_cells = [(r,c) for r in range(GRID_SIZE) for c in range(GRID_SIZE)]
        self.dice_positions = random.sample(all_cells, 6)
        for r,c in self.dice_positions:
            self.board[r][c] = '#'

        # Reset canvas cases
        for (r,c), rect in self.cells.items():
            color = 'black' if (r,c) in self.dice_positions else 'white'
            self.canvas.itemconfig(rect, fill=color)

        # Reset zone pièces
        for w in self.pieces_frame.winfo_children():
            w.destroy()
        for pid in PIECES.keys():
            self.create_piece_widget(pid)

        # Reset timer
        self.timer_running = True
        self.start_time = time.time()
        self.update_timer()

        self.dice_label.config(text=f"Dés : {self.dice_positions}")

        self.player_label.config(text=f"Joueur : {self.player_name}")

    def create_piece_widget(self, piece_id):
        coords = PIECES[piece_id]
        w = max(c for r,c in coords) + 1
        h = max(r for r,c in coords) + 1
        width = w * CELL_SIZE
        height = h * CELL_SIZE

        canvas = tk.Canvas(self.pieces_frame, width=width, height=height, bg='lightgray', highlightthickness=1, highlightbackground="black")
        canvas.pack(pady=5)

        color = self.piece_colors.get(piece_id, "#888888")

        for (r,c) in coords:
            x1 = c * CELL_SIZE
            y1 = r * CELL_SIZE
            x2 = x1 + CELL_SIZE
            y2 = y1 + CELL_SIZE
            canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline='black')

        canvas.piece_id = piece_id
        canvas.origin = 'pieces_frame'
        canvas.bind("<ButtonPress-1>", self.start_drag)
        canvas.bind("<B1-Motion>", self.do_drag)
        canvas.bind("<ButtonRelease-1>", self.drop_piece)

    # Drag & Drop variables
    def start_drag(self, event):
        widget = event.widget
        self.drag_data["item"] = widget
        self.drag_data["piece_id"] = widget.piece_id
        self.drag_data["start_x"] = event.x
        self.drag_data["start_y"] = event.y

        # On place le widget dans la fenêtre principale pour pouvoir le déplacer librement
        widget.lift()
        widget.place(in_=self, x=widget.winfo_rootx() - self.winfo_rootx(), y=widget.winfo_rooty() - self.winfo_rooty())

    def do_drag(self, event):
        widget = self.drag_data["item"]
        if not widget:
            return
        dx = event.x - self.drag_data["start_x"]
        dy = event.y - self.drag_data["start_y"]
        x = widget.winfo_x() + dx
        y = widget.winfo_y() + dy
        widget.place(x=x, y=y)

    def drop_piece(self, event):
        widget = self.drag_data["item"]
        if not widget:
            return

        piece_id = self.drag_data["piece_id"]

        abs_x = widget.winfo_rootx() + event.x
        abs_y = widget.winfo_rooty() + event.y
        grid_x = self.canvas.winfo_rootx()
        grid_y = self.canvas.winfo_rooty()

        rel_x = abs_x - grid_x
        rel_y = abs_y - grid_y

        row = int(rel_y // CELL_SIZE)
        col = int(rel_x // CELL_SIZE)

        # Validation placement
        if self.can_place(piece_id, row, col):
            self.place_piece(piece_id, row, col)
            widget.destroy()
            self.moves.append((piece_id, (row,col), time.time()))
            if len(self.placed_pieces) == len(PIECES):
                self.win()
        else:
            # Remet à sa place (dans pieces_frame)
            widget.place_forget()
            widget.pack(pady=5)

        self.drag_data = {"item": None, "piece_id": None, "start_x": 0, "start_y": 0}

    # Pour drag & drop depuis la grille (ex: déplacer pièce posée)
    def canvas_click(self, event):
        if self.replay_mode: return
        r = event.y // CELL_SIZE
        c = event.x // CELL_SIZE
        if r >= GRID_SIZE or c >= GRID_SIZE: return
        piece_id = self.board[r][c]
        if piece_id in self.placed_pieces:
            self.drag_data["item"] = "canvas_piece"
            self.drag_data["piece_id"] = piece_id
            self.drag_data["start_x"] = event.x
            self.drag_data["start_y"] = event.y

    def canvas_drag(self, event):
        if self.drag_data["item"] != "canvas_piece":
            return
        # On déplace visuellement la pièce sur le canvas (simulation)
        self.canvas.delete("drag_preview")
        piece_id = self.drag_data["piece_id"]
        coords = PIECES[piece_id]
        color = self.piece_colors[piece_id]

        # Nouvelle position calculée
        new_row = event.y // CELL_SIZE
        new_col = event.x // CELL_SIZE

        # Dessine preview pièce à la nouvelle position
        for (rr, cc) in coords:
            r = new_row + rr
            c = new_col + cc
            if 0 <= r < GRID_SIZE and 0 <= c < GRID_SIZE:
                x1 = c * CELL_SIZE
                y1 = r * CELL_SIZE
                x2 = x1 + CELL_SIZE
                y2 = y1 + CELL_SIZE
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, stipple='gray50', tags="drag_preview")

    def canvas_drop(self, event):
        if self.drag_data["item"] != "canvas_piece":
            return
        self.canvas.delete("drag_preview")
        piece_id = self.drag_data["piece_id"]

        new_row = event.y // CELL_SIZE
        new_col = event.x // CELL_SIZE

        # Retire la pièce de sa position précédente
        if piece_id in self.placed_pieces:
            for (r,c) in self.placed_pieces[piece_id]:
                self.board[r][c] = ''
                self.canvas.itemconfig(self.cells[(r,c)], fill='white')

        # Essaye de replacer à la nouvelle position
        if self.can_place(piece_id, new_row, new_col):
            self.place_piece(piece_id, new_row, new_col)
            self.moves.append((piece_id, (new_row,new_col), time.time()))
        else:
            # Si non valide, remet pièce à l'ancienne position
            old_pos = self.moves[-1][1] if self.moves else None
            if old_pos:
                self.place_piece(piece_id, old_pos[0], old_pos[1])
            else:
                # Jamais placé avant ? remet dans pièces à gauche
                self.create_piece_widget(piece_id)

        self.drag_data = {"item": None, "piece_id": None, "start_x": 0, "start_y": 0}

    def can_place(self, piece_id, row, col):
        coords = PIECES[piece_id]
        for (r,c) in coords:
            rr = row + r
            cc = col + c
            if rr < 0 or rr >= GRID_SIZE or cc < 0 or cc >= GRID_SIZE:
                return False
            if self.board[rr][cc] != '':
                # sauf la case noire (dés) on ne peut pas mettre pièce
                return False
        return True

    def place_piece(self, piece_id, row, col):
        coords = PIECES[piece_id]
        color = self.piece_colors[piece_id]
        self.placed_pieces[piece_id] = []
        for (r,c) in coords:
            rr = row + r
            cc = col + c
            self.board[rr][cc] = piece_id
            self.canvas.itemconfig(self.cells[(rr,cc)], fill=color)
            self.placed_pieces[piece_id].append((rr,cc))

    def undo(self):
        if not self.moves:
            return
        if self.replay_mode:
            messagebox.showinfo("Replay","Pas d'annulation en mode replay")
            return
        piece_id, (row,col), _ = self.moves.pop()
        if piece_id in self.placed_pieces:
            for (r,c) in self.placed_pieces[piece_id]:
                self.board[r][c] = ''
                self.canvas.itemconfig(self.cells[(r,c)], fill='white')
            del self.placed_pieces[piece_id]
            self.create_piece_widget(piece_id)

    def update_timer(self):
        if self.timer_running:
            self.elapsed_time = int(time.time() - self.start_time)
            self.timer_label.config(text=f"Temps : {self.elapsed_time} s")
            self.after(500, self.update_timer)

    def win(self):
        self.timer_running = False
        messagebox.showinfo("Gagné !", f"Bravo {self.player_name}, vous avez gagné en {self.elapsed_time} secondes.")
        self.save_game()

    def save_game(self):
        # Sauvegarde dans games.log JSON ligne unique
        game_data = {
            "player": self.player_name,
            "dice": self.dice_positions,
            "moves": [{"piece": m[0], "pos": m[1], "timestamp": m[2]} for m in self.moves],
            "duration": self.elapsed_time
        }
        with open(LOG_FILE, "a") as f:
            f.write(json.dumps(game_data) + "\n")

    def load_replay(self):
        # Ouvre un fichier games.log, choix d'une ligne (partie) et replay
        path = filedialog.askopenfilename(title="Sélectionner fichier replay", filetypes=[("Log files","*.log"),("All files","*.*")])
        if not path:
            return
        with open(path, "r") as f:
            lines = f.readlines()
        if not lines:
            messagebox.showerror("Erreur","Fichier vide")
            return
        # Choix ligne par index
        idx = simpledialog.askinteger("Replay", f"Choisir partie 1-{len(lines)}", minvalue=1, maxvalue=len(lines))
        if not idx:
            return
        line = lines[idx-1]
        try:
            data = json.loads(line)
        except Exception as e:
            messagebox.showerror("Erreur", f"Format JSON invalide: {e}")
            return
        self.start_replay(data)

    def start_replay(self, data):
        self.replay_mode = True
        self.timer_running = False
        self.board = [['' for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.placed_pieces.clear()
        self.moves.clear()
        self.elapsed_time = data.get("duration", 0)

        # Placer dés
        self.dice_positions = data.get("dice", [])
        for r,c in self.dice_positions:
            self.board[r][c] = '#'

        for (r,c), rect in self.cells.items():
            color = 'black' if (r,c) in self.dice_positions else 'white'
            self.canvas.itemconfig(rect, fill=color)

        for w in self.pieces_frame.winfo_children():
            w.destroy()

        self.dice_label.config(text=f"Dés : {self.dice_positions}")
        self.player_label.config(text=f"Joueur : {data.get('player','?')}")
        self.timer_label.config(text=f"Temps : {self.elapsed_time} s")

        self.replay_moves = data.get("moves", [])
        self.replay_index = 0
        self.after(1000, self.replay_step)

    def replay_step(self):
        if self.replay_index >= len(self.replay_moves):
            messagebox.showinfo("Replay fini", "Fin du replay")
            self.replay_mode = False
            return
        move = self.replay_moves[self.replay_index]
        pid = move["piece"]
        r,c = move["pos"]
        self.place_piece(pid, r, c)
        self.replay_index += 1
        self.after(1000, self.replay_step)

    def stop_replay(self):
        self.replay_mode = False

    def abandon(self):
        # Appelle le solver pour solution depuis état actuel
        # Ici stub simple : on demande confirmation et affiche message
        if self.replay_mode:
            messagebox.showinfo("Replay","Pas d'abandon possible en mode replay")
            return
        res = messagebox.askyesno("Abandonner", "Voulez-vous que le solver cherche une solution à partir de cet état ?")
        if not res:
            return

        # On simule le solver
        solution_found = self.call_solver()

        if solution_found:
            messagebox.showinfo("Solution trouvée", "Le solver a trouvé une solution valide ! (stub)")
            # En vrai, on afficherait solution
        else:
            messagebox.showinfo("Pas de solution", "Aucune solution trouvée, on retire la plus petite pièce et on réessaie (stub).")

    def call_solver(self):
        # Stub: ici tu peux intégrer ton solver réel.
        # Pour l'instant on renvoie True ou False aléatoirement.
        return random.choice([True, False])


if __name__ == "__main__":
    app = GeniusSquareApp()
    app.mainloop()
