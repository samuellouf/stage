import pygame
import random
from typing import List, Tuple

# ----- Configuration générale -----
SCREEN_WIDTH, SCREEN_HEIGHT = 600, 700
GRID_SIZE = 6
CELL_SIZE = SCREEN_WIDTH // GRID_SIZE
GRID_TOP_OFFSET = 100
FPS = 60
BLOCK_COUNT = 7

# ----- Couleurs -----
WHITE = (255, 255, 255)
LIGHT_GRAY = (220, 220, 220)
DARK_GRAY = (40, 40, 40)
BLUE = (50, 150, 255)
RED = (200, 50, 50)
BLACK = (0, 0, 0)
GREEN = (0, 200, 100)

# ----- Initialisation Pygame -----
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Genius Square")
clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", 48)

# ----- Définition des pièces -----
PIECE_SHAPES = [
    [(0, 0), (0, 1), (1, 0), (1, 1)],     # carré
    [(0, 0), (1, 0), (2, 0)],             # ligne verticale
    [(0, 0), (0, 1), (0, 2)],             # ligne horizontale
    [(0, 0), (1, 0), (1, 1)],             # L inversé
    [(0, 1), (1, 1), (1, 0)],             # L classique
    [(0, 1), (1, 0), (1, 1)],             # angle coin bas
    [(0, 0), (0, 1), (1, 1)],             # angle coin haut
    [(1, 0), (1, 1), (0, 1)],             # coin inversé
    [(0, 0), (1, 0), (1, -1)],            # Z
]


class Piece:
    """Représente une pièce du puzzle."""

    def __init__(self, shape: List[Tuple[int, int]], color=BLUE):
        self.original_shape = shape[:]
        self.shape = shape[:]
        self.color = color
        self.row = random.randint(6, 9)
        self.col = random.randint(0, 5)
        self.dragging = False

    def get_cells(self) -> List[Tuple[int, int]]:
        return [(self.row + dr, self.col + dc) for dr, dc in self.shape]

    def draw(self, surface):
        for dr, dc in self.shape:
            r, c = self.row + dr, self.col + dc
            x = c * CELL_SIZE
            y = r * CELL_SIZE + GRID_TOP_OFFSET
            pygame.draw.rect(surface, self.color, (x, y, CELL_SIZE, CELL_SIZE))
            pygame.draw.rect(surface, BLACK, (x, y, CELL_SIZE, CELL_SIZE), 2)

    def move_to(self, row: int, col: int):
        self.row = row
        self.col = col

    def is_clicked(self, mouse_pos) -> bool:
        mx, my = mouse_pos
        for dr, dc in self.shape:
            r = self.row + dr
            c = self.col + dc
            x = c * CELL_SIZE
            y = r * CELL_SIZE + GRID_TOP_OFFSET
            rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
            if rect.collidepoint(mx, my):
                return True
        return False

    def rotate(self):
        """Fait tourner la pièce de 90° autour de (0,0)."""
        self.shape = [(-dc, dr) for dr, dc in self.shape]

        # Pour que la pièce soit toujours visible dans le coin supérieur gauche
        min_r = min(dr for dr, dc in self.shape)
        min_c = min(dc for dr, dc in self.shape)
        self.shape = [(dr - min_r, dc - min_c) for dr, dc in self.shape]


def generate_blocks() -> List[Tuple[int, int]]:
    """Retourne 7 positions aléatoires d'obstacles sur la grille."""
    all_cells = [(r, c) for r in range(GRID_SIZE) for c in range(GRID_SIZE)]
    return random.sample(all_cells, BLOCK_COUNT)


def draw_grid(blocks: List[Tuple[int, int]]):
    """Affiche la grille et les obstacles."""
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            x = c * CELL_SIZE
            y = r * CELL_SIZE + GRID_TOP_OFFSET
            pygame.draw.rect(screen, WHITE, (x, y, CELL_SIZE, CELL_SIZE))
            pygame.draw.rect(screen, LIGHT_GRAY, (x, y, CELL_SIZE, CELL_SIZE), 1)

            if (r, c) in blocks:
                pygame.draw.rect(screen, RED, (x + 6, y + 6, CELL_SIZE - 12, CELL_SIZE - 12))


def is_valid_position(pieces: List[Piece], blocks: List[Tuple[int, int]]) -> bool:
    """Vérifie si toutes les pièces sont bien placées."""
    occupied = set(blocks)
    for piece in pieces:
        for r, c in piece.get_cells():
            if not (0 <= r < GRID_SIZE and 0 <= c < GRID_SIZE):
                return False
            if (r, c) in occupied:
                return False
            occupied.add((r, c))
    return True


def main():
    pieces = [Piece(shape) for shape in PIECE_SHAPES]
    blocks = generate_blocks()
    selected_piece = None
    won = False

    running = True
    while running:
        screen.fill(DARK_GRAY)
        draw_grid(blocks)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                for piece in reversed(pieces):
                    if piece.is_clicked(pygame.mouse.get_pos()):
                        selected_piece = piece
                        piece.dragging = True
                        break

            elif event.type == pygame.MOUSEBUTTONUP:
                if selected_piece:
                    mx, my = pygame.mouse.get_pos()
                    row = (my - GRID_TOP_OFFSET) // CELL_SIZE
                    col = mx // CELL_SIZE
                    selected_piece.move_to(row, col)
                    selected_piece.dragging = False
                    selected_piece = None
                    won = is_valid_position(pieces, blocks)

            elif event.type == pygame.KEYDOWN:
                if selected_piece and event.key == pygame.K_r:
                    selected_piece.rotate()

        if selected_piece and selected_piece.dragging:
            mx, my = pygame.mouse.get_pos()
            row = (my - GRID_TOP_OFFSET) // CELL_SIZE
            col = mx // CELL_SIZE
            selected_piece.move_to(row, col)

        for piece in pieces:
            piece.draw(screen)

        if won:
            text = font.render("GAGNÉ !", True, GREEN)
            screen.blit(text, (SCREEN_WIDTH // 2 - 100, 30))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()



