import os
import pygame
import random

pygame.font.init()

# Screen Size
WIDTH, HEIGHT = 750, 750
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simon's Space Blaster Game")

# Background
BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background-black.png")), (WIDTH, HEIGHT))

# Enemy Ships
RED_SHIP = pygame.image.load(os.path.join("assets", "red_ship_small.png"))
GREEN_SHIP = pygame.image.load(os.path.join("assets", "green_ship_small.png"))
BLUE_SHIP = pygame.image.load(os.path.join("assets", "blue_ship_small.png"))

# Player Ship
YELLOW_SHIP = pygame.image.load(os.path.join("assets", "yellow_ship - Copy.png"))

# Lasers
RED_LASER = pygame.image.load(os.path.join("assets", "laser_red.png"))
GREEN_LASER = pygame.image.load(os.path.join("assets", "laser_green.png"))
BLUE_LASER = pygame.image.load(os.path.join("assets", "laser_blue.png"))
YELLOW_LASER = pygame.image.load(os.path.join("assets", "laser_yellow.png"))


class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not(height >= self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)


class Ship:
    COOLDOWN = 30

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 5
                self.lasers.remove(laser)

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x - 17, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1


class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = YELLOW_SHIP
        self.laser_img = YELLOW_LASER
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    def move_lasers(self, vel, enemies):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for enemy in enemies:
                    if laser.collision(enemy):
                        enemies.remove(enemy)
                        self.lasers.remove(laser)

    def draw(self, window):
        super().draw(window)
        self.health_bar(window)

    def health_bar(self, window):
        pygame.draw.rect(window, (255, 0, 0),
                         (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0, 255, 0),
                         (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() *
                          (self.health / self.max_health), 10))


class Enemy(Ship):
    COLOUR_MAP = {
        "red": (RED_SHIP, RED_LASER),
        "green": (GREEN_SHIP, GREEN_LASER),
        "blue": (BLUE_SHIP, BLUE_LASER)
    }

    def __init__(self, x, y, colour, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOUR_MAP[colour]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, vel):
        self.y += vel


def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) is not None


def main():
    run = True
    fps = 60
    level = 0
    lives = 5
    player_vel = 5
    enemy_vel = 1
    laser_vel = 4
    main_font = pygame.font.SysFont("None", 35)
    lost_font = pygame.font.SysFont("None", 60)
    clock = pygame.time.Clock()
    player = Player(350, 650)
    enemies = []
    wave_length = 5
    lost = False
    lost_count = 0

    def redraw_window():
        WIN.blit(BG, (0, 0))
        # Draw lives & levels test
        level_label = main_font.render(f"Level: {level}", True, (255, 255, 255))
        lives_label = main_font.render(f"Lives: {lives}", True, (255, 255, 255))
        WIN.blit(lives_label, (10, 10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))
        # Draw each enemy
        for each_enemy in enemies:
            each_enemy.draw(WIN)
        # Draw player
        player.draw(WIN)
        # Draw lost text
        if lost:
            lost_label = lost_font.render("You Lost!!", True, (255, 255, 255))
            WIN.blit(lost_label, (WIDTH / 2 - lost_label.get_width() / 2, HEIGHT / 2 - 10))
        # Update display
        pygame.display.update()

    while run:
        clock.tick(fps)
        redraw_window()
        # Check lives and health
        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1
        # If lost hold message on screen
        if lost:
            if lost_count >= fps * 3:
                run = False
            else:
                continue

        if len(enemies) == 0:
            level += 1
            wave_length += 4
            for i in range(wave_length):
                enemy = Enemy(random.randrange(90, WIDTH - 90), random.randrange(-1500, -100),
                              random.choice(["red", "green", "blue"]))
                enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        keys = pygame.key.get_pressed()
        if (keys[pygame.K_a] or keys[pygame.K_LEFT]) and player.x - player_vel > -player_vel:  # Left
            player.x -= player_vel
        if (keys[pygame.K_d] or keys[pygame.K_RIGHT]) and player.x < (WIDTH - player.get_width()):  # Right
            player.x += player_vel
        if (keys[pygame.K_w] or keys[pygame.K_UP]) and player.y - player_vel > 0:  # Up
            player.y -= player_vel
        if (keys[pygame.K_s] or keys[pygame.K_DOWN]) and player.y + player_vel < (HEIGHT - player.get_height()):  # Down
            player.y += player_vel
        if keys[pygame.K_SPACE]:
            player.shoot()

        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            # Move any lasers and check if they have hit the player
            enemy.move_lasers(laser_vel, player)

            if random.randrange(0, 4*fps) == 1:
                enemy.shoot()

            if collide(enemy, player):
                enemies.remove(enemy)
                player.health -= 5
            elif enemy.y + enemy.get_height() > HEIGHT:  # Enemy got past player lose a life
                lives -= 1
                enemies.remove(enemy)

        # Check if players laser has hit any enemies
        player.move_lasers(-laser_vel, enemies)


main()
