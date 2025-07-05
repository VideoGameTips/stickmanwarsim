import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Set up the display
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Stickman Battle")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

class Bullet:
    def __init__(self, x, y, dx, dy, team):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.team = team
        self.speed = 7
        self.damage = 20
        
    def move(self):
        self.x += self.dx * self.speed
        self.y += self.dy * self.speed
        
    def draw(self):
        color = RED if self.team == 'red' else BLUE
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), 3)

class Stickman:
    def __init__(self, x, y, team):
        self.x = x
        self.y = y
        self.team = team  # 'red' or 'blue'
        self.health = 100
        self.speed = 2
        self.attack_range = 50
        self.attack_damage = 10
        self.target = None
        self.shoot_timer = 0
        self.shoot_delay = 60  # Shoot every 1 second (60 frames)
        
    def draw(self):
        # Draw body
        color = RED if self.team == 'red' else BLUE
        pygame.draw.line(screen, color, (self.x, self.y - 20), (self.x, self.y + 20), 2)
        # Draw head
        pygame.draw.circle(screen, color, (self.x, self.y - 30), 10)
        # Draw arms
        pygame.draw.line(screen, color, (self.x, self.y - 10), (self.x - 15, self.y), 2)
        pygame.draw.line(screen, color, (self.x, self.y - 10), (self.x + 15, self.y), 2)
        # Draw legs
        pygame.draw.line(screen, color, (self.x, self.y + 20), (self.x - 15, self.y + 40), 2)
        pygame.draw.line(screen, color, (self.x, self.y + 20), (self.x + 15, self.y + 40), 2)
        
        # Draw health bar
        pygame.draw.rect(screen, BLACK, (self.x - 20, self.y - 50, 40, 5))
        pygame.draw.rect(screen, color, (self.x - 20, self.y - 50, 40 * (self.health/100), 5))
        
        # Draw gun
        gun_angle = math.atan2(self.target.y - self.y if self.target else 0, 
                             self.target.x - self.x if self.target else 1)
        gun_length = 20
        gun_end_x = self.x + math.cos(gun_angle) * gun_length
        gun_end_y = self.y + math.sin(gun_angle) * gun_length
        color = RED if self.team == 'red' else BLUE
        pygame.draw.line(screen, color, (self.x, self.y), (gun_end_x, gun_end_y), 3)

    def move_towards(self, target):
        dx = target.x - self.x
        dy = target.y - self.y
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance > self.attack_range:
            self.x += (dx/distance) * self.speed
            self.y += (dy/distance) * self.speed

    def attack(self, target):
        distance = math.sqrt((target.x - self.x)**2 + (target.y - self.y)**2)
        if distance <= self.attack_range:
            target.health -= self.attack_damage
            return True
        return False

    def shoot(self, target):
        if not target:
            return None
            
        dx = target.x - self.x
        dy = target.y - self.y
        distance = math.sqrt(dx**2 + dy**2)
        if distance == 0:
            return None
            
        dx = dx / distance
        dy = dy / distance
        
        return Bullet(self.x, self.y, dx, dy, self.team)

class Game:
    def __init__(self):
        # Define base positions at the bottom of the screen
        self.red_base_x = 100
        self.blue_base_x = WIDTH - 100
        self.base_y = HEIGHT - 80  # Position bases slightly above bottom
        
        # Spawn initial armies at their bases
        self.red_army = [Stickman(self.red_base_x, self.base_y, 'red') 
                        for _ in range(5)]
        self.blue_army = [Stickman(self.blue_base_x, self.base_y, 'blue') 
                         for _ in range(5)]
        
        # Add spawn timer
        self.spawn_timer = 0
        self.spawn_delay = 180  # Spawn new soldier every 3 seconds (60 fps * 3)
        
        self.bullets = []
    
    def update(self):
        # Handle spawning new soldiers
        self.spawn_timer += 1
        if self.spawn_timer >= self.spawn_delay:
            self.spawn_timer = 0
            self.red_army.append(Stickman(self.red_base_x, self.base_y, 'red'))
            self.blue_army.append(Stickman(self.blue_base_x, self.base_y, 'blue'))
        
        # Update bullets
        for bullet in self.bullets[:]:
            bullet.move()
            
            # Remove bullets that are off screen
            if (bullet.x < 0 or bullet.x > WIDTH or 
                bullet.y < 0 or bullet.y > HEIGHT):
                self.bullets.remove(bullet)
                continue
                
            # Check bullet collisions
            if bullet.team == 'red':
                for enemy in self.blue_army:
                    if (abs(bullet.x - enemy.x) < 15 and 
                        abs(bullet.y - enemy.y) < 20):
                        enemy.health -= bullet.damage
                        if bullet in self.bullets:
                            self.bullets.remove(bullet)
                        break
            else:
                for enemy in self.red_army:
                    if (abs(bullet.x - enemy.x) < 15 and 
                        abs(bullet.y - enemy.y) < 20):
                        enemy.health -= bullet.damage
                        if bullet in self.bullets:
                            self.bullets.remove(bullet)
                        break
        
        # Update red army
        for soldier in self.red_army[:]:
            if soldier.health <= 0:
                self.red_army.remove(soldier)
                continue
                
            # Find nearest enemy
            nearest = None
            min_dist = float('inf')
            for enemy in self.blue_army:
                dist = math.sqrt((enemy.x - soldier.x)**2 + (enemy.y - soldier.y)**2)
                if dist < min_dist:
                    min_dist = dist
                    nearest = enemy
                    
            if nearest:
                soldier.target = nearest
                soldier.move_towards(nearest)
                
                # Handle shooting
                soldier.shoot_timer += 1
                if soldier.shoot_timer >= soldier.shoot_delay:
                    soldier.shoot_timer = 0
                    bullet = soldier.shoot(nearest)
                    if bullet:
                        self.bullets.append(bullet)

        # Update blue army
        for soldier in self.blue_army[:]:
            if soldier.health <= 0:
                self.blue_army.remove(soldier)
                continue
                
            # Find nearest enemy
            nearest = None
            min_dist = float('inf')
            for enemy in self.red_army:
                dist = math.sqrt((enemy.x - soldier.x)**2 + (enemy.y - soldier.y)**2)
                if dist < min_dist:
                    min_dist = dist
                    nearest = enemy
                    
            if nearest:
                soldier.target = nearest
                soldier.move_towards(nearest)
                
                # Handle shooting
                soldier.shoot_timer += 1
                if soldier.shoot_timer >= soldier.shoot_delay:
                    soldier.shoot_timer = 0
                    bullet = soldier.shoot(nearest)
                    if bullet:
                        self.bullets.append(bullet)

    def draw(self):
        screen.fill(WHITE)
        
        # Draw bases
        pygame.draw.rect(screen, RED, (self.red_base_x - 30, self.base_y, 60, 60))
        pygame.draw.rect(screen, BLUE, (self.blue_base_x - 30, self.base_y, 60, 60))
        
        # Draw bullets
        for bullet in self.bullets:
            bullet.draw()
            
        # Draw soldiers
        for soldier in self.red_army:
            soldier.draw()
        for soldier in self.blue_army:
            soldier.draw()
        
        pygame.display.flip()

def main():
    clock = pygame.time.Clock()
    game = Game()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        game.update()
        game.draw()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main() 