###############################################################################################
#                                                                                             #
#                          PAT VS HR                                                          #
#                                                                                             #
#   PLAY AS PATRICK AS HE FENDS OFF BAD RESUMES PROVIDED BY HR                                #
#                                                                                             #
#   THINK YOU HAVE WHAT IT TAKES TO DEFEAT THE HR DEPARTMENT??                                #
#                                                                                             #
#                                                                                             #
#   A GAME BY MATT GREEN                                                                      #
#       25/05/2024                                                                            #
###############################################################################################

import os
import sys
import pygame
import random

sys.stdout = open(os.devnull, 'w')
sys.stderr = open(os.devnull, 'w')

pygame.init()

sys.stdout = sys.__stdout__
sys.stderr = sys.__stderr__

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PLAYER_SPEED = 5
OBJECT_SPEED = 5
PROJECTILE_SPEED = 10
INITIAL_SPAWN_RATE = 50
FONT_COLOR = (255, 255, 255)
BORDER_COLOR = (0, 0, 0)
BORDER_THICKNESS = 2
SHOOTING_DURATION = 10

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

background_img = pygame.image.load(os.path.join(BASE_DIR, 'background.png'))
player_img = pygame.image.load(os.path.join(BASE_DIR, 'player1.png'))
player_shooting_img = pygame.image.load(os.path.join(BASE_DIR, 'player2.png'))
object_img = pygame.image.load(os.path.join(BASE_DIR, 'object.png'))
explosion_img = pygame.image.load(os.path.join(BASE_DIR, 'explosion.png'))
projectile_img = pygame.image.load(os.path.join(BASE_DIR, 'projectile.png'))
start_img = pygame.image.load(os.path.join(BASE_DIR, 'start.png'))
gameover_img = pygame.image.load(os.path.join(BASE_DIR, 'gameover.png'))
newgame_img = pygame.image.load(os.path.join(BASE_DIR, 'newgame.png'))

shoot_sound = pygame.mixer.Sound(os.path.join(BASE_DIR, 'shoot.mp3'))

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pat Vs HR")

clock = pygame.time.Clock()

font = pygame.font.SysFont(None, 36)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_img
        self.rect = self.image.get_rect()
        self.rect.x = 50
        self.rect.y = SCREEN_HEIGHT // 2
        self.shooting = False
        self.lives = 3
        self.shooting_timer = 0

    def move(self, keys):
        if keys[pygame.K_UP] and self.rect.top > 0:
            self.rect.y -= PLAYER_SPEED
        if keys[pygame.K_DOWN] and self.rect.bottom < SCREEN_HEIGHT:
            self.rect.y += PLAYER_SPEED

    def shoot(self):
        projectile = Projectile(self.rect.right, self.rect.centery)
        all_sprites.add(projectile)
        projectiles.add(projectile)
        self.shooting = True
        self.shooting_timer = SHOOTING_DURATION
        self.image = player_shooting_img
        shoot_sound.play()

    def update(self):
        if self.shooting:
            self.shooting_timer -= 1
            if self.shooting_timer <= 0:
                self.shooting = False
                self.image = player_img

class Object(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = object_img
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH
        self.rect.y = random.randint(0, SCREEN_HEIGHT - self.rect.height)

    def update(self):
        self.rect.x -= OBJECT_SPEED
        if self.rect.right < 0:
            self.kill()

class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = projectile_img
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y

    def update(self):
        self.rect.x += PROJECTILE_SPEED
        if self.rect.left > SCREEN_WIDTH:
            self.kill()

all_sprites = pygame.sprite.Group()
objects = pygame.sprite.Group()
projectiles = pygame.sprite.Group()

player = Player()
all_sprites.add(player)

def render_text_with_border(text, font, text_color, border_color, border_thickness):
    text_surface = font.render(text, True, text_color)
    width, height = text_surface.get_size()
    border_surfaces = []
    
    for dx in range(-border_thickness, border_thickness + 1):
        for dy in range(-border_thickness, border_thickness + 1):
            if dx != 0 or dy != 0:
                border_surface = font.render(text, True, border_color)
                border_surfaces.append((border_surface, (dx, dy)))

    return text_surface, border_surfaces

def display_image(image, x, y):
    rect = image.get_rect(center=(x, y))
    screen.blit(image, rect)

def game_loop():
    global running, score, spawn_rate, frame_count

    running = True
    score = 0
    spawn_rate = INITIAL_SPAWN_RATE
    frame_count = 0
    player.lives = 3
    player.rect.y = SCREEN_HEIGHT // 2
    all_sprites.add(player)

    while running:
        clock.tick(60)
        frame_count += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                player.shoot()

        keys = pygame.key.get_pressed()
        player.move(keys)

        # Spawning objects
        if frame_count % spawn_rate == 0:
            obj = Object()
            all_sprites.add(obj)
            objects.add(obj)
            if spawn_rate > 10:
                spawn_rate -= 1

        all_sprites.update()

        # Check for collisions
        hits = pygame.sprite.groupcollide(objects, projectiles, True, True)
        if hits:
            score += len(hits)

        player_hits = pygame.sprite.spritecollide(player, objects, True)
        if player_hits:
            player.lives -= 1
            if player.lives <= 0:
                running = False

        screen.blit(background_img, (0, 0))
        all_sprites.draw(screen)
        
        # Score
        score_text, score_borders = render_text_with_border(f'Score: {score}', font, FONT_COLOR, BORDER_COLOR, BORDER_THICKNESS)
        for border_surface, offset in score_borders:
            screen.blit(border_surface, (10 + offset[0], 10 + offset[1]))
        screen.blit(score_text, (10, 10))
        
        # Lives
        lives_text, lives_borders = render_text_with_border(f'Lives: {player.lives}', font, FONT_COLOR, BORDER_COLOR, BORDER_THICKNESS)
        for border_surface, offset in lives_borders:
            screen.blit(border_surface, (10 + offset[0], 40 + offset[1]))
        screen.blit(lives_text, (10, 40))

        pygame.display.flip()

def main_menu():
    start_button_rect = start_img.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                waiting = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if start_button_rect.collidepoint(event.pos):
                    waiting = False
        
        screen.blit(background_img, (0, 0))
        display_image(start_img, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        pygame.display.flip()
        clock.tick(60)

def game_over():
    gameover_button_rect = newgame_img.get_rect(midbottom=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if gameover_button_rect.collidepoint(event.pos):
                    waiting = False
        
        screen.blit(background_img, (0, 0))
        display_image(gameover_img, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        display_image(newgame_img, SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50)
        pygame.display.flip()
        clock.tick(60)

# Main game flow
while True:
    main_menu()
    game_loop()
    game_over()