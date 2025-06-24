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
            norm = tuple(sorted(((x-minx, y-miny) for x,y in pts)))
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
                coords = [(i+x, j+y) for x,y in orient]
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

        self.canvas = tk.Canvas(root, width=600, height=600, bg='white')
        self.canvas.grid(row=0, column=1, rowspan=8)

        tk.Button(root, text="Nouvelle partie", command=self.new_game).grid(row=0, column=0)
        tk.Button(root, text="Undo (Ctrl+Z)", command=self.undo).grid(row=1, column=0)
        tk.Button(root, text="Abandonner", command=self.give_up).grid(row=2, column=0)
        tk.Button(root, text="Replay", command=self.load_replay).grid(row=3, column=0)

        self.timer_label = tk.Label(root, text="Temps: 0")
        self.timer_label.grid(row=4, column=0)
        self.roll_label = tk.Label(root, text="Dés: ")
        self.roll_label.grid(row=5, column=0)
        self.player_label = tk.Label(root, text="Joueur: ")
        self.player_label.grid(row=6, column=0)

        self.root.bind("<Control-z>", lambda e: self.undo())
        self.canvas.bind("<Button-1>", self.click)

        self.selected = None
        self.moves = []
        self.placed = []
        self.start = None
        self.timer_running = False

        self._ensure_settings()
        self._load_settings()
        self._init_ui()

    def _ensure_settings(self):
        if not os.path.exists("settings.ini"):
            cfg = configparser.ConfigParser()
            cfg["Player"]={"name":"Player1"}
            cfg["Colors"] = {b: "#%06x" % random.randint(0,0xFFFFFF) for b in ALL_BLOCKS}
            with open("settings.ini","w") as f:
                cfg.write(f)

    def _load_settings(self):
        cfg = configparser.ConfigParser()
        cfg.read("settings.ini")
        self.player = cfg.get("Player","name","Player1")
        self.player_label.config(text="Joueur: "+self.player)
        self.colors = {b:cfg["Colors"].get(b,"#CCCCCC") for b in ALL_BLOCKS}

    def _init_ui(self):
        self.cell_size=100
        self.board=[[ '' for _ in range(GRID_SIZE)] for __ in range(GRID_SIZE)]
        self.draw_grid()
        self.new_game()

    def draw_grid(self):
        self.cells={}
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                x,y=i*self.cell_size,j*self.cell_size
                cid=self.canvas.create_rectangle(y,x,y+self.cell_size,x+self.cell_size,outline="black",fill="white")
                self.cells[(i,j)] = cid

    def new_game(self):
        self.canvas.delete("all")
        self.draw_grid()
        self.board=[[ '' for _ in range(GRID_SIZE)] for __ in range(GRID_SIZE)]
        self.placed.clear()
        self.moves.clear()
        self.roll = random.sample([(i,j) for i in range(GRID_SIZE) for j in range(GRID_SIZE)], 6)
        for i,j in self.roll:
            self.board[i][j]="#"
            self.canvas.itemconfig(self.cells[(i,j)],fill="black")
        self.roll_label.config(text="Dés: "+str(self.roll))
        self.start=time.time()
        self.timer_running=True
        self.update_timer()

    def update_timer(self):
        if self.timer_running:
            self.timer_label.config(text="Temps: "+str(int(time.time()-self.start)))
            self.root.after(500,self.update_timer)

    def click(self, ev):
        x,y=ev.y//self.cell_size,ev.x//self.cell_size
        if not self.selected:
            blk = self._pick_block()
            if blk:
                self.selected = blk
        else:
            if self.try_place(self.selected,(x,y)):
                self.moves.append((self.selected,(x,y),time.time()))
                self.placed.append(self.selected)
                self.selected=None
                if len(self.placed) == len(ALL_BLOCKS):
                    self.win()

    def _pick_block(self):
        choices=[b for b in ALL_BLOCKS if b not in self.placed]
        if not choices:
            return None
        blk = random.choice(choices)
        messagebox.showinfo("Selection", f"Sélection automatique: {blk}")
        return blk

    def try_place(self, blk, topleft):
        board=[row[:] for row in self.board]
        for x,y in ALL_PIECES[blk][0]:
            i,j = topleft[0]+x, topleft[1]+y
            if i<0 or i>=GRID_SIZE or j<0 or j>=GRID_SIZE or board[i][j]!="" :
                return False
            board[i][j]=blk
        self.board=board
        for x,y in ALL_PIECES[blk][0]:
            self.canvas.itemconfig(self.cells[(topleft[0]+x,topleft[1]+y)], fill=self.colors[blk])
        return True

    def win(self):
        self.timer_running=False
        dur=int(time.time()-self.start)
        msg=f"Bravo {self.player} ! Temps: {dur} secondes."
        messagebox.showinfo("Gagné!", msg)
        log = {
            "player": self.player,
            "dice": self.roll,
            "moves": [{"blk": b, "pos": p, "t": t} for b, p, t in self.moves],
            "duration": dur
        }
        with open("games.log","a") as f:
            f.write(json.dumps(log)+"\n")

    def undo(self):
        if not self.moves:
            return
        blk,pos,t = self.moves.pop()
        self.placed.remove(blk)
        self.new_game()
        for b,p,tt in self.moves:
            self.try_place(b,p)

    def give_up(self):
        board = [['' if self.board[i][j] != "#" else "#" for j in range(GRID_SIZE)] for i in range(GRID_SIZE)]
        rem = [b for b in ALL_BLOCKS if b not in self.placed]
        sol = solve(board, rem)
        if sol is None:
            messagebox.showinfo("Solver", "Pas de solution trouvée (on peut supprimer une pièce).")
            return
        for b, coords in sol.items():
            for i,j in coords:
                self.canvas.itemconfig(self.cells[(i,j)], fill=self.colors[b])
        self.timer_running = False

    def load_replay(self):
        if not os.path.exists("games.log"):
            messagebox.showerror("Replay", "Fichier games.log introuvable.")
            return
        with open("games.log") as f:
            lines = f.readlines()
        if not lines:
            messagebox.showinfo("Replay", "Aucune partie enregistrée.")
            return
        g = json.loads(lines[-1])
        self.canvas.delete("all")
        self.draw_grid()
        for i,j in g["dice"]:
            self.canvas.itemconfig(self.cells[(i,j)], fill="black")
        for mv in g["moves"]:
            blk, (x,y), t = mv["blk"], mv["pos"], mv["t"]
            for xx,yy in ALL_PIECES[blk][0]:
                self.canvas.itemconfig(self.cells[(x+xx,y+yy)], fill=self.colors[blk])
        messagebox.showinfo("Replay", f"Rejeu de {g['player']} en {g['duration']} secondes.")

if __name__ == "__main__":
    root = tk.Tk()
    GeniusSquare(root)
    root.mainloop()
