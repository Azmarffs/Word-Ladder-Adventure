import pygame
import sys
import random
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
ALGORITHM_COLORS = {
    'bfs': (52, 152, 219),  # Blue
    'ucs': (155, 89, 182),  # Purple
    'a_star': (231, 76, 60)  # Red
}

# Menu States
MENU_STATE_MAIN = "MAIN"
MENU_STATE_GAME = "GAME"
MENU_STATE_HELP = "HELP"
MENU_STATE_CUSTOM = "CUSTOM"
MENU_STATE_ALGORITHM = "ALGORITHM"

# Animation constants
NODE_RADIUS = 30
NODE_SPACING = 100
GRAPH_CENTER_X = WINDOW_WIDTH // 2
GRAPH_CENTER_Y = WINDOW_HEIGHT // 2
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

class MenuButton(AnimatedButton):
    def __init__(self, x: int, y: int, width: int, height: int, text: str, color: Tuple[int, int, int], icon: str = None):
        super().__init__(x, y, width, height, text, color)
        self.icon = icon
        self.pulse = 0
        
    def draw(self, screen: pygame.Surface):
        self.pulse = (self.pulse + 0.05) % (2 * math.pi)
        pulse_scale = 1.0 + 0.02 * math.sin(self.pulse) if self.hover else 1.0
        
        # Calculate scaled dimensions with pulse effect
        scaled_width = int(self.original_rect.width * self.scale * pulse_scale)
        scaled_height = int(self.original_rect.height * self.scale * pulse_scale)
        x = self.original_rect.centerx - scaled_width // 2
        y = self.original_rect.centery - scaled_height // 2
        
        self.rect = pygame.Rect(x, y, scaled_width, scaled_height)
        
        # Draw glowing effect when hovered
        if self.hover:
            glow_surface = pygame.Surface((scaled_width + 20, scaled_height + 20), pygame.SRCALPHA)
            for i in range(10):
                alpha = 25 - i * 2
                pygame.draw.rect(glow_surface, (*self.color, alpha),
                               (i, i, scaled_width + 20 - 2*i, scaled_height + 20 - 2*i),
                               border_radius=15)
            screen.blit(glow_surface, (x - 10, y - 10))
        
        # Draw button background with gradient
        pygame.draw.rect(screen, self.color, self.rect, border_radius=12)
        gradient_rect = self.rect.copy()
        gradient_rect.height = self.rect.height // 2
        gradient = pygame.Surface((gradient_rect.width, gradient_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(gradient, (255, 255, 255, 30), gradient.get_rect(), border_radius=12)
        screen.blit(gradient, gradient_rect)
        
        # Draw icon if provided
        if self.icon:
            icon_font = pygame.font.Font(None, int(36 * self.scale * pulse_scale))
            icon_surface = icon_font.render(self.icon, True, WHITE)
            icon_rect = icon_surface.get_rect(
                centery=self.rect.centery,
                x=self.rect.x + 20
            )
            screen.blit(icon_surface, icon_rect)
            
            # Draw text with offset for icon
            font = pygame.font.Font(None, int(32 * self.scale * pulse_scale))
            text_surface = font.render(self.text, True, WHITE)
            text_rect = text_surface.get_rect(
                centery=self.rect.centery,
                x=icon_rect.right + 10
            )
            screen.blit(text_surface, text_rect)
        else:
            # Draw centered text
            font = pygame.font.Font(None, int(32 * self.scale * pulse_scale))
            text_surface = font.render(self.text, True, WHITE)
            text_rect = text_surface.get_rect(center=self.rect.center)
            screen.blit(text_surface, text_rect)

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
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
            if self.rect.collidepoint(event.pos):
                self.click_animation = 1.0
                return True
        return False

class AlgorithmButton(AnimatedButton):
    def __init__(self, x: int, y: int, width: int, height: int, text: str, color: Tuple[int, int, int], description: str):
        super().__init__(x, y, width, height, text, color)
        self.description = description
        
    def draw(self, screen: pygame.Surface, selected: bool = False):
        super().draw(screen)
        
        if self.hover or selected:
            # Draw description tooltip
            font = pygame.font.Font(None, 24)
            desc_lines = self.description.split('\n')
            desc_surfaces = [font.render(line, True, BLACK) for line in desc_lines]
            
            # Calculate tooltip dimensions
            max_width = max(surface.get_width() for surface in desc_surfaces)
            total_height = sum(surface.get_height() for surface in desc_surfaces)
            
            padding = 10
            tooltip = pygame.Surface((max_width + padding * 2, 
                                    total_height + padding * 2 + (len(desc_lines) - 1) * 5), 
                                   pygame.SRCALPHA)
            pygame.draw.rect(tooltip, (*WHITE, 230), tooltip.get_rect(), border_radius=8)
            
            # Draw each line
            y_offset = padding
            for surface in desc_surfaces:
                tooltip.blit(surface, (padding, y_offset))
                y_offset += surface.get_height() + 5
            
            # Position tooltip above button
            tooltip_x = self.rect.centerx - tooltip.get_width() // 2
            tooltip_y = self.rect.top - tooltip.get_height() - 5
            screen.blit(tooltip, (tooltip_x, tooltip_y))
            
            if selected:
                # Draw selection indicator
                pygame.draw.rect(screen, SUCCESS_COLOR, self.rect, 3, border_radius=12)

class ModernInputBox:
    def __init__(self, x: int, y: int, width: int, height: int, max_length: int = 6, placeholder: str = "Type a word..."):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = ''
        self.active = False
        self.animation_progress = 0
        self.error = False
        self.error_shake = 0
        self.cursor_visible = True
        self.cursor_timer = 0
        self.max_length = max_length
        self.placeholder = placeholder
        
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
            elif event.unicode in string.ascii_letters and len(self.text) < self.max_length:
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
            text_surface = font.render(self.placeholder, True, GRAY)
            text_rect = text_surface.get_rect(center=box_rect.center)
            screen.blit(text_surface, text_rect)

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
        self.label = None
        
    def update(self):
        self.x += (self.target_x - self.x) * 0.1
        self.y += (self.target_y - self.y) * 0.1
        target_scale = HOVER_SCALE if self.hover else 1.0
        self.scale += (target_scale - self.scale) * ANIMATION_SPEED
        self.pulse = (self.pulse + 0.1) % (2 * math.pi)
        
    def draw(self, screen: pygame.Surface, is_current: bool, is_target: bool, is_optimal_path: bool = False):
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
        if is_optimal_path and not (is_current or is_target):
            # Highlight nodes in the optimal path
            color = (255, 193, 7)  # Amber color for optimal path
            
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
        
        # Draw label if exists
        if self.label:
            label_font = pygame.font.Font(None, int(18 * self.scale))
            label_surface = label_font.render(self.label, True, BLACK)
            label_bg = pygame.Surface((label_surface.get_width() + 10, label_surface.get_height() + 6), pygame.SRCALPHA)
            pygame.draw.rect(label_bg, (255, 255, 255, 200), label_bg.get_rect(), border_radius=8)
            label_bg.blit(label_surface, (5, 3))
            
            # Position label above node
            label_x = self.x - label_bg.get_width() // 2
            label_y = self.y - scaled_radius - label_bg.get_height() - 5
            screen.blit(label_bg, (label_x, label_y))

class WordGraph:
    def __init__(self):
        self.nodes: Dict[str, GraphNode] = {}
        self.edges: List[Tuple[str, str]] = []
        self.optimal_path: List[str] = []
        
    def update_layout(self, path: List[str], optimal_path: List[str] = None):
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
        
        # Store optimal path if provided
        self.optimal_path = optimal_path or []
        
        # Add labels to nodes in optimal path
        if optimal_path:
            for i, word in enumerate(optimal_path):
                if word in self.nodes:
                    self.nodes[word].label = f"Step {i+1}"
        
    def draw(self, screen: pygame.Surface, current_word: str, target_word: str):
        # Draw edges with animated gradient effect
        for start_word, end_word in self.edges:
            start_node = self.nodes[start_word]
            end_node = self.nodes[end_word]
            
            # Determine if this edge is part of the optimal path
            is_optimal_edge = False
            if self.optimal_path and len(self.optimal_path) > 1:
                for i in range(len(self.optimal_path) - 1):
                    if (self.optimal_path[i] == start_word and 
                        self.optimal_path[i+1] == end_word):
                        is_optimal_edge = True
                        break
            
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
                edge_color = (255, 193, 7) if is_optimal_edge else PRIMARY_COLOR  # Amber for optimal path
                pygame.draw.line(screen, (*edge_color, alpha), (x1, y1), (x2, y2), 3)
        
        # Draw nodes
        for word, node in self.nodes.items():
            node.update()
            is_in_optimal = word in self.optimal_path
            node.draw(screen, word == current_word, word == target_word, is_in_optimal)

class CustomGameMenu:
    def __init__(self, game: WordLadderGame):
        self.game = game
        center_x = WINDOW_WIDTH // 2
        
        self.back_button = MenuButton(
            PADDING,
            PADDING,
            BUTTON_WIDTH,
            BUTTON_HEIGHT,
            "Back to Menu",
            SECONDARY_COLOR,
            "←"
        )
        
        self.start_input = ModernInputBox(
            center_x - INPUT_WIDTH - 20,
            WINDOW_HEIGHT // 2 - 50,
            INPUT_WIDTH,
            INPUT_HEIGHT,
            6,
            "Start word..."
        )
        
        self.target_input = ModernInputBox(
            center_x + 20,
            WINDOW_HEIGHT // 2 - 50,
            INPUT_WIDTH,
            INPUT_HEIGHT,
            6,
            "Target word..."
        )
        
        self.start_button = AnimatedButton(
            center_x - BUTTON_WIDTH // 2,
            WINDOW_HEIGHT // 2 + 50,
            BUTTON_WIDTH,
            BUTTON_HEIGHT,
            "Start Game",
            SUCCESS_COLOR
        )
        
        self.message = ""
        self.message_color = BLACK
        self.message_animation = 0
        
    def draw(self, screen: pygame.Surface):
        # Draw title
        font_title = pygame.font.Font(None, 64)
        title = font_title.render("Custom Word Ladder", True, PRIMARY_COLOR)
        title_rect = title.get_rect(centerx=WINDOW_WIDTH//2, y=100)
        screen.blit(title, title_rect)
        
        # Draw subtitle
        font_subtitle = pygame.font.Font(None, 32)
        subtitle = font_subtitle.render("Enter two words of the same length", True, SECONDARY_COLOR)
        subtitle_rect = subtitle.get_rect(centerx=WINDOW_WIDTH//2, y=title_rect.bottom + 20)
        screen.blit(subtitle, subtitle_rect)
        
        # Draw input labels
        font_label = pygame.font.Font(None, 28)
        start_label = font_label.render("Start Word:", True, BLACK)
        target_label = font_label.render("Target Word:", True, BLACK)
        
        screen.blit(start_label, (self.start_input.rect.x, self.start_input.rect.y - 30))
        screen.blit(target_label, (self.target_input.rect.x, self.target_input.rect.y - 30))
        
        # Draw input boxes and buttons
        self.start_input.draw(screen)
        self.target_input.draw(screen)
        self.start_button.draw(screen)
        self.back_button.draw(screen)
        
        # Draw message
        if self.message:
            if self.message_animation < 1:
                self.message_animation = min(1, self.message_animation + 0.05)
            message_surface = font_subtitle.render(self.message, True, self.message_color)
            message_surface.set_alpha(int(255 * self.message_animation))
            message_rect = message_surface.get_rect(
                centerx=WINDOW_WIDTH//2,
                y=self.start_button.rect.bottom + 40
            )
            screen.blit(message_surface, message_rect)
            
    def show_message(self, text: str, color: Tuple[int, int, int]):
        self.message = text
        self.message_color = color
        self.message_animation = 0
        
    def handle_event(self, event: pygame.event.Event) -> Tuple[Optional[str], Optional[Tuple[str, str]]]:
        self.start_input.handle_event(event)
        self.target_input.handle_event(event)
        
        if self.back_button.handle_event(event):
            return MENU_STATE_MAIN, None
            
        if self.start_button.handle_event(event):
            start_word = self.start_input.text.lower()
            target_word = self.target_input.text.lower()
            
            if not start_word or not target_word:
                self.show_message("Please enter both words", ERROR_COLOR)
                return None, None
                
            if len(start_word) != len(target_word):
                self.show_message("Words must be the same length", ERROR_COLOR)
                return None, None
                
            try:
                # Check if words are valid and a path exists
                if self.game.word_ladder.check_valid_word_pair(start_word, target_word):
                    return MENU_STATE_GAME, (start_word, target_word)
                else:
                    self.show_message("No valid path exists between these words", ERROR_COLOR)
            except ValueError as e:
                self.show_message(str(e), ERROR_COLOR)
                
        return None, None

class AlgorithmMenu:
    def __init__(self, game: WordLadderGame):
        self.game = game
        center_x = WINDOW_WIDTH // 2
        button_y = WINDOW_HEIGHT // 2 - 100
        button_spacing = 80
        
        self.back_button = MenuButton(
            PADDING,
            PADDING,
            BUTTON_WIDTH,
            BUTTON_HEIGHT,
            "Back to Game",
            SECONDARY_COLOR,
            "←"
        )
        
        self.algorithm_buttons = {
            'bfs': AlgorithmButton(
                center_x - BUTTON_WIDTH//2,
                button_y,
                BUTTON_WIDTH,
                BUTTON_HEIGHT,
                "BFS",
                ALGORITHM_COLORS['bfs'],
                "Breadth-First Search\nFinds the shortest path\nFast but uses more memory"
            ),
            'ucs': AlgorithmButton(
                center_x - BUTTON_WIDTH//2,
                button_y + button_spacing,
                BUTTON_WIDTH,
                BUTTON_HEIGHT,
                "UCS",
                ALGORITHM_COLORS['ucs'],
                "Uniform Cost Search\nOptimal for equal step costs\nMore efficient than BFS"
            ),
            'a_star': AlgorithmButton(
                center_x - BUTTON_WIDTH//2,
                button_y + button_spacing * 2,
                BUTTON_WIDTH,
                BUTTON_HEIGHT,
                "A*",
                ALGORITHM_COLORS['a_star'],
                "A* Search\nUses heuristics to find optimal path\nMost efficient algorithm"
            )
        }
        
    def draw(self, screen: pygame.Surface):
        # Draw title
        font_title = pygame.font.Font(None, 64)
        title = font_title.render("Select Hint Algorithm", True, PRIMARY_COLOR)
        title_rect = title.get_rect(centerx=WINDOW_WIDTH//2, y=100)
        screen.blit(title, title_rect)
        
        # Draw buttons
        for alg, button in self.algorithm_buttons.items():
            button.draw(screen, alg == self.game.hint_algorithm)
            
        self.back_button.draw(screen)
        
    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        if self.back_button.handle_event(event):
            return MENU_STATE_GAME
            
        for alg, button in self.algorithm_buttons.items():
            if button.handle_event(event):
                self.game.set_hint_algorithm(alg)
                return MENU_STATE_GAME
                
        return None

class MainMenu:
    def __init__(self):
        center_x = WINDOW_WIDTH // 2
        button_spacing = 80
        start_y = WINDOW_HEIGHT // 2 - 100
        
        self.buttons = {
            'play': MenuButton(
                center_x - BUTTON_WIDTH//2,
                start_y,
                BUTTON_WIDTH,
                BUTTON_HEIGHT,
                "Play Game",
                PRIMARY_COLOR,
                "▶"
            ),
            'custom': MenuButton(
                center_x - BUTTON_WIDTH//2,
                start_y + button_spacing,
                BUTTON_WIDTH,
                BUTTON_HEIGHT,
                "Custom Game",
                (52, 152, 219),  # Blue
                "✎"
            ),
            'help': MenuButton(
                center_x - BUTTON_WIDTH//2,
                start_y + button_spacing * 2,
                BUTTON_WIDTH,
                BUTTON_HEIGHT,
                "How to Play",
                SECONDARY_COLOR,
                "?"
            ),
            'quit': MenuButton(
                center_x - BUTTON_WIDTH//2,
                start_y + button_spacing * 3,
                BUTTON_WIDTH,
                BUTTON_HEIGHT,
                "Quit Game",
                ERROR_COLOR,
                "✕"
            )
        }
        
        self.title_animation = 0
        self.particles = [(random.random() * WINDOW_WIDTH,
                          random.random() * WINDOW_HEIGHT,
                          random.random() * 2 * math.pi) for _ in range(50)]
        
    def draw(self, screen: pygame.Surface):
        # Draw animated background particles
        for i, (x, y, angle) in enumerate(self.particles):
            size = 3 + 2 * math.sin(self.title_animation + i * 0.1)
            alpha = int(128 + 64 * math.sin(self.title_animation + i * 0.2))
            particle_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            pygame.draw.circle(particle_surface, (*PRIMARY_COLOR, alpha), (size, size), size)
            screen.blit(particle_surface, (x, y))
            
            # Update particle position
            self.particles[i] = ((x + math.cos(angle) * 0.5) % WINDOW_WIDTH,
                               (y + math.sin(angle) * 0.5) % WINDOW_HEIGHT,
                               angle)
        
        # Draw animated title
        self.title_animation += 0.05
        title_scale = 1 + 0.05 * math.sin(self.title_animation)
        font_title = pygame.font.Font(None, int(100 * title_scale))
        title = font_title.render("Word Ladder", True, PRIMARY_COLOR)
        title_rect = title.get_rect(centerx=WINDOW_WIDTH//2, y=150)
        screen.blit(title, title_rect)
        
        # Draw subtitle
        font_subtitle = pygame.font.Font(None, 36)
        subtitle = font_subtitle.render("An Elegant Word Game", True, SECONDARY_COLOR)
        subtitle_rect = subtitle.get_rect(centerx=WINDOW_WIDTH//2, y=title_rect.bottom + 20)
        screen.blit(subtitle, subtitle_rect)
        
        # Draw buttons
        for button in self.buttons.values():
            button.draw(screen)
            
    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        for name, button in self.buttons.items():
            if button.handle_event(event):
                if name == 'play':
                    return MENU_STATE_GAME
                elif name == 'custom':
                    return MENU_STATE_CUSTOM
                elif name == 'help':
                    return MENU_STATE_HELP
                elif name == 'quit':
                    pygame.quit()
                    sys.exit()
        return None

class HelpMenu:
    def __init__(self):
        self.back_button = MenuButton(
            PADDING,
            PADDING,
            BUTTON_WIDTH,
            BUTTON_HEIGHT,
            "Back to Menu",
            SECONDARY_COLOR,
            "←"
        )
        
        self.scroll_offset = 0
        self.target_scroll = 0
        self.rules = [
            ("Objective", "Transform one word into another by changing one letter at a time."),
            ("Rules", "• Each word must be a valid English word\n• Only one letter can be changed at a time\n• Complete the transformation within the move limit"),
            ("Difficulty Levels", "• Beginner: 3-4 letter words, 5 moves\n• Advanced: 4-5 letter words, 7 moves\n• Challenge: 5-6 letter words, 10 moves with obstacles"),
            ("Obstacles", "In Challenge mode, you may encounter:\n• Banned words that cannot be used\n• Restricted letters that cannot appear in your words"),
            ("Algorithms", "You can choose different algorithms for hints:\n• BFS: Breadth-First Search finds shortest paths\n• UCS: Uniform Cost Search is optimal for equal costs\n• A*: A-Star uses heuristics for efficiency"),
            ("Custom Games", "Create your own word ladder by entering:\n• A starting word\n• A target word of the same length\nThe game will verify if a valid path exists."),
            ("Scoring", "• Points are awarded based on remaining moves\n• Bonus points for completing in fewer moves\n• Try to beat your high score!")
        ]
        
    def draw(self, screen: pygame.Surface):
        # Smooth scrolling
        self.scroll_offset += (self.target_scroll - self.scroll_offset) * 0.1
        
        # Draw help content
        content_surface = pygame.Surface((WINDOW_WIDTH - 2*PADDING, WINDOW_HEIGHT - 2*PADDING), pygame.SRCALPHA)
        y_offset = -int(self.scroll_offset)
        
        for title, text in self.rules:
            # Draw section title
            font_title = pygame.font.Font(None, 48)
            title_surface = font_title.render(title, True, PRIMARY_COLOR)
            title_rect = title_surface.get_rect(x=0, y=y_offset)
            content_surface.blit(title_surface, title_rect)
            
            # Draw section content
            font_content = pygame.font.Font(None, 32)
            y_offset += 60
            for line in text.split('\n'):
                text_surface = font_content.render(line, True, BLACK)
                text_rect = text_surface.get_rect(x=20, y=y_offset)
                content_surface.blit(text_surface, text_rect)
                y_offset += 40
            
            y_offset += 40
        
        screen.blit(content_surface, (PADDING, PADDING + BUTTON_HEIGHT + PADDING))
        
        # Draw back button
        self.back_button.draw(screen)
        
    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        if event.type == pygame.MOUSEWHEEL:
            self.target_scroll = max(0, min(self.target_scroll - event.y * 30, 400))
        
        if self.back_button.handle_event(event):
            return MENU_STATE_MAIN
        return None

class WordLadderGUI:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Word Ladder - An Elegant Word Game")
        
        self.game = WordLadderGame()
        self.game_state = None
        self.animation_time = 0
        self.word_graph = WordGraph()
        self.menu_state = MENU_STATE_MAIN
        self.main_menu = MainMenu()
        self.help_menu = HelpMenu()
        self.custom_menu = CustomGameMenu(self.game)
        self.algorithm_menu = AlgorithmMenu(self.game)
        self.selected_difficulty = None
        
        # Create UI elements
        center_x = WINDOW_WIDTH // 2
        
        # Create difficulty buttons
        difficulty_y = WINDOW_HEIGHT//2 - 100
        self.difficulty_buttons = {
            'BEGINNER': DifficultyButton(
                center_x - BUTTON_WIDTH//2,
                difficulty_y,
                BUTTON_WIDTH,
                BUTTON_HEIGHT,
                "Beginner",
                (46, 213, 115),  # Green
                "3-4 letter words, 5 moves"
            ),
            'ADVANCED': DifficultyButton(
                center_x - BUTTON_WIDTH//2,
                difficulty_y + BUTTON_HEIGHT + 30,
                BUTTON_WIDTH,
                BUTTON_HEIGHT,
                "Advanced",
                (255, 165, 0),  # Orange
                "4-5 letter words, 7 moves"
            ),
            'CHALLENGE': DifficultyButton(
                center_x - BUTTON_WIDTH//2,
                difficulty_y + (BUTTON_HEIGHT + 30) * 2,
                BUTTON_WIDTH,
                BUTTON_HEIGHT,
                "Challenge",
                (255, 71, 87),  # Red
                "5-6 letter words, 10 moves with obstacles"
            )
        }
        
        self.input_box = ModernInputBox(center_x - INPUT_WIDTH//2, 
                                      WINDOW_HEIGHT//2 + 50, 
                                      INPUT_WIDTH, 
                                      INPUT_HEIGHT)
        
        self.game_buttons = {
            'menu': MenuButton(PADDING, 
                             PADDING,
                             BUTTON_WIDTH, 
                             BUTTON_HEIGHT, 
                             "Main Menu", 
                             SECONDARY_COLOR,
                             "←"),
            'hint': AnimatedButton(center_x - BUTTON_WIDTH - 10, 
                                 WINDOW_HEIGHT - BUTTON_HEIGHT - PADDING,
                                 BUTTON_WIDTH, 
                                 BUTTON_HEIGHT, 
                                 "Get Hint", 
                                 SECONDARY_COLOR),
            'algorithm': AnimatedButton(center_x + 10, 
                                      WINDOW_HEIGHT - BUTTON_HEIGHT - PADDING,
                                      BUTTON_WIDTH, 
                                      BUTTON_HEIGHT, 
                                      "Algorithm", 
                                      PRIMARY_COLOR),
            'full_hint': AnimatedButton(center_x - BUTTON_WIDTH//2, 
                                      WINDOW_HEIGHT - BUTTON_HEIGHT*2 - PADDING*2,
                                      BUTTON_WIDTH, 
                                      BUTTON_HEIGHT, 
                                      "Show Path", 
                                      ALGORITHM_COLORS['a_star'])
        }
        
        self.message = ""
        self.message_color = BLACK
        self.message_animation = 0
        self.score = 0
        self.high_score = 0
        self.hint_detail_level = 'basic'
        self.optimal_path = None
        
    def draw(self):
        self.screen.fill(BACKGROUND_COLOR)
        self.animation_time += 0.02
        
        # Draw animated background
        for i in range(10):
            x = WINDOW_WIDTH * 0.1 * i
            y = WINDOW_HEIGHT * (0.5 + 0.2 * math.sin(self.animation_time + i * 0.5))
            radius = 20 + 10 * math.sin(self.animation_time * 2 + i)
            pygame.draw.circle(self.screen, (*PRIMARY_COLOR, 30), (int(x), int(y)), int(radius))
        
        if self.menu_state == MENU_STATE_MAIN:
            self.main_menu.draw(self.screen)
        elif self.menu_state == MENU_STATE_HELP:
            self.help_menu.draw(self.screen)
        elif self.menu_state == MENU_STATE_CUSTOM:
            self.custom_menu.draw(self.screen)
        elif self.menu_state == MENU_STATE_ALGORITHM:
            self.algorithm_menu.draw(self.screen)
        elif self.menu_state == MENU_STATE_GAME:
            if not self.game_state:
                # Draw difficulty selection screen
                font_title = pygame.font.Font(None, 64)
                title = font_title.render("Select Difficulty", True, PRIMARY_COLOR)
                title_rect = title.get_rect(centerx=WINDOW_WIDTH//2, y=100)
                self.screen.blit(title, title_rect)
                
                # Draw difficulty buttons
                for diff, button in self.difficulty_buttons.items():
                    button.draw(self.screen, diff == self.selected_difficulty)
                
                # Draw back button
                self.game_buttons['menu'].draw(self.screen)
            else:
                # Draw game screen
                self.word_graph.update_layout(self.game_state['path'], self.optimal_path)
                self.word_graph.draw(self.screen, 
                                   self.game_state['current_word'],
                                   self.game_state['target_word'])
                
                # Draw game info
                font = pygame.font.Font(None, 36)
                info_text = [
                    f"Current Word: {self.game_state['current_word']}",
                    f"Target Word: {self.game_state['target_word']}",
                    f"Moves: {self.game_state['moves']}/{self.game_state['max_moves']}",
                    f"Score: {self.score}"
                ]
                
                for i, text in enumerate(info_text):
                    surface = font.render(text, True, BLACK)
                    self.screen.blit(surface, (PADDING, PADDING + 40*i))
                
                # Draw algorithm indicator
                alg_color = ALGORITHM_COLORS[self.game.hint_algorithm]
                alg_text = f"Hint: {self.game.hint_algorithm.upper()}"
                alg_surface = font.render(alg_text, True, alg_color)
                self.screen.blit(alg_surface, (WINDOW_WIDTH - alg_surface.get_width() - PADDING, PADDING))
                
                # Draw obstacles info for Challenge mode
                if self.game_state['difficulty'] == 'CHALLENGE':
                    obstacles_y = PADDING + 40*len(info_text) + 20
                    
                    if self.game_state.get('banned_words') and len(self.game_state['banned_words']) > 0:
                        banned_text = f"Banned Words: {', '.join(self.game_state['banned_words'][:3])}"
                        if len(self.game_state['banned_words']) > 3:
                            banned_text += f" +{len(self.game_state['banned_words']) - 3} more"
                        banned_surface = font.render(banned_text, True, ERROR_COLOR)
                        self.screen.blit(banned_surface, (PADDING, obstacles_y))
                        obstacles_y += 40
                    
                    if self.game_state.get('restricted_letters') and len(self.game_state['restricted_letters']) > 0:
                        restricted_text = f"Restricted Letters: {', '.join(self.game_state['restricted_letters'])}"
                        restricted_surface = font.render(restricted_text, True, ERROR_COLOR)
                        self.screen.blit(restricted_surface, (PADDING, obstacles_y))
                
                # Draw input box and buttons
                self.input_box.draw(self.screen)
                for button in self.game_buttons.values():
                    button.draw(self.screen)
                
                # Draw message
                if self.message:
                    if self.message_animation < 1:
                        self.message_animation = min(1, self.message_animation + 0.05)
                    message_surface = font.render(self.message, True, self.message_color)
                    message_surface.set_alpha(int(255 * self.message_animation))
                    message_rect = message_surface.get_rect(
                        centerx=WINDOW_WIDTH//2,
                        y=WINDOW_HEIGHT//2 - 100
                    )
                    self.screen.blit(message_surface, message_rect)
        
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
                
                if self.menu_state == MENU_STATE_MAIN:
                    new_state = self.main_menu.handle_event(event)
                    if new_state:
                        self.menu_state = new_state
                        if new_state == MENU_STATE_GAME:
                            self.game_state = None
                            self.selected_difficulty = None
                            self.optimal_path = None
                
                elif self.menu_state == MENU_STATE_HELP:
                    new_state = self.help_menu.handle_event(event)
                    if new_state:
                        self.menu_state = new_state
                        
                elif self.menu_state == MENU_STATE_CUSTOM:
                    new_state, custom_words = self.custom_menu.handle_event(event)
                    if new_state:
                        self.menu_state = new_state
                        if new_state == MENU_STATE_GAME and custom_words:
                            try:
                                self.game_state = self.game.start_game(custom_words=custom_words)
                                self.show_message(f"Transform '{self.game_state['start_word']}' into '{self.game_state['target_word']}'", PRIMARY_COLOR)
                            except ValueError as e:
                                self.menu_state = MENU_STATE_CUSTOM
                                self.custom_menu.show_message(str(e), ERROR_COLOR)
                                
                elif self.menu_state == MENU_STATE_ALGORITHM:
                    new_state = self.algorithm_menu.handle_event(event)
                    if new_state:
                        self.menu_state = new_state
                        # Reset optimal path when algorithm changes
                        self.optimal_path = None
                
                elif self.menu_state == MENU_STATE_GAME:
                    if not self.game_state:
                        # Handle difficulty selection
                        for diff, button in self.difficulty_buttons.items():
                            if button.handle_event(event):
                                self.selected_difficulty = diff
                                self.game_state = self.game.start_game(diff)
                                self.show_message(f"Transform '{self.game_state['start_word']}' into '{self.game_state['target_word']}'", PRIMARY_COLOR)
                                break
                        
                        # Handle back button
                        if self.game_buttons['menu'].handle_event(event):
                            self.menu_state = MENU_STATE_MAIN
                    else:
                        # Handle game input
                        if self.game_buttons['menu'].handle_event(event):
                            self.menu_state = MENU_STATE_MAIN
                            self.optimal_path = None
                        elif self.game_buttons['algorithm'].handle_event(event):
                            self.menu_state = MENU_STATE_ALGORITHM
                        elif self.game_buttons['hint'].handle_event(event):
                            if self.game_state['status'] == 'PLAYING':
                                hint_data = self.game.get_hint(detail_level='basic')
                                if hint_data and hint_data['next_word']:
                                    self.show_message(f"Hint: Try '{hint_data['next_word']}' - {hint_data['explanation']}", 
                                                    ALGORITHM_COLORS[self.game.hint_algorithm])
                                else:
                                    self.show_message("No hint available", ERROR_COLOR)
                        elif self.game_buttons['full_hint'].handle_event(event):
                            if self.game_state['status'] == 'PLAYING':
                                hint_data = self.game.get_hint(detail_level='full')
                                if hint_data and hint_data['full_path']:
                                    self.optimal_path = hint_data['full_path']
                                    path_str = " → ".join(self.optimal_path)
                                    self.show_message(f"Optimal path: {path_str}", 
                                                    ALGORITHM_COLORS[self.game.hint_algorithm])
                                else:
                                    self.show_message("No path available", ERROR_COLOR)
                        
                        word = self.input_box.handle_event(event)
                        if word:
                            try:
                                self.game_state = self.game.make_move(word)
                                # Reset optimal path when a move is made
                                self.optimal_path = None
                                
                                if self.game_state['status'] == 'WON':
                                    self.update_score()
                                    self.show_message(f"Congratulations! Score: {self.score}", SUCCESS_COLOR)
                                elif self.game_state['status'] == 'LOST':
                                    self.show_message("Game Over! Try again!", ERROR_COLOR)
                            except ValueError as e:
                                self.show_message(str(e), ERROR_COLOR)
                                self.input_box.show_error()
            
            self.draw()
            clock.tick(60)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    gui = WordLadderGUI()
    gui.run()