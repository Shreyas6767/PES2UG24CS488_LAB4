from email import message

import pygame

from .paddle import Paddle
from .ball import Ball
from .brick import Brick

# Game Engine

WHITE = (255, 255, 255)
BG = (15, 15, 25)
BRICK_COLORS = [
    (200, 60, 60),
    (200, 140, 60),
    (200, 200, 60),
    (80, 180, 80),
    (80, 140, 200),
]

class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.paddle = Paddle(width // 2 - 50, height - 30, 100, 14)

        self.ball = Ball(width // 2, height - 50, radius=8)
        self.ball.vx, self.ball.vy = 4, -4

        self.rows, self.cols = 5, 8
        self.bricks = self._build_bricks(self.rows, self.cols)

        self.lives = 3
        self.score = 0
        self.font = pygame.font.SysFont("Arial", 28)
        self.game_over = False
        self.result = None  # "win" or "lose"
        self.paddle_sound = pygame.mixer.Sound("sounds/paddle.mp3")
        self.brick_sound = pygame.mixer.Sound("sounds/brick.mp3")
        self.lose_sound = pygame.mixer.Sound("sounds/lose.mp3")
        self.win_sound = pygame.mixer.Sound("sounds/win.mp3")

    def _build_bricks(self, rows, cols):
        bricks = []
        margin, gap, top = 30, 6, 60
        brick_w = (self.width - margin * 2 - gap * (cols - 1)) // cols
        brick_h = 22
        for r in range(rows):
            for c in range(cols):
                x = margin + c * (brick_w + gap)
                y = top + r * (brick_h + gap)
                bricks.append(Brick(x, y, brick_w, brick_h))
        return bricks

    def handle_event(self, event):
        if not self.game_over:
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                self.reset_game("easy")

            elif event.key == pygame.K_2:
                self.reset_game("medium")

            elif event.key == pygame.K_3:
                self.reset_game("hard")
            elif event.key == pygame.K_q:
                pygame.event.post(pygame.event.Event(pygame.QUIT))

    def handle_input(self):
        if self.game_over:
            return
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.paddle.move(-self.paddle.speed, self.width)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.paddle.move(self.paddle.speed, self.width)

    def update(self):
        if self.game_over:
            return

        previous_rect = self.ball.rect()
        self.ball.move()
        current_rect = self.ball.rect()

        if self.ball.x - self.ball.radius <= 0 or self.ball.x + self.ball.radius >= self.width:
            self.ball.vx *= -1
        if self.ball.y - self.ball.radius <= 0:
            self.ball.vy *= -1

        if current_rect.colliderect(self.paddle.rect()):
            self.paddle_sound.play()
            paddle_rect = self.paddle.rect()

            if previous_rect.bottom <= paddle_rect.top and current_rect.bottom >= paddle_rect.top:
                self.ball.vy = -abs(self.ball.vy)

            elif previous_rect.top >= paddle_rect.bottom and current_rect.top <= paddle_rect.bottom:
                self.ball.vy = abs(self.ball.vy)

            elif previous_rect.right <= paddle_rect.left and current_rect.right >= paddle_rect.left:
                self.ball.vx = -abs(self.ball.vx)

            elif previous_rect.left >= paddle_rect.right and current_rect.left <= paddle_rect.right:
                self.ball.vx = abs(self.ball.vx)

        for brick in self.bricks:
            if brick.alive and current_rect.colliderect(brick.rect()):
                self.brick_sound.play()
                brick_rect = brick.rect()
                brick.alive = False
                self.score += 1

                if previous_rect.bottom <= brick_rect.top and current_rect.bottom >= brick_rect.top:
                    self.ball.vy = -abs(self.ball.vy)

                elif previous_rect.top >= brick_rect.bottom and current_rect.top <= brick_rect.bottom:
                    self.ball.vy = abs(self.ball.vy)

                elif previous_rect.right <= brick_rect.left and current_rect.right >= brick_rect.left:
                    self.ball.vx = -abs(self.ball.vx)

                elif previous_rect.left >= brick_rect.right and current_rect.left <= brick_rect.right:
                    self.ball.vx = abs(self.ball.vx)

                break

        if self.ball.y - self.ball.radius > self.height:
            self.lives -= 1
            self.lose_sound.play()
            if self.lives <= 0:
                self.game_over = True
                self.result = "lose"
            else:
                self._reset_ball()

        if all(not b.alive for b in self.bricks):
            self.game_over = True
            self.result = "win"
            self.win_sound.play()

    def _reset_ball(self):
        self.ball.x, self.ball.y = self.width // 2, self.height - 50
        self.ball.vx, self.ball.vy = 4, -4

    def reset_game(self, difficulty="medium"):
        if difficulty == "easy":
            paddle_width = 120
            ball_speed = 3

        elif difficulty == "hard":
            paddle_width = 80
            ball_speed = 6

        else:
            paddle_width = 100
            ball_speed = 4

        self.paddle = Paddle(
            self.width // 2 - paddle_width // 2,
            self.height - 30,
            paddle_width,
            14
        )

        self.ball = Ball(
            self.width // 2,
            self.height - 50,
            radius=8
        )

        self.ball.vx = ball_speed
        self.ball.vy = -ball_speed

        self.bricks = self._build_bricks(self.rows, self.cols)

        self.lives = 3
        self.score = 0
        self.game_over = False
        self.result = None

    def render(self, screen):
        screen.fill(BG)

        pygame.draw.rect(screen, WHITE, self.paddle.rect())
        pygame.draw.circle(screen, WHITE, (int(self.ball.x), int(self.ball.y)), self.ball.radius)

        for i, brick in enumerate(self.bricks):
            if brick.alive:
                row = i // self.cols
                color = BRICK_COLORS[row % len(BRICK_COLORS)]
                pygame.draw.rect(screen, color, brick.rect())

        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        lives_text = self.font.render(f"Lives: {self.lives}", True, WHITE)
        screen.blit(lives_text, (self.width - 130, 10))

        if self.game_over:
            if self.result == "win":
                message = "YOU WIN!"
            else:
                message = "GAME OVER"

            result_text = self.font.render(message, True, WHITE)
            score_text = self.font.render(
                f"Final Score: {self.score}", True, WHITE
            )

            screen.blit(
                result_text,
                (
                    self.width // 2 - result_text.get_width() // 2,
                    self.height // 2 - 40,
                ),
            )

            screen.blit(
                score_text,
                (
                    self.width // 2 - score_text.get_width() // 2,
                    self.height // 2 + 10,
                ),
            )

            replay_text = self.font.render(
                "1 - Easy   2 - Medium   3 - Hard",
                True,
                WHITE
            )

            quit_text = self.font.render(
                "Q - Quit",
                True,
                WHITE
            )

            screen.blit(
                replay_text,
                (
                    self.width // 2 - replay_text.get_width() // 2,
                    self.height // 2 + 60,
                ),
            )

            screen.blit(
                quit_text,
                (
                    self.width // 2 - quit_text.get_width() // 2,
                    self.height // 2 + 100,
                ),
            )
