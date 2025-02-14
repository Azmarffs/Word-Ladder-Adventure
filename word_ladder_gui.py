import pygame
import sys
from word_ladder import WordLadderGame
from typing import Optional, Tuple, Dict, List
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

# Graph visualization constants
NODE_RADIUS = 30
NODE_SPACING = 100
GRAPH_CENTER_X = WINDOW_WIDTH // 2
GRAPH_CENTER_Y = WINDOW_HEIGHT // 2

# Animation constants
ANIMATION_SPEED = 0.05
HOVER_SCALE = 1.05

class Tutorial:
    def __init__(self):
        self.steps = [
            "Welcome to Word Ladder! Transform one word into another by changing one letter at a time.",
            "Click 'New Game' to start a new puzzle with random words.",
            "Type your word in the input box and press Enter to make a move.",
            "Each word must be a valid English word and differ by only one letter.",
            "Need help? Click 'Get Hint' for a suggestion!",
            "Try to reach the target word within the move limit. Good luck!"
        ]
        self.current_step = 0
        self.visible = True
        self.fade = 1.0
        
    def draw(self, screen: pygame.Surface):
        if not self.visible:
            return
            
        font = pygame.font.Font(None, 32)
        text = self.steps[self.current_step]
        
        # Create tutorial panel
        padding = 20
        text_surface = font.render(text, True, BLACK)
        panel_width = text_surface.get_width() + padding * 2
        panel_height = text_surface.get_height() + padding * 2
        
        panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        panel.fill((*WHITE, int(220 * self.fade)))
        pygame.draw.rect(panel, (*PRIMARY_COLOR, int(50 * self.fade)), panel.get_rect(), 2, border_radius=10)
        
        # Add text
        text_surface.set_alpha(int(255 * self.fade))
        panel.blit(text_surface, (padding, padding))
        
        # Draw on screen
        x = (WINDOW_WIDTH - panel_width) // 2
        y = WINDOW_HEIGHT - panel_height - PADDING * 3
        screen.blit(panel, (x, y))
        
        # Draw navigation dots
        dot_y = y + panel_height + 10
        for i in range(len(self.steps)):
            dot_color = PRIMARY_COLOR if i == self.current_step else GRAY
            dot_x = WINDOW_WIDTH // 2 - (len(self.steps) * 15) // 2 + i * 15
            pygame.draw.circle(screen, dot_color, (dot_x, dot_y), 4)
    
    def next_step(self):
        self.current_step = (self.current_step + 1) % len(self.steps)
        
    def hide(self):
        self.visible = False

class GraphNode:
    def __init__(self, word: str, x: float, y: float):
        self.word = word
        self.x = x
        self.y = y
        self.target_x = x
        self.target_y = y
        self.scale = 1.0
        self.hover = False
        self.pulse = 0
        
    def update(self):
        self.x += (self.target_x - self.x) * 0.1
        self.y += (self.target_y - self.y) * 0.1
        target_scale = HOVER_SCALE if self.hover else 1.0
        self.scale += (target_scale - self.scale) * ANIMATION_SPEED
        self.pulse = (self.pulse + 0.1) % (2 * math.pi)
        
    def draw(self, screen: pygame.Surface, is_current: bool, is_target: bool):
        # Calculate scaled dimensions
        pulse_scale = 1.0 + 0.1 * math.sin(self.pulse) if is_current else 1.0
        scaled_radius = int(NODE_RADIUS * self.scale * pulse_scale)
        
        # Draw glow effect for current/target nodes
        if is_current or is_target:
            glow_radius = scaled_radius + 10
            glow_color = SUCCESS_COLOR if is_target else PRIMARY_COLOR
            glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
            for r in range(5):
                alpha = 50 - r * 10
                pygame.draw.circle(glow_surface, (*glow_color, alpha), 
                                (glow_radius, glow_radius), glow_radius - r)
            screen.blit(glow_surface, 
                       (self.x - glow_radius, self.y - glow_radius))
        
        # Draw shadow
        shadow_pos = (int(self.x), int(self.y + 3))
        pygame.draw.circle(screen, (*BLACK, 30), shadow_pos, scaled_radius)
        
        # Draw node
        color = SUCCESS_COLOR if is_target else PRIMARY_COLOR if is_current else SECONDARY_COLOR
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), scaled_radius)
        
        # Draw highlight effect
        highlight = pygame.Surface((scaled_radius * 2, scaled_radius), pygame.SRCALPHA)
        pygame.draw.ellipse(highlight, (255, 255, 255, 30), highlight.get_rect())
        screen.blit(highlight, (self.x - scaled_radius, self.y - scaled_radius))
        
        # Draw text with shadow
        font = pygame.font.Font(None, int(24 * self.scale * pulse_scale))
        shadow_text = font.render(self.word, True, (*BLACK, 128))
        text = font.render(self.word, True, WHITE)
        
        shadow_rect = shadow_text.get_rect(center=(self.x + 1, self.y + 1))
        text_rect = text.get_rect(center=(self.x, self.y))
        
        screen.blit(shadow_text, shadow_rect)
        screen.blit(text, text_rect)

class WordGraph:
    def __init__(self):
        self.nodes: Dict[str, GraphNode] = {}
        self.edges: List[Tuple[str, str]] = []
        
    def update_layout(self, path: List[str]):
        # Create nodes for each word in the path
        num_nodes = len(path)
        for i, word in enumerate(path):
            angle = 2 * math.pi * i / num_nodes
            x = GRAPH_CENTER_X + math.cos(angle) * NODE_SPACING * 2
            y = GRAPH_CENTER_Y + math.sin(angle) * NODE_SPACING
            
            if word not in self.nodes:
                self.nodes[word] = GraphNode(word, x, y)
            else:
                self.nodes[word].target_x = x
                self.nodes[word].target_y = y
                
        # Create edges between consecutive words
        self.edges = list(zip(path[:-1], path[1:]))
        
    def draw(self, screen: pygame.Surface, current_word: str, target_word: str):
        # Draw edges with animated gradient effect
        for start_word, end_word in self.edges:
            start_node = self.nodes[start_word]
            end_node = self.nodes[end_word]
            
            # Create animated gradient line
            steps = 15
            t_offset = (pygame.time.get_ticks() % 1000) / 1000.0
            
            for i in range(steps):
                t = (i / (steps - 1) + t_offset) % 1.0
                x1 = start_node.x + (end_node.x - start_node.x) * t
                y1 = start_node.y + (end_node.y - start_node.y) * t
                x2 = start_node.x + (end_node.x - start_node.x) * ((t + 0.1) % 1.0)
                y2 = start_node.y + (end_node.y - start_node.y) * ((t + 0.1) % 1.0)
                
                alpha = int(255 * (1 - abs(t - 0.5) * 2))
                pygame.draw.line(screen, (*PRIMARY_COLOR, alpha), (x1, y1), (x2, y2), 3)
        
        # Draw nodes
        for word, node in self.nodes.items():
            node.update()
            node.draw(screen, word == current_word, word == target_word)

class AnimatedButton:
    def __init__(self, x: int, y: int, width: int, height: int, text: str, color: Tuple[int, int, int]):
        self.original_rect = pygame.Rect(x, y, width, height)
        self.rect = self.original_rect.copy()
        self.text = text
        self.color = color
        self.hover = False
        self.scale = 1.0
        self.animation_progress = 0
        self.click_animation = 0
        
    def draw(self, screen: pygame.Surface):
        target_scale = HOVER_SCALE if self.hover else 1.0
        self.scale += (target_scale - self.scale) * ANIMATION_SPEED
        
        if self.click_animation > 0:
            self.click_animation = max(0, self.click_animation - 0.1)
            self.scale = 1.0 - self.click_animation * 0.1
        
        # Calculate scaled dimensions
        scaled_width = int(self.original_rect.width * self.scale)
        scaled_height = int(self.original_rect.height * self.scale)
        x = self.original_rect.centerx - scaled_width // 2
        y = self.original_rect.centery - scaled_height // 2
        
        self.rect = pygame.Rect(x, y, scaled_width, scaled_height)
        
        # Draw button with shadow and glow
        shadow_rect = self.rect.copy()
        shadow_rect.y += 3
        pygame.draw.rect(screen, (*BLACK, 30), shadow_rect, border_radius=12)
        
        if self.hover:
            glow_rect = self.rect.copy()
            glow_rect.inflate_ip(4, 4)
            pygame.draw.rect(screen, (*self.color, 100), glow_rect, border_radius=12)
        
        # Draw main button with gradient
        color = tuple(min(c + 20, 255) for c in self.color) if self.hover else self.color
        pygame.draw.rect(screen, color, self.rect, border_radius=12)
        
        gradient_rect = self.rect.copy()
        gradient_rect.height = self.rect.height // 2
        gradient = pygame.Surface((gradient_rect.width, gradient_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(gradient, (255, 255, 255, 30), gradient.get_rect(), border_radius=12)
        screen.blit(gradient, gradient_rect)
        
        # Draw text with shadow and scale animation
        font = pygame.font.Font(None, int(32 * self.scale))
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
                self.click_animation = 1.0
                return True
        return False

class DifficultyButton(AnimatedButton):
    def __init__(self, x: int, y: int, width: int, height: int, text: str, color: Tuple[int, int, int], description: str):
        super().__init__(x, y, width, height, text, color)
        self.description = description
        
    def draw(self, screen: pygame.Surface, selected: bool = False):
        super().draw(screen)
        
        if self.hover or selected:
            # Draw description tooltip
            font = pygame.font.Font(None, 24)
            desc_surface = font.render(self.description, True, BLACK)
            padding = 10
            tooltip = pygame.Surface((desc_surface.get_width() + padding * 2, 
                                    desc_surface.get_height() + padding * 2), 
                                   pygame.SRCALPHA)
            pygame.draw.rect(tooltip, (*WHITE, 230), tooltip.get_rect(), border_radius=8)
            tooltip.blit(desc_surface, (padding, padding))
            
            # Position tooltip above button
            tooltip_x = self.rect.centerx - tooltip.get_width() // 2
            tooltip_y = self.rect.top - tooltip.get_height() - 5
            screen.blit(tooltip, (tooltip_x, tooltip_y))
            
            if selected:
                # Draw selection indicator
                pygame.draw.rect(screen, SUCCESS_COLOR, self.rect, 3, border_radius=12)

class ModernInputBox:
    def __init__(self, x: int, y: int, width: int, height: int):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = ''
        self.active = False
        self.animation_progress = 0
        self.error = False
        self.error_shake = 0
        self.cursor_visible = True
        self.cursor_timer = 0
        
    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        if event.type == pygame.MOUSEBUTTONDOWN:
            was_active = self.active
            self.active = self.rect.collidepoint(event.pos)
            if self.active and not was_active:
                self.animation_progress = 0
            
        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                if self.text:
                    text = self.text.lower()
                    self.text = ''
                    return text
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.unicode in string.ascii_letters and len(self.text) < 6:
                self.text += event.unicode
        return None
        
    def show_error(self):
        self.error = True
        self.error_shake = 1.0
        
    def draw(self, screen: pygame.Surface):
        # Update animations
        if self.error_shake > 0:
            self.error_shake = max(0, self.error_shake - 0.1)
            
        self.cursor_timer = (self.cursor_timer + 1) % 30
        self.cursor_visible = self.cursor_timer < 15
        
        # Calculate shake offset
        shake_offset = math.sin(self.error_shake * 10) * 5 * self.error_shake
        
        # Draw input box background with error state
        box_rect = self.rect.copy()
        box_rect.x += shake_offset
        pygame.draw.rect(screen, LIGHT_GRAY, box_rect, border_radius=12)
        
        # Animated border
        if self.active:
            self.animation_progress = min(1, self.animation_progress + ANIMATION_SPEED)
        else:
            self.animation_progress = max(0, self.animation_progress - ANIMATION_SPEED)
            
        border_color = ERROR_COLOR if self.error else tuple(
            int(a + (b - a) * self.animation_progress) 
            for a, b in zip(GRAY, PRIMARY_COLOR)
        )
        pygame.draw.rect(screen, border_color, box_rect, 2, border_radius=12)
        
        # Draw text with cursor
        font = pygame.font.Font(None, 32)
        if self.text:
            text_surface = font.render(self.text, True, BLACK)
            text_rect = text_surface.get_rect(center=box_rect.center)
            screen.blit(text_surface, text_rect)
            
            # Draw cursor
            if self.active and self.cursor_visible:
                cursor_x = text_rect.right + 2
                cursor_height = text_surface.get_height()
                pygame.draw.line(screen, BLACK,
                               (cursor_x, box_rect.centery - cursor_height//2),
                               (cursor_x, box_rect.centery + cursor_height//2), 2)
        else:
            text_surface = font.render("Type a word...", True, GRAY)
            text_rect = text_surface.get_rect(center=box_rect.center)
            screen.blit(text_surface, text_rect)

class WordLadderGUI:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Word Ladder - An Elegant Word Game")
        
        self.game = WordLadderGame()
        self.game_state = None
        self.animation_time = 0
        self.word_graph = WordGraph()
        self.tutorial = Tutorial()
        self.selected_difficulty = 'BEGINNER'
        
        # Create UI elements
        center_x = WINDOW_WIDTH // 2
        self.input_box = ModernInputBox(center_x - INPUT_WIDTH//2, 
                                      WINDOW_HEIGHT//2 + 50, 
                                      INPUT_WIDTH, 
                                      INPUT_HEIGHT)
        
        # Create difficulty buttons
        difficulty_y = WINDOW_HEIGHT//4
        difficulty_spacing = BUTTON_WIDTH + PADDING
        self.difficulty_buttons = {
            'BEGINNER': DifficultyButton(
                center_x - difficulty_spacing - BUTTON_WIDTH//2,
                difficulty_y,
                BUTTON_WIDTH,
                BUTTON_HEIGHT,
                "Beginner",
                (46, 213, 115),  # Green
                "3-4 letter words, 5 moves"
            ),
            'ADVANCED': DifficultyButton(
                center_x - BUTTON_WIDTH//2,
                difficulty_y,
                BUTTON_WIDTH,
                BUTTON_HEIGHT,
                "Advanced",
                (255, 165, 0),  # Orange
                "4-5 letter words, 7 moves"
            ),
            'CHALLENGE': DifficultyButton(
                center_x + difficulty_spacing - BUTTON_WIDTH//2,
                difficulty_y,
                BUTTON_WIDTH,
                BUTTON_HEIGHT,
                "Challenge",
                (255, 71, 87),  # Red
                "5-6 letter words, 10 moves"
            )
        }
        
        button_y = WINDOW_HEIGHT - BUTTON_HEIGHT - PADDING
        self.buttons = {
            'start': AnimatedButton(center_x - BUTTON_WIDTH - PADDING, 
                                  button_y,
                                  BUTTON_WIDTH, 
                                  BUTTON_HEIGHT, 
                                  "New Game", 
                                  PRIMARY_COLOR),
            'hint': AnimatedButton(center_x + PADDING, 
                                 button_y,
                                 BUTTON_WIDTH, 
                                 BUTTON_HEIGHT, 
                                 "Get Hint", 
                                 SECONDARY_COLOR)
        }
        
        self.message = ""
        self.message_color = BLACK
        self.message_animation = 0
        self.score = 0
        self.high_score = 0
        
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
        
        # Draw difficulty buttons
        for diff, button in self.difficulty_buttons.items():
            button.draw(self.screen, diff == self.selected_difficulty)
        
        if self.game_state:
            # Draw word graph
            self.word_graph.update_layout(self.game_state['path'])
            self.word_graph.draw(self.screen, 
                               self.game_state['current_word'],
                               self.game_state['target_word'])
            
            # Draw game info with modern styling
            info_panel = pygame.Surface((300, 200), pygame.SRCALPHA)
            pygame.draw.rect(info_panel, (*WHITE, 200), info_panel.get_rect(), border_radius=15)
            
            # Add decorative header
            pygame.draw.rect(info_panel, PRIMARY_COLOR, 
                           (0, 0, 300, 40), border_radius=15)
            pygame.draw.rect(info_panel, PRIMARY_COLOR, 
                           (0, 20, 300, 20))
            
            font = pygame.font.Font(None, 36)
            
            # Header text
            header = font.render("Game Info", True, WHITE)
            header_rect = header.get_rect(centerx=150, y=10)
            info_panel.blit(header, header_rect)
            
            # Game stats
            y_offset = 50
            for label, value in [
                ("Difficulty:", self.selected_difficulty.capitalize()),
                ("Start Word:", self.game_state['start_word']),
                ("Target Word:", self.game_state['target_word']),
                ("Moves:", f"{self.game_state['moves']}/{self.game_state['max_moves']}"),
                ("Score:", str(self.score)),
                ("High Score:", str(self.high_score))
            ]:
                text = font.render(f"{label} {value}", True, BLACK)
                info_panel.blit(text, (20, y_offset))
                y_offset += 30
            
            self.screen.blit(info_panel, (PADDING, 100))
            
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
            
        # Draw tutorial
        self.tutorial.draw(self.screen)
            
        pygame.display.flip()
        
    def show_message(self, text: str, color: Tuple[int, int, int]):
        self.message = text
        self.message_color = color
        self.message_animation = 0
        
    def update_score(self):
        if self.game_state['status'] == 'WON':
            moves_bonus = self.game_state['max_moves'] - self.game_state['moves']
            self.score = max(0, moves_bonus * 100)
            self.high_score = max(self.high_score, self.score)
        
    def run(self):
        clock = pygame.time.Clock()
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # Handle difficulty selection
                    for diff, button in self.difficulty_buttons.items():
                        if button.handle_event(event):
                            self.selected_difficulty = diff
                            if self.game_state:
                                self.show_message(f"Difficulty changed to {diff}", PRIMARY_COLOR)
                    
                    # Advance tutorial
                    if self.tutorial.visible:
                        self.tutorial.next_step()
                    
                # Handle button events
                if self.buttons['start'].handle_event(event):
                    self.game_state = self.game.start_game(self.selected_difficulty)
                    self.show_message(f"Game started in {self.selected_difficulty} mode! Enter your word", BLACK)
                    self.tutorial.hide()
                    
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
                        self.input_box.show_error()
                    else:
                        try:
                            self.game_state = self.game.make_move(word)
                            if self.game_state['status'] == 'WON':
                                self.update_score()
                                self.show_message(f"Congratulations! Score: {self.score}", SUCCESS_COLOR)
                            elif self.game_state['status'] == 'LOST':
                                self.show_message("Game Over! Try again!", ERROR_COLOR)
                        except ValueError as e:
                            self.show_message(str(e), ERROR_COLOR)
                            self.input_box.show_error()
                
                # Update hover states for difficulty buttons
                for button in self.difficulty_buttons.values():
                    button.handle_event(event)
            
            self.draw()
            clock.tick(60)
            
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    gui = WordLadderGUI()
    gui.run()