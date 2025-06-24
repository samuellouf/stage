import pygame
import random
import math

# Initialisation
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mini Fortnite - Zone & Dégâts")
clock = pygame.time.Clock()

# Couleurs
WHITE = (255, 255, 255)
BLUE = (50, 150, 255)
RED = (200, 0, 0)
GREEN = (0, 255, 0)
GRAY = (30, 30, 30)
YELLOW = (255, 255, 0)

# Joueur
player = pygame.Rect(400, 300, 30, 30)
player_speed = 5
bullets = []
health = 100
font = pygame.font.SysFont(None, 28)

# Ennemis
enemies = [pygame.Rect(random.randint(0, WIDTH), random.randint(0, HEIGHT), 30, 30) for _ in range(5)]

# Zone de sécurité (storm)
zone_radius = 300
zone_center = (WIDTH // 2, HEIGHT // 2)

# Tir
def shoot_bullet(start_pos, target_pos):
    dx, dy = target_pos[0] - start_pos[0], target_pos[1] - start_pos[1]
    distance = math.hypot(dx, dy)
    if distance == 0:
        return
    dx /= distance
    dy /= distance
    bullets.append({"pos": list(start_pos), "dir": (dx, dy)})

# Affichage de la vie
def draw_health_bar(current_health):
    bar_width = 200
    bar_height = 20
    x, y = 20, 20
    pygame.draw.rect(screen, RED, (x, y, bar_width, bar_height))
    pygame.draw.rect(screen, GREEN, (x, y, bar_width * current_health / 100, bar_height))
    health_text = font.render(f"Vie : {int(current_health)}%", True, WHITE)
    screen.blit(health_text, (x + 60, y - 25))

# Boucle principale
running = True
while running:
    clock.tick(60)
    screen.fill(GRAY)

    # Événements
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            shoot_bullet(player.center, pygame.mouse.get_pos())

    # Contrôles joueur
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]: player.y -= player_speed
    if keys[pygame.K_s]: player.y += player_speed
    if keys[pygame.K_a]: player.x -= player_speed
    if keys[pygame.K_d]: player.x += player_speed

    # Mouvements des balles
    for bullet in bullets[:]:
        bullet["pos"][0] += bullet["dir"][0] * 10
        bullet["pos"][1] += bullet["dir"][1] * 10
        if not (0 <= bullet["pos"][0] <= WIDTH and 0 <= bullet["pos"][1] <= HEIGHT):
            bullets.remove(bullet)

    # Ennemis poursuivent le joueur
    for enemy in enemies:
        dx = player.x - enemy.x
        dy = player.y - enemy.y
        dist = math.hypot(dx, dy)
        if dist > 0:
            enemy.x += int(dx / dist * 2)
            enemy.y += int(dy / dist * 2)

    # Collisions balle / ennemi
    for bullet in bullets[:]:
        bx, by = bullet["pos"]
        for enemy in enemies[:]:
            if enemy.collidepoint(bx, by):
                enemies.remove(enemy)
                bullets.remove(bullet)
                break

    # Réduction de la zone
    zone_radius -= 0.02
    pygame.draw.circle(screen, BLUE, zone_center, int(zone_radius), 2)

    # Vérifie si le joueur est en dehors de la zone
    dist_to_center = math.hypot(player.centerx - zone_center[0], player.centery - zone_center[1])
    if dist_to_center > zone_radius:
        pygame.draw.rect(screen, RED, player)
        health -= 0.2  # dégâts par tick
    else:
        pygame.draw.rect(screen, GREEN, player)

    # Dessin des ennemis et des balles
    for enemy in enemies:
        pygame.draw.rect(screen, YELLOW, enemy)
    for bullet in bullets:
        pygame.draw.circle(screen, WHITE, (int(bullet["pos"][0]), int(bullet["pos"][1])), 5)

    # Affiche la vie
    draw_health_bar(health)

    # Fin de partie
    if health <= 0:
        game_over_text = font.render("💀 GAME OVER 💀", True, RED)
        screen.blit(game_over_text, (WIDTH // 2 - 80, HEIGHT // 2))
        pygame.display.flip()
        pygame.time.wait(3000)
        break

    pygame.display.flip()

pygame.quit()
