import pygame
import random
import os

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooter")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)
GREY = (100, 100, 100)

# Clock
clock = pygame.time.Clock()

# Load assets
PLAYER_IMG = pygame.image.load("assets/player.png")
PLAYER_IMG = pygame.transform.scale(PLAYER_IMG, (50, 50))

background_img = pygame.image.load("assets/space_bg.jpg")
background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))
background_y = 0

ASTEROID_IMGS = [
    pygame.transform.scale(pygame.image.load(f"assets/asteroid{i}.png"), (60, 60)) for i in range(1, 4)
]

TREASURE_IMG = pygame.transform.scale(pygame.image.load("assets/treasure.png"), (30, 30))

# Sounds
pygame.mixer.music.load("assets/bg_music.mp3")
pygame.mixer.music.play(-1)
laser_sound = pygame.mixer.Sound("assets/laser.wav")
explosion_sound = pygame.mixer.Sound("assets/explosion.wav")

BULLET_TYPES = {
    'normal': {'color': (255, 255, 0), 'damage': 10, 'speed': 10},
    'laser': {'color': (255, 0, 0), 'damage': 25, 'speed': 15},
}

ASTEROID_SIZES = {
    'small': {'radius': 20, 'health': 20},
    'medium': {'radius': 35, 'health': 50},
    'large': {'radius': 50, 'health': 100},
}

# Achievement tracking
asteroids_destroyed = 0
treasures_collected = 0
lasers_fired = 0
achievements_unlocked = []

def check_achievements():
    if asteroids_destroyed >= 50:
        achievements_unlocked.append("Asteroid Destroyer")
    if treasures_collected >= 10:
        achievements_unlocked.append("Treasure Hunter")
    if lasers_fired >= 20:
        achievements_unlocked.append("Laser Commander")

# Game entities
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = PLAYER_IMG
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT - 60))
        self.health = 100
        self.speed = 2.5

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= 5
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += 5
        self.rect.y = HEIGHT - 80

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, bullet_type):
        super().__init__()
        self.type = bullet_type
        self.damage = BULLET_TYPES[bullet_type]['damage']
        self.image = pygame.Surface((5, 10))
        self.image.fill(BULLET_TYPES[bullet_type]['color'])
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = BULLET_TYPES[bullet_type]['speed']

    def update(self):
        self.rect.y -= self.speed
        if self.rect.bottom < 0:
            self.kill()

class Obstacle(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        size_key = random.choice(list(ASTEROID_SIZES.keys()))
        self.size = ASTEROID_SIZES[size_key]
        self.health = self.size['health']
        self.radius = self.size['radius']
        self.image = random.choice(ASTEROID_IMGS)
        self.rect = self.image.get_rect(center=(random.randint(50, WIDTH - 50), -self.radius))
        self.speed = random.uniform(1, 2)

    def update(self):
        self.rect.y += self.speed + player.speed
        if self.rect.top > HEIGHT:
            self.kill()

    def damage_obstacle(self, amount):
        self.health -= amount
        if self.health <= 0:
            explosions.add(Explosion(self.rect.center))
            explosion_sound.play()
            self.kill()

class TreasureBox(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = TREASURE_IMG
        self.rect = self.image.get_rect(center=(random.randint(50, WIDTH - 50), -30))
        self.speed = 2

    def update(self):
        self.rect.y += self.speed + player.speed
        if self.rect.top > HEIGHT:
            self.kill()

class Explosion(pygame.sprite.Sprite):
    def __init__(self, center):
        super().__init__()
        self.frames = [pygame.Surface((20, 20), pygame.SRCALPHA) for _ in range(5)]
        for frame in self.frames:
            frame.fill(random.choice([RED, (255, 165, 0), (255, 255, 0)]))
        self.index = 0
        self.image = self.frames[self.index]
        self.rect = self.image.get_rect(center=center)
        self.timer = 0

    def update(self):
        self.timer += 1
        if self.timer % 5 == 0:
            self.index += 1
            if self.index >= len(self.frames):
                self.kill()
            else:
                self.image = self.frames[self.index]

# Groups
player = Player()
player_group = pygame.sprite.Group(player)
bullets = pygame.sprite.Group()
obstacles = pygame.sprite.Group()
treasures = pygame.sprite.Group()
explosions = pygame.sprite.Group()

# Score and font
score = 0
level = 1
level_threshold = 100
font = pygame.font.SysFont('Arial', 28, bold=True)
large_font = pygame.font.SysFont('Arial', 36, bold=True)

# Limits
MAX_OBSTACLES = 10
MAX_TREASURES = 3
laser_count = 5

# Game loop
running = True
bullet_type = 'normal'
game_over = False

while running:
    clock.tick(60)

    if game_over:
        screen.fill(BLACK)
        over_text = large_font.render("Game Over", True, RED)
        screen.blit(over_text, (WIDTH // 2 - over_text.get_width() // 2, 100))

        score_text = font.render(f"Final Score: {score}", True, WHITE)
        screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 160))

        screen.blit(font.render("Achievements Unlocked:", True, CYAN), (WIDTH // 2 - 120, 210))
        if achievements_unlocked:
            for i, achievement in enumerate(achievements_unlocked):
                ach_text = font.render(f"✔ {achievement}", True, GREEN)
                screen.blit(ach_text, (WIDTH // 2 - 100, 250 + i * 30))
        else:
            none_text = font.render("None. Keep trying!", True, GREY)
            screen.blit(none_text, (WIDTH // 2 - 100, 250))

        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        continue

    # Background scroll
    background_y += player.speed
    if background_y >= HEIGHT:
        background_y = 0
    screen.blit(background_img, (0, background_y - HEIGHT))
    screen.blit(background_img, (0, background_y))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if bullet_type == 'laser' and laser_count <= 0:
                    continue
                bullet = Bullet(player.rect.centerx, player.rect.top, bullet_type)
                bullets.add(bullet)
                laser_sound.play()
                if bullet_type == 'laser':
                    laser_count -= 1
                    lasers_fired += 1
            if event.key == pygame.K_1:
                bullet_type = 'normal'
            if event.key == pygame.K_2:
                bullet_type = 'laser'

    player.update()

    if score > level * level_threshold:
        level += 1
        MAX_OBSTACLES += 3
        MAX_TREASURES += 1
        for o in obstacles:
            o.speed += 0.5
        player.speed += 0.5

    if len(obstacles) < MAX_OBSTACLES and random.random() < 0.02:
        obstacles.add(Obstacle())
    if len(treasures) < MAX_TREASURES and random.random() < 0.003:
        treasures.add(TreasureBox())

    bullets.update()
    obstacles.update()
    treasures.update()
    explosions.update()

    collisions = pygame.sprite.groupcollide(bullets, obstacles, True, False)
    for bullet, hit_list in collisions.items():
        for obstacle in hit_list:
            obstacle.damage_obstacle(bullet.damage)
            if obstacle.health <= 0:
                score += 10
                asteroids_destroyed += 1

    collected = pygame.sprite.spritecollide(player, treasures, True)
    for _ in collected:
        score += 10
        laser_count += 1
        treasures_collected += 1

    hits = pygame.sprite.spritecollide(player, obstacles, True)
    for hit in hits:
        player.health -= 20
        if player.health <= 0:
            check_achievements()
            game_over = True

    player_group.draw(screen)
    bullets.draw(screen)
    obstacles.draw(screen)
    treasures.draw(screen)
    explosions.draw(screen)

    # HUD at bottom (no background)
    score_text = font.render(f"Score: {score}", True, WHITE)
    level_text = font.render(f"Level: {level}", True, WHITE)
    health_text = font.render(f"Health: {player.health}", True, WHITE)
    laser_text = font.render(f"Laser Ammo: {laser_count}", True, WHITE)

    screen.blit(score_text, (10, HEIGHT - 80))
    screen.blit(level_text, (10, HEIGHT - 50))
    screen.blit(health_text, (WIDTH - 200, HEIGHT - 80))
    screen.blit(laser_text, (WIDTH - 200, HEIGHT - 50))

    pygame.display.flip()

pygame.quit()
