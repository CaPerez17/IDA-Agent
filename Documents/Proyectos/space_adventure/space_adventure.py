import pygame
import random
import math

pygame.init()

# Configuración
WIDTH, HEIGHT = 800, 600
FPS = 60
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Adventure")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

# Colores
BLACK = (0, 0, 30)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 100, 100)
YELLOW = (255, 255, 0)

class Player:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT - 100
        self.size = 30
        self.speed = 5
        self.rect = pygame.Rect(self.x, self.y, self.size, self.size)
    
    def update(self, keys):
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x = max(0, self.x - self.speed)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x = min(WIDTH - self.size, self.x + self.speed)
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.y = max(0, self.y - self.speed)
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.y = min(HEIGHT - self.size, self.y + self.speed)
        self.rect.x, self.rect.y = self.x, self.y
    
    def draw(self):
        pygame.draw.rect(screen, GREEN, self.rect)
        pygame.draw.circle(screen, YELLOW, self.rect.center, 8)

class Enemy:
    def __init__(self):
        side = random.choice(['top', 'bottom', 'left', 'right'])
        if side == 'top': self.x, self.y = random.randint(0, WIDTH), -30
        elif side == 'bottom': self.x, self.y = random.randint(0, WIDTH), HEIGHT + 30
        elif side == 'left': self.x, self.y = -30, random.randint(0, HEIGHT)
        else: self.x, self.y = WIDTH + 30, random.randint(0, HEIGHT)
        self.size = 25
        self.speed = 2
        self.rect = pygame.Rect(self.x, self.y, self.size, self.size)
    
    def update(self, player_x, player_y):
        dx = player_x - self.x
        dy = player_y - self.y
        dist = math.sqrt(dx*dx + dy*dy)
        if dist > 0:
            self.x += (dx / dist) * self.speed
            self.y += (dy / dist) * self.speed
        self.rect.x, self.rect.y = self.x, self.y
    
    def draw(self):
        pygame.draw.rect(screen, RED, self.rect)
    
    def off_screen(self):
        return self.x < -50 or self.x > WIDTH + 50 or self.y < -50 or self.y > HEIGHT + 50

class Bullet:
    def __init__(self, x, y, target_x, target_y):
        self.x, self.y = x, y
        dx = target_x - x
        dy = target_y - y
        dist = math.sqrt(dx*dx + dy*dy)
        self.vx = (dx / dist) * 8 if dist > 0 else 0
        self.vy = (dy / dist) * 8 if dist > 0 else 0
        self.radius = 5
        self.rect = pygame.Rect(x - self.radius, y - self.radius, self.radius*2, self.radius*2)
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.rect.x, self.rect.y = self.x - self.radius, self.y - self.radius
    
    def draw(self):
        pygame.draw.circle(screen, YELLOW, (int(self.x), int(self.y)), self.radius)
    
    def off_screen(self):
        return self.x < 0 or self.x > WIDTH or self.y < 0 or self.y > HEIGHT

def main():
    player = Player()
    enemies = []
    bullets = []
    score = 0
    last_enemy = 0
    last_shot = 0
    running = True
    game_over = False
    
    while running:
        clock.tick(FPS)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if game_over:
                    player = Player()
                    enemies = []
                    bullets = []
                    score = 0
                    game_over = False
        
        if not game_over:
            keys = pygame.key.get_pressed()
            player.update(keys)
            
            # Disparar
            now = pygame.time.get_ticks()
            mouse_pressed = pygame.mouse.get_pressed()
            if mouse_pressed[0] and now - last_shot > 200:
                mx, my = pygame.mouse.get_pos()
                bullets.append(Bullet(player.rect.centerx, player.rect.centery, mx, my))
                last_shot = now
            
            # Crear enemigos
            if now - last_enemy > 1500:
                enemies.append(Enemy())
                last_enemy = now
            
            # Actualizar enemigos
            for enemy in enemies[:]:
                enemy.update(player.rect.centerx, player.rect.centery)
                if enemy.rect.colliderect(player.rect):
                    game_over = True
                for bullet in bullets[:]:
                    if enemy.rect.colliderect(bullet.rect):
                        enemies.remove(enemy)
                        bullets.remove(bullet)
                        score += 10
                        break
                if enemy.off_screen():
                    enemies.remove(enemy)
            
            # Actualizar balas
            for bullet in bullets[:]:
                bullet.update()
                if bullet.off_screen():
                    bullets.remove(bullet)
        
        # Dibujar
        screen.fill(BLACK)
        if not game_over:
            player.draw()
            for enemy in enemies:
                enemy.draw()
            for bullet in bullets:
                bullet.draw()
            screen.blit(font.render(f"Score: {score}", True, WHITE), (10, 10))
        else:
            screen.blit(font.render("GAME OVER", True, RED), (WIDTH//2 - 100, HEIGHT//2))
            screen.blit(font.render(f"Score: {score}", True, WHITE), (WIDTH//2 - 80, HEIGHT//2 + 40))
            screen.blit(font.render("Press SPACE to restart", True, WHITE), (WIDTH//2 - 150, HEIGHT//2 + 80))
        
        pygame.display.flip()
    
    pygame.quit()

if __name__ == "__main__":
    main()
