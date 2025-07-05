import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Set up the display
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ball Breaker")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)

# Font
font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 24)

class Ball:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        # Random direction
        angle = random.uniform(0, 2 * math.pi)
        self.dx = math.cos(angle) * 3
        self.dy = math.sin(angle) * 3
        self.radius = 8
        self.color = (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))
        
    def move(self):
        self.x += self.dx
        self.y += self.dy
        
        # Bounce off walls
        if self.x <= self.radius or self.x >= WIDTH - self.radius:
            self.dx *= -1
        if self.y <= self.radius or self.y >= HEIGHT - self.radius:
            self.dy *= -1
            
    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        
    def check_collision(self, platform):
        # Check if ball collides with platform
        closest_x = max(platform.x, min(self.x, platform.x + platform.width))
        closest_y = max(platform.y, min(self.y, platform.y + platform.height))
        
        distance = math.sqrt((self.x - closest_x)**2 + (self.y - closest_y)**2)
        return distance <= self.radius

class Platform:
    def __init__(self, x, y, width, height, health):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.max_health = health
        self.health = health
        self.color = GREEN
        self.damage_cooldown = 0
        self.cooldown_time = 30  # 0.5 seconds at 60 FPS
        
    def take_damage(self, damage=1):
        if self.damage_cooldown <= 0:
            self.health -= damage
            self.damage_cooldown = self.cooldown_time
            # Update color based on health percentage
            health_percent = self.health / self.max_health
            if health_percent > 0.6:
                self.color = GREEN
            elif health_percent > 0.3:
                self.color = YELLOW
            else:
                self.color = RED
            return True
        return False
            
    def is_destroyed(self):
        return self.health <= 0
        
    def draw(self):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        # Draw health bar
        health_width = (self.width * self.health) / self.max_health
        pygame.draw.rect(screen, BLACK, (self.x, self.y - 10, self.width, 5))
        pygame.draw.rect(screen, GREEN, (self.x, self.y - 10, health_width, 5))

class Game:
    def __init__(self):
        self.balls = []
        self.platforms = []
        self.money = 100
        self.ball_cost = 20
        self.score = 0
        
        # Create initial platforms
        self.create_platforms()
        
    def create_platforms(self):
        # Create platforms in different positions
        platform_configs = [
            (100, 100, 80, 20, 3),
            (300, 150, 100, 25, 4),
            (500, 120, 60, 30, 2),
            (200, 300, 120, 20, 5),
            (400, 250, 90, 25, 3),
            (600, 200, 70, 30, 4),
            (150, 400, 110, 20, 3),
            (350, 350, 80, 25, 4),
            (550, 380, 100, 20, 65),
        ]
        
        for x, y, w, h, health in platform_configs:
            self.platforms.append(Platform(x, y, w, h, health))
    
    def buy_ball(self):
        if self.money >= self.ball_cost:
            self.money -= self.ball_cost
            # Spawn ball in center of screen
            self.balls.append(Ball(WIDTH // 2, HEIGHT // 2))
            return True
        return False
    
    def update(self):
        # Update balls
        for ball in self.balls[:]:
            ball.move()
            
            # Check collisions with platforms
            for platform in self.platforms[:]:
                if ball.check_collision(platform):
                    platform_center_x = platform.x + platform.width / 2
                    platform_center_y = platform.y + platform.height / 2
                    diff_x = abs(ball.x - platform_center_x)
                    diff_y = abs(ball.y - platform_center_y)
                    if diff_x > diff_y:
                        ball.dx *= -1
                    else:
                        ball.dy *= -1

                   
                   
                    if platform.take_damage():
                        if platform.is_destroyed():
                            self.platforms.remove(platform)
                            self.score += 10
                            self.money += 5  # Reward for destroying platform
                    break
        
        # Update platform cooldowns
        for platform in self.platforms:
            if platform.damage_cooldown > 0:
                platform.damage_cooldown -= 1
    
    def draw(self):
        screen.fill(BLACK)
        
        # Draw platforms
        for platform in self.platforms:
            platform.draw()
        
        # Draw balls
        for ball in self.balls:
            ball.draw()
        
        # Draw UI
        # Money display
        money_text = font.render(f"Money: ${self.money}", True, WHITE)
        screen.blit(money_text, (10, 10))
        
        # Score display
        score_text = font.render(f"Score: {self.score}", True, WHITE)
        screen.blit(score_text, (10, 50))
        
        # Ball cost display
        cost_text = small_font.render(f"Ball Cost: ${self.ball_cost}", True, WHITE)
        screen.blit(cost_text, (10, 90))
        
        # Instructions
        instructions = [
            "Click SPACE to buy a ball",
            "Balls spawn in center and move randomly",
            "Destroy platforms to earn money and score!"
        ]
        
        for i, instruction in enumerate(instructions):
            inst_text = small_font.render(instruction, True, GRAY)
            screen.blit(inst_text, (10, HEIGHT - 80 + i * 20))
        
        # Ball count
        ball_count_text = small_font.render(f"Active Balls: {len(self.balls)}", True, WHITE)
        screen.blit(ball_count_text, (WIDTH - 150, 10))
        
        # Platform count
        platform_count_text = small_font.render(f"Platforms: {len(self.platforms)}", True, WHITE)
        screen.blit(platform_count_text, (WIDTH - 150, 30))

def main():
    clock = pygame.time.Clock()
    game = Game()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if not game.buy_ball():
                        # Show "not enough money" message
                        print("Not enough money!")
        
        game.update()
        game.draw()
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    main()
