import pygame
import sys
from word_ladder import WordLadderGame
from typing import Optional, Tuple
import string
import math

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 768
PADDING = 20
BUTTON_HEIGHT = 50
BUTTON_WIDTH = 200
INPUT_HEIGHT = 50
INPUT_WIDTH = 300

# Colors
BACKGROUND_COLOR = (245, 247, 250)
PRIMARY_COLOR = (88, 86, 214)    # Modern Purple
SECONDARY_COLOR = (106, 90, 205)  # Slate Blue
SUCCESS_COLOR = (46, 213, 115)   # Vibrant Green
ERROR_COLOR = (255, 71, 87)      # Soft Red
WHITE = (255, 255, 255)
BLACK = (30, 30, 30)
GRAY = (158, 158, 158)
LIGHT_GRAY = (240, 240, 240)

# Animation constants
ANIMATION_SPEED = 0.05
HOVER_SCALE = 1.05

class AnimatedButton:
    def __init__(self, x: int, y: int, width: int, height: int, text: str, color: Tuple[int, int, int]):
        self.original_rect = pygame.Rect(x, y, width, height)
        self.rect = self.original_rect.copy()
        self.text = text
        self.color = color
        self.hover = False
        self.scale = 1.0
        self.animation_progress = 0
        
    def draw(self, screen: pygame.Surface):
        target_scale = HOVER_SCALE if self.hover else 1.0
        self.scale += (target_scale - self.scale) * ANIMATION_SPEED
        
        # Calculate scaled dimensions
        scaled_width = int(self.original_rect.width * self.scale)
        scaled_height = int(self.original_rect.height * self.scale)
        x = self.original_rect.centerx - scaled_width // 2
        y = self.original_rect.centery - scaled_height // 2
        
        self.rect = pygame.Rect(x, y, scaled_width, scaled_height)
        
        # Draw button with shadow
        shadow_rect = self.rect.copy()
        shadow_rect.y += 3
        pygame.draw.rect(screen, (*BLACK, 30), shadow_rect, border_radius=12)
        
        # Draw main button
        color = tuple(min(c + 20, 255) for c in self.color) if self.hover else self.color
        pygame.draw.rect(screen, color, self.rect, border_radius=12)
        
        # Add gradient effect
        gradient_rect = self.rect.copy()
        gradient_rect.height = self.rect.height // 2
        gradient = pygame.Surface((gradient_rect.width, gradient_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(gradient, (255, 255, 255, 30), gradient.get_rect(), border_radius=12)
        screen.blit(gradient, gradient_rect)
        
        # Draw text with shadow
        font = pygame.font.Font(None, 32)
        shadow_surface = font.render(self.text, True, (*BLACK, 128))
        shadow_rect = shadow_surface.get_rect(center=(self.rect.centerx + 1, self.rect.centery + 1))
        screen.blit(shadow_surface, shadow_rect)
        
        text_surface = font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
        
    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)
            
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.hover:
                return True
        return False

class ModernInputBox:
    def __init__(self, x: int, y: int, width: int, height: int):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = ''
        self.active = False
        self.animation_progress = 0
        
    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        if event.type == pygame.MOUSEBUTTONDOWN:
            was_active = self.active
            self.active = self.rect.collidepoint(event.pos)
            if self.active and not was_active:
                self.animation_progress = 0
            
        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                text = self.text.lower()
                self.text = ''
                return text
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.unicode in string.ascii_letters:
                self.text += event.unicode
        return None
        
    def draw(self, screen: pygame.Surface):
        # Draw input box background
        pygame.draw.rect(screen, LIGHT_GRAY, self.rect, border_radius=12)
        
        # Animated border
        if self.active:
            self.animation_progress = min(1, self.animation_progress + ANIMATION_SPEED)
        else:
            self.animation_progress = max(0, self.animation_progress - ANIMATION_SPEED)
            
        border_color = tuple(int(a + (b - a) * self.animation_progress) 
                           for a, b in zip(GRAY, PRIMARY_COLOR))
        pygame.draw.rect(screen, border_color, self.rect, 2, border_radius=12)
        
        # Draw text with placeholder
        font = pygame.font.Font(None, 32)
        if self.text:
            text_surface = font.render(self.text, True, BLACK)
        else:
            text_surface = font.render("Type a word...", True, GRAY)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

class WordLadderGUI:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Word Ladder - An Elegant Word Game")
        
        self.game = WordLadderGame()
        self.game_state = None
        self.animation_time = 0
        
        # Create UI elements
        center_x = WINDOW_WIDTH // 2
        self.input_box = ModernInputBox(center_x - INPUT_WIDTH//2, 
                                      WINDOW_HEIGHT//2, 
                                      INPUT_WIDTH, 
                                      INPUT_HEIGHT)
        
        self.buttons = {
            'start': AnimatedButton(center_x - BUTTON_WIDTH - PADDING, 
                                  WINDOW_HEIGHT - BUTTON_HEIGHT - PADDING,
                                  BUTTON_WIDTH, 
                                  BUTTON_HEIGHT, 
                                  "New Game", 
                                  PRIMARY_COLOR),
            'hint': AnimatedButton(center_x + PADDING, 
                                 WINDOW_HEIGHT - BUTTON_HEIGHT - PADDING,
                                 BUTTON_WIDTH, 
                                 BUTTON_HEIGHT, 
                                 "Get Hint", 
                                 SECONDARY_COLOR)
        }
        
        self.message = ""
        self.message_color = BLACK
        self.message_animation = 0
        
    def draw(self):
        self.screen.fill(BACKGROUND_COLOR)
        self.animation_time += 0.02
        
        # Draw decorative background patterns
        for i in range(10):
            x = WINDOW_WIDTH * 0.1 * i
            y = WINDOW_HEIGHT * (0.5 + 0.2 * math.sin(self.animation_time + i * 0.5))
            radius = 20 + 10 * math.sin(self.animation_time * 2 + i)
            pygame.draw.circle(self.screen, (*PRIMARY_COLOR, 30), (int(x), int(y)), int(radius))
        
        # Draw game title with animation
        font_large = pygame.font.Font(None, 72)
        title_scale = 1 + 0.05 * math.sin(self.animation_time * 2)
        title = font_large.render("Word Ladder", True, PRIMARY_COLOR)
        title = pygame.transform.scale(title, 
                                     (int(title.get_width() * title_scale), 
                                      int(title.get_height() * title_scale)))
        title_rect = title.get_rect(centerx=WINDOW_WIDTH//2, y=PADDING)
        self.screen.blit(title, title_rect)
        
        if self.game_state:
            # Draw game info with modern styling
            font = pygame.font.Font(None, 36)
            
            # Game info panel
            info_panel = pygame.Surface((300, 150), pygame.SRCALPHA)
            pygame.draw.rect(info_panel, (*WHITE, 200), info_panel.get_rect(), border_radius=15)
            
            # Start word
            start_text = font.render(f"Start: {self.game_state['start_word']}", True, BLACK)
            info_panel.blit(start_text, (20, 20))
            
            # Target word
            target_text = font.render(f"Target: {self.game_state['target_word']}", True, BLACK)
            info_panel.blit(target_text, (20, 60))
            
            # Moves
            moves_text = font.render(f"Moves: {self.game_state['moves']}/{self.game_state['max_moves']}", True, BLACK)
            info_panel.blit(moves_text, (20, 100))
            
            self.screen.blit(info_panel, (PADDING, 100))
            
            # Current word with pulsing effect
            scale = 1 + 0.1 * math.sin(self.animation_time * 3)
            current_text = font.render(f"Current: {self.game_state['current_word']}", True, PRIMARY_COLOR)
            current_text = pygame.transform.scale(current_text,
                                               (int(current_text.get_width() * scale),
                                                int(current_text.get_height() * scale)))
            current_rect = current_text.get_rect(centerx=WINDOW_WIDTH//2, y=WINDOW_HEIGHT//2 - 100)
            self.screen.blit(current_text, current_rect)
            
            # Path with animated arrow
            arrow_offset = 10 * math.sin(self.animation_time * 4)
            path_text = font.render("Path: " + " → ".join(self.game_state['path']), True, SECONDARY_COLOR)
            path_rect = path_text.get_rect(centerx=WINDOW_WIDTH//2 + arrow_offset, y=WINDOW_HEIGHT//2 + 100)
            self.screen.blit(path_text, path_rect)
            
        # Draw message with fade animation
        if self.message:
            if self.message_animation < 1:
                self.message_animation = min(1, self.message_animation + 0.05)
            font = pygame.font.Font(None, 36)
            message_text = font.render(self.message, True, self.message_color)
            message_text.set_alpha(int(255 * self.message_animation))
            message_rect = message_text.get_rect(centerx=WINDOW_WIDTH//2, y=WINDOW_HEIGHT//2 - 50)
            self.screen.blit(message_text, message_rect)
        
        # Draw UI elements
        self.input_box.draw(self.screen)
        for button in self.buttons.values():
            button.draw(self.screen)
            
        pygame.display.flip()
        
    def show_message(self, text: str, color: Tuple[int, int, int]):
        self.message = text
        self.message_color = color
        self.message_animation = 0
        
    def run(self):
        clock = pygame.time.Clock()
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    
                # Handle button events
                if self.buttons['start'].handle_event(event):
                    self.game_state = self.game.start_game('BEGINNER')
                    self.show_message("Game started! Enter your word", BLACK)
                    
                elif self.buttons['hint'].handle_event(event):
                    if self.game_state and self.game_state['status'] == 'PLAYING':
                        hint = self.game.get_hint()
                        if hint:
                            self.show_message(f"Hint: Try '{hint}'", SECONDARY_COLOR)
                    
                # Handle input box events
                word = self.input_box.handle_event(event)
                if word:
                    if not self.game_state or self.game_state['status'] != 'PLAYING':
                        self.show_message("Start a new game first!", ERROR_COLOR)
                    else:
                        try:
                            self.game_state = self.game.make_move(word)
                            if self.game_state['status'] == 'WON':
                                self.show_message("Congratulations! You won!", SUCCESS_COLOR)
                            elif self.game_state['status'] == 'LOST':
                                self.show_message("Game Over! Try again!", ERROR_COLOR)
                        except ValueError as e:
                            self.show_message(str(e), ERROR_COLOR)
            
            self.draw()
            clock.tick(60)
            
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    gui = WordLadderGUI()
    gui.run()