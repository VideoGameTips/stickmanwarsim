import pygame
import math

# Initialize Pygame
pygame.init()

# Set up the display
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Stickman Fighter")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

class Fighter:
    def __init__(self, x, y, color, controls):
        self.x = x
        self.y = y
        self.color = color
        self.controls = controls  # Dictionary of control keys
        self.health = 100
        self.velocity_y = 0
        self.is_jumping = False
        self.facing_right = True if color == BLUE else False
        self.punch_cooldown = 0
        self.attack_cooldowns = {
            'slide': 0,
            'kick': 0,
            'projectile': 0  # Generic name for fire/ice balls
        }
        self.projectiles = []  # Store active projectiles
        self.sliding = False
        self.slide_speed = 0
        self.projectile_type = 'fire' if color == RED else 'ice'  # Determine projectile type by player
        
    def move(self):
        speed = 5
        keys = pygame.key.get_pressed()
        
        # Horizontal movement
        if keys[self.controls['left']]:
            self.x -= speed
            self.facing_right = False
        if keys[self.controls['right']]:
            self.x += speed
            self.facing_right = True
            
        # Jumping
        if keys[self.controls['up']] and not self.is_jumping:
            self.velocity_y = -15
            self.is_jumping = True
            
        # Apply gravity
        self.velocity_y += 0.8
        self.y += self.velocity_y
        
        # Floor collision
        if self.y > HEIGHT - 100:
            self.y = HEIGHT - 100
            self.velocity_y = 0
            self.is_jumping = False
            
        # Screen boundaries
        self.x = max(50, min(self.x, WIDTH - 50))
        
        # Update punch cooldown
        if self.punch_cooldown > 0:
            self.punch_cooldown -= 1
        
        # Handle sliding
        if self.sliding:
            self.x += self.slide_speed
            self.slide_speed *= 0.9  # Slow down slide
            if abs(self.slide_speed) < 0.5:
                self.sliding = False
                self.slide_speed = 0
        
        # Update all cooldowns
        for attack in self.attack_cooldowns:
            if self.attack_cooldowns[attack] > 0:
                self.attack_cooldowns[attack] -= 1
                
        # Update projectiles
        for projectile in self.projectiles[:]:
            projectile['x'] += projectile['speed'] * projectile['direction']
            # Remove projectiles that go off screen
            if projectile['x'] < 0 or projectile['x'] > WIDTH:
                self.projectiles.remove(projectile)
    
    def punch(self, other):
        if self.punch_cooldown == 0:
            # Check if other fighter is in range
            distance = abs(self.x - other.x)
            if distance < 60:  # Punch range
                other.health -= 10
                self.punch_cooldown = 20  # Cooldown frames
                return True
        return False
    
    def slide(self):
        if self.attack_cooldowns['slide'] == 0:
            self.sliding = True
            self.slide_speed = 15 if self.facing_right else -15
            self.attack_cooldowns['slide'] = 45
            return True
        return False
    
    def kick(self, other):
        if self.attack_cooldowns['kick'] == 0:
            distance = abs(self.x - other.x)
            if distance < 70:
                other.health -= 15
                other.velocity_y = -10  # Strong upward knockback
                self.attack_cooldowns['kick'] = 30
                return True
        return False
    
    def launch_projectile(self):
        if self.attack_cooldowns['projectile'] == 0:
            direction = 1 if self.facing_right else -1
            self.projectiles.append({
                'x': self.x,
                'y': self.y - 10,
                'direction': direction,
                'speed': 8
            })
            self.attack_cooldowns['projectile'] = 60
            return True
        return False
    
    def draw(self):
        # Draw body
        pygame.draw.line(screen, self.color, (self.x, self.y - 20), (self.x, self.y + 20), 2)
        
        # Draw head
        pygame.draw.circle(screen, self.color, (self.x, self.y - 30), 10)
        
        # Draw arms (with punching animation)
        arm_angle = 45 if self.punch_cooldown > 15 else 0
        if self.facing_right:
            pygame.draw.line(screen, self.color, 
                           (self.x, self.y - 10),
                           (self.x + 15 * math.cos(math.radians(arm_angle)), 
                            self.y - 10 + 15 * math.sin(math.radians(arm_angle))), 2)
        else:
            pygame.draw.line(screen, self.color, 
                           (self.x, self.y - 10),
                           (self.x - 15 * math.cos(math.radians(arm_angle)), 
                            self.y - 10 + 15 * math.sin(math.radians(arm_angle))), 2)
        
        # Draw legs
        pygame.draw.line(screen, self.color, (self.x, self.y + 20), (self.x - 15, self.y + 40), 2)
        pygame.draw.line(screen, self.color, (self.x, self.y + 20), (self.x + 15, self.y + 40), 2)
        
        # Draw health bar
        pygame.draw.rect(screen, BLACK, (self.x - 25, self.y - 50, 50, 5))
        pygame.draw.rect(screen, GREEN, (self.x - 25, self.y - 50, 50 * (self.health/100), 5))
        
        # Draw projectiles
        for projectile in self.projectiles:
            self.draw_projectile(projectile)
    
    def draw_projectile(self, projectile):
        if self.projectile_type == 'fire':
            # Fire ball (orange/red)
            pygame.draw.circle(screen, (255, 165, 0), 
                            (int(projectile['x']), int(projectile['y'])), 8)
            pygame.draw.circle(screen, (255, 69, 0), 
                            (int(projectile['x'] - projectile['direction'] * 5), 
                             int(projectile['y'])), 6)
        else:
            # Ice ball (light blue/white)
            pygame.draw.circle(screen, (135, 206, 235), 
                            (int(projectile['x']), int(projectile['y'])), 8)
            pygame.draw.circle(screen, (255, 255, 255), 
                            (int(projectile['x'] - projectile['direction'] * 5), 
                             int(projectile['y'])), 6)

def main():
    clock = pygame.time.Clock()
    running = True
    
    # Update player1 controls with new attacks
    player1 = Fighter(200, HEIGHT - 100, RED, {
        'left': pygame.K_a,
        'right': pygame.K_d,
        'up': pygame.K_w,
        'slide': pygame.K_s,
        'kick': pygame.K_q,
        'projectile': pygame.K_z
    })
    
    # Updated Player 2 controls with new attacks
    player2 = Fighter(600, HEIGHT - 100, BLUE, {
        'left': pygame.K_LEFT,
        'right': pygame.K_RIGHT,
        'up': pygame.K_UP,
        'slide': pygame.K_DOWN,
        'kick': pygame.K_SLASH,
        'projectile': pygame.K_QUOTE
    })

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                # Handle Player 1 attacks
                if event.key == player1.controls['slide']:
                    player1.slide()
                if event.key == player1.controls['kick']:
                    player1.kick(player2)
                if event.key == player1.controls['projectile']:
                    player1.launch_projectile()
                
                # Handle Player 2 attacks
                if event.key == player2.controls['slide']:
                    player2.slide()
                if event.key == player2.controls['kick']:
                    player2.kick(player1)
                if event.key == player2.controls['projectile']:
                    player2.launch_projectile()
        
        # Update
        player1.move()
        player2.move()
        
        # Check Player 1's fireball collisions
        for projectile in player1.projectiles[:]:
            if (abs(projectile['x'] - player2.x) < 20 and 
                abs(projectile['y'] - player2.y) < 30):
                player2.health -= 20
                player1.projectiles.remove(projectile)
        
        # Check Player 2's iceball collisions
        for projectile in player2.projectiles[:]:
            if (abs(projectile['x'] - player1.x) < 20 and 
                abs(projectile['y'] - player1.y) < 30):
                player1.health -= 20
                # Ice effect: Slow down player1 briefly
                player1.speed = 2  # Temporary slow effect
                player2.projectiles.remove(projectile)
        
        # Check slide collisions for both players
        if player1.sliding:
            if (abs(player1.x - player2.x) < 30 and 
                abs(player1.y - player2.y) < 40):
                player2.health -= 15
                player2.x += 30 if player1.facing_right else -30
                player1.sliding = False
                
        if player2.sliding:
            if (abs(player2.x - player1.x) < 30 and 
                abs(player2.y - player1.y) < 40):
                player1.health -= 15
                player1.x += 30 if player2.facing_right else -30
                player2.sliding = False
        
        # Check for game over
        if player1.health <= 0 or player2.health <= 0:
            running = False
        
        # Draw
        screen.fill(WHITE)
        pygame.draw.line(screen, BLACK, (0, HEIGHT - 60), (WIDTH, HEIGHT - 60), 2)  # Ground line
        player1.draw()
        player2.draw()
        pygame.display.flip()
        
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
