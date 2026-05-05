import pygame
import sys
import random
import math

# Initialize Pygame FIRST
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (50, 150, 255)
GREEN = (50, 255, 150)
RED = (255, 50, 50)
YELLOW = (255, 255, 0)
ORANGE = (255, 150, 50)

class LoadingScreen:
    def __init__(self):
        self.angle = 0
    
    def update(self):
        self.angle += 10
    
    def draw(self, screen):
        screen.fill(BLUE)
        # Loading spinner
        for i in range(8):
            angle = self.angle + i * 45
            x = SCREEN_WIDTH//2 + 50 * math.cos(math.radians(angle))
            y = SCREEN_HEIGHT//2 + 50 * math.sin(math.radians(angle))
            pygame.draw.circle(screen, YELLOW, (int(x), int(y)), 8)
        
        font = pygame.font.Font(None, 48)
        text = font.render("LOADING...", True, WHITE)
        screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, SCREEN_HEIGHT//2 + 80))

class ResearchGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("🔬 RESEARCH HUNTER")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 32)
        self.tiny_font = pygame.font.Font(None, 24)
        
        # Game state
        self.reset_game()
        
        # Loading state
        self.loading_timer = 60
        self.loading = True
        self.loading_screen = LoadingScreen()
        
        # RELOADING SYSTEM (1.5 seconds = 90 frames at 60fps)
        self.reload_timer = 0
        self.max_reload_time = 90
        
        # DIFFICULTY SYSTEM
        self.base_obstacle_chance = 0.3  # 30% base chance
        self.projectiles = []
        self.state = "playing"  # playing, game_over
        
        print("🎮 Game initialized!")
    
    def reset_game(self):
        self.score = 0
        self.lives = 3
        self.game_active = True
        self.research_points = []
        self.obstacles = []
        self.player_pos = [SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100]
        self.spawn_timer = 0
        self.reload_timer = 0
    
    def get_obstacle_chance(self):
        """Dynamic obstacle spawn rate based on score milestones"""
        if self.score >= 20000:
            return 0.75  # 75% obstacles at 20k+
        elif self.score >= 15000:
            return 0.65  # 65% at 15k
        elif self.score >= 10000:
            return 0.55  # 55% at 10k
        elif self.score >= 5000:
            return 0.45  # 45% at 5k
        else:
            return self.base_obstacle_chance  # 30% base
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and self.game_active and self.state == "playing":
                    self.fire_projectiles()
                if event.key == pygame.K_r:
                    if self.state != "playing":
                        self.reset_game()
                        self.state = "playing"
        
        # Movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.player_pos[0] > 50:
            self.player_pos[0] -= 5
        if keys[pygame.K_RIGHT] and self.player_pos[0] < SCREEN_WIDTH - 50:
            self.player_pos[0] += 5
        if keys[pygame.K_UP] and self.player_pos[1] > 50:
            self.player_pos[1] -= 5
        if keys[pygame.K_DOWN] and self.player_pos[1] < SCREEN_HEIGHT - 50:
            self.player_pos[1] += 5
        
        return True
    
    def fire_projectiles(self):
        # Check if reloaded
        if self.reload_timer > 0:
            return
        
        # Start reload timer (1.5 seconds)
        self.reload_timer = self.max_reload_time
        
        # Fire 3 projectiles with spread
        for i in range(3):
            spread = (i - 1) * 15
            proj = {
                "x": self.player_pos[0],
                "y": self.player_pos[1],
                "vx": math.sin(math.radians(spread)) * 3,
                "vy": -8,
                "life": 120
            }
            self.projectiles.append(proj)
    
    def update_reload(self):
        if self.reload_timer > 0:
            self.reload_timer -= 1
    
    def get_reload_progress(self):
        if self.reload_timer <= 0:
            return 1.0
        return self.reload_timer / self.max_reload_time
    
    def update_projectiles(self):
        for proj in self.projectiles[:]:
            proj["x"] += proj["vx"]
            proj["y"] += proj["vy"]
            proj["life"] -= 1
            
            if proj["life"] <= 0 or proj["y"] < -20:
                self.projectiles.remove(proj)
    
    def check_projectile_hits(self):
        for proj in self.projectiles[:]:
            proj_rect = pygame.Rect(proj["x"]-8, proj["y"]-8, 16, 16)
            
            for point in self.research_points[:]:
                point_rect = pygame.Rect(point[0]-15, point[1]-15, 30, 30)
                if proj_rect.colliderect(point_rect):
                    self.score += point[2] * 2  # Double points!
                    self.research_points.remove(point)
                    self.projectiles.remove(proj)
                    break
    
    def spawn_objects(self):
        self.spawn_timer += 1
        if self.spawn_timer > 25:  # Slightly faster spawning
            obstacle_chance = self.get_obstacle_chance()
            
            if random.random() < (1.0 - obstacle_chance):  # Research points
                x = random.randint(50, SCREEN_WIDTH - 50)
                self.research_points.append([x, -20, 100])
            else:  # Obstacles - MORE FREQUENT at high scores!
                x = random.randint(50, SCREEN_WIDTH - 50)
                self.obstacles.append([x, -20])
            
            self.spawn_timer = 0
    
    def update_objects(self):
        # Research points
        for point in self.research_points[:]:
            point[1] += 3 + (self.score // 10000)  # Speed up slightly at high scores
            if point[1] > SCREEN_HEIGHT:
                self.research_points.remove(point)
        
        # Obstacles - FASTER at high scores
        for obstacle in self.obstacles[:]:
            obstacle[1] += 4 + (self.score // 10000)
            if obstacle[1] > SCREEN_HEIGHT:
                self.obstacles.remove(obstacle)
    
    def check_collisions(self):
        player_rect = pygame.Rect(self.player_pos[0]-25, self.player_pos[1]-25, 50, 50)
        
        for obstacle in self.obstacles[:]:
            obs_rect = pygame.Rect(obstacle[0]-20, obstacle[1]-20, 40, 40)
            if player_rect.colliderect(obs_rect):
                self.lives -= 1
                self.obstacles.remove(obstacle)
                if self.lives <= 0:
                    self.state = "game_over"
                return
    
    def update(self):
        if self.loading:
            self.loading_timer -= 1
            self.loading_screen.update()
            if self.loading_timer <= 0:
                self.loading = False
            return
        
        if self.state == "playing" and self.game_active:
            self.update_reload()
            self.spawn_objects()
            self.update_objects()
            self.update_projectiles()
            self.check_projectile_hits()
            self.check_collisions()
    
    def draw(self):
        if self.loading:
            self.loading_screen.draw(self.screen)
        else:
            self.screen.fill(BLUE)
            
            # Title
            title = self.font.render("SHOTGUN SLIME HUNTER", True, WHITE)
            self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 10))
            
            if self.state == "playing":
                # Player
                pygame.draw.circle(self.screen, WHITE, (int(self.player_pos[0]), int(self.player_pos[1])), 25)
                pygame.draw.circle(self.screen, BLACK, (int(self.player_pos[0]), int(self.player_pos[1])), 25, 3)
                
                # Research points
                for point in self.research_points:
                    pygame.draw.rect(self.screen, YELLOW, (point[0]-15, point[1]-15, 30, 30))
                    pygame.draw.rect(self.screen, GREEN, (point[0]-12, point[1]-12, 24, 24))
                
                # Obstacles
                for obstacle in self.obstacles:
                    pygame.draw.rect(self.screen, RED, (obstacle[0]-20, obstacle[1]-20, 40, 40))
                    pygame.draw.rect(self.screen, BLACK, (obstacle[0]-20, obstacle[1]-20, 40, 40), 3)
                
                # Projectiles
                for proj in self.projectiles:
                    pygame.draw.circle(self.screen, ORANGE, (int(proj["x"]), int(proj["y"])), 6)
                    pygame.draw.circle(self.screen, YELLOW, (int(proj["x"]), int(proj["y"])), 6, 2)
                
                # RELOAD BAR
                reload_bar_empty = pygame.Rect(20, 80, 200, 20)
                pygame.draw.rect(self.screen, BLACK, reload_bar_empty)
                
                reload_progress = self.get_reload_progress()
                fill_width = int((1.0 - reload_progress) * 200)
                reload_color = GREEN if reload_progress < 0.2 else YELLOW if reload_progress < 0.5 else RED
                
                if fill_width > 0:
                    pygame.draw.rect(self.screen, reload_color, (20, 80, fill_width, 20))
                
                pygame.draw.rect(self.screen, WHITE, reload_bar_empty, 2)
                
                reload_label = self.tiny_font.render("RELOAD", True, WHITE)
                self.screen.blit(reload_label, (20, 65))
                
                reload_time = max(0, int(self.reload_timer / 60))
                reload_text = self.tiny_font.render(f"({reload_time}s)", True, WHITE)
                self.screen.blit(reload_text, (230, 65))
                
                # DIFFICULTY INDICATOR
                obstacle_chance = self.get_obstacle_chance()
                diff_text = self.tiny_font.render(f"DANGER: {int(obstacle_chance*100)}%", True, RED)
                self.screen.blit(diff_text, (SCREEN_WIDTH - 200, 65))
                
                # UI
                score_text = self.small_font.render(f"SCORE: {self.score}", True, WHITE)
                lives_text = self.small_font.render(f"LIVES: {self.lives}", True, WHITE)
                
                self.screen.blit(score_text, (20, SCREEN_HEIGHT - 80))
                self.screen.blit(lives_text, (20, SCREEN_HEIGHT - 50))
                
                controls = self.tiny_font.render("←→↑↓ MOVE | SPACE FIRE | R RESTART", True, WHITE)
                self.screen.blit(controls, (20, SCREEN_HEIGHT - 25))
            
            elif self.state == "game_over":
                game_over = self.font.render("GAME OVER", True, RED)
                final_score = self.small_font.render(f"FINAL SCORE: {self.score}", True, WHITE)
                restart = self.small_font.render("PRESS R TO PLAY AGAIN", True, YELLOW)
                
                self.screen.blit(game_over, (SCREEN_WIDTH//2 - game_over.get_width()//2, 200))
                self.screen.blit(final_score, (SCREEN_WIDTH//2 - final_score.get_width()//2, 300))
                self.screen.blit(restart, (SCREEN_WIDTH//2 - restart.get_width()//2, 380))
        
        pygame.display.flip()
    
    def run(self):
        print("🎮 Starting game loop...")
        running = True
        
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    print("SHOTGUN SLIME HUNTER 2D- DYNAMIC DIFFICULTY")
    print("DIFFICULTY MILESTONES:")
    print("0-4999: 30% red boxes")
    print("5000+: 45% red boxes")
    print("10000+: 55% red boxes") 
    print("15000+: 65% red boxes")
    print("20000+: 75% red boxes")
    print("\nCONTROLS:")
    print("←→↑↓ = Move | SPACE = FIRE (1.5s reload)")
    
    game = ResearchGame()
    game.run()