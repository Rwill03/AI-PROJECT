import pygame
from pygame.locals import *
from sklearn.linear_model import LinearRegression
import numpy as np

pygame.init()

screen_width = 600
screen_height = 500

fpsClock = pygame.time.Clock()
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Pong')

# Define font
font = pygame.font.SysFont('Constantia', 30)

# Define game variables
margin = 50
cpu_score = 0
player_score = 0
fps = 60
live_ball = False
winner = 0
speed_increase = 0

# Define colors
bg = (0, 0, 0)
white = (255, 255, 255)


def draw_board():
    screen.fill(bg)
    pygame.draw.line(screen, white, (0, margin), (screen_width, margin), 2)


def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


class Paddle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.rect = Rect(x, y, 20, 100)
        self.speed = 5
        self.ai_speed = 5

    def move(self):
        key = pygame.key.get_pressed()
        if key[pygame.K_UP] and self.rect.top > margin:
            self.rect.move_ip(0, -1 * self.speed)
        if key[pygame.K_DOWN] and self.rect.bottom < screen_height:
            self.rect.move_ip(0, self.speed)

    def draw(self):
        pygame.draw.rect(screen, white, self.rect)

    def ai(self):
        # AI to move the paddle automatically
        # Move down
        if self.rect.centery < pong.rect.centery and self.rect.bottom < screen_height:
            self.rect.move_ip(0, self.ai_speed)
        # Move up
        if self.rect.centery > pong.rect.centery and self.rect.top > margin:
            self.rect.move_ip(0, -1 * self.ai_speed)


class Ball:
    def __init__(self, x, y):
        self.reset(x, y)

    def move(self):
        # Check collision with top margin
        if self.rect.top < margin:
            self.speed_y *= -1
        # Check collision with bottom of the screen
        if self.rect.bottom > screen_height:
            self.speed_y *= -1
        if self.rect.colliderect(player_paddle) or self.rect.colliderect(cpu_paddle):
            self.speed_x *= -1

        # Check for out of bounds
        if self.rect.left < 0:
            self.winner = 1
        if self.rect.left > screen_width:
            self.winner = -1

        # Update ball position
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        return self.winner

    def draw(self):
        pygame.draw.circle(screen, white, (self.rect.x + self.ball_rad, self.rect.y + self.ball_rad), self.ball_rad)

    def reset(self, x, y):
        self.x = x
        self.y = y
        self.ball_rad = 8
        self.rect = Rect(x, y, self.ball_rad * 2, self.ball_rad * 2)
        self.speed_x = -4
        self.speed_y = 4
        self.winner = 0  # 1 is the player and -1 is the CPU


# Create paddles
player_paddle = Paddle(screen_width - 40, screen_height // 2)
cpu_paddle = Paddle(20, screen_height // 2)

# Create pong ball
pong = Ball(screen_width - 60, screen_height // 2 + 50)

# Create linear regression model
cpu_model = LinearRegression()

# Game loop
run = True
while run:
    fpsClock.tick(fps)

    draw_board()
    draw_text('CPU: ' + str(cpu_score), font, white, 20, 15)
    draw_text('P1: ' + str(player_score), font, white, screen_width - 100, 15)
    draw_text('BALL SPEED: ' + str(abs(pong.speed_x)), font, white, screen_width // 2 - 100, 15)

    player_paddle.draw()
    cpu_paddle.draw()

    if live_ball:
        speed_increase += 1
        winner = pong.move()
        if winner == 0:
            pong.draw()
            player_paddle.move()

            # Change the CPU paddle movement to the prediction of the model
            X_train = np.array([[pong.rect.centerx]])
            y_train = np.array([cpu_paddle.rect.centery])

            # Train the model with the current data
            cpu_model.fit(X_train, y_train)

            # Predict the new position of the CPU paddle
            predicted_position = cpu_model.predict(np.array([[pong.rect.centerx]]))
            cpu_paddle.rect.centery = int(predicted_position[0])

            cpu_paddle.ai()  # Include this line to update AI movement

        else:
            live_ball = False
            if winner == 1:
                player_score += 1
            elif winner == -1:
                cpu_score += 1

    if not live_ball:
        if winner == 0:
            draw_text('CLICK ANYWHERE TO START', font, white, 100, screen_height // 2 - 100)
        if winner == 1:
            draw_text('YOU SCORED!', font, white, 220, screen_height // 2 - 100)
            draw_text('CLICK ANYWHERE TO START', font, white, 100, screen_height // 2 - 50)
        if winner == -1:
            draw_text('CPU SCORED!', font, white, 220, screen_height // 2 - 100)
            draw_text('CLICK ANYWHERE TO START', font, white, 100, screen_height // 2 - 50)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN and not live_ball:
            live_ball = True
            pong.reset(screen_width - 60, screen_height // 2 + 50)

    if speed_increase > 500:
        speed_increase = 0
        if pong.speed_x < 0:
            pong.speed_x -= 1
        if pong.speed_x > 0:
            pong.speed_x += 1
        if pong.speed_y < 0:
            pong.speed_y -= 1
        if pong.speed_y > 0:
            pong.speed_y += 1

    pygame.display.update()

pygame.quit()
