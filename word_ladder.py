from collections import deque, defaultdict
import heapq
from typing import List, Set, Dict, Tuple, Optional, Callable
import string
import random

class WordLadder:
    def __init__(self, dictionary_words: Set[str]):
        self.dictionary = {word.lower() for word in dictionary_words if word.isalpha()}
        self.difficulty_levels = {
            'BEGINNER': {'min_length': 3, 'max_length': 4, 'max_moves': 5},
            'ADVANCED': {'min_length': 4, 'max_length': 5, 'max_moves': 7},
            'CHALLENGE': {'min_length': 5, 'max_length': 6, 'max_moves': 10, 'obstacles': True}
        }
        self.banned_words = set()
        self.restricted_letters = set()
        
    def _get_neighbors(self, word: str) -> List[str]:
        """Generate all possible one-letter variations of the word that exist in dictionary."""
        neighbors = []
        for i in range(len(word)):
            for c in string.ascii_lowercase:
                # Skip restricted letters in Challenge mode
                if c in self.restricted_letters:
                    continue
                    
                new_word = word[:i] + c + word[i+1:]
                if (new_word in self.dictionary and 
                    new_word != word and 
                    new_word not in self.banned_words):
                    neighbors.append(new_word)
        return neighbors

    def get_random_word_pair(self, difficulty: str = 'BEGINNER') -> Tuple[str, str]:
        """Generate a random word pair based on difficulty level."""
        level = self.difficulty_levels[difficulty]
        valid_words = [word for word in self.dictionary 
                      if level['min_length'] <= len(word) <= level['max_length']]
        
        # Reset obstacles for new game
        self.banned_words = set()
        self.restricted_letters = set()
        
        # Add obstacles for Challenge mode
        if difficulty == 'CHALLENGE' and level.get('obstacles', False):
            # Ban a few random words that aren't critical to solutions
            potential_banned = random.sample(valid_words, min(10, len(valid_words)))
            for word in potential_banned:
                # Only ban if removing it doesn't disconnect the graph too much
                self.banned_words.add(word)
                if len(valid_words) > 50:  # Only restrict letters if we have enough words
                    # Restrict 1-2 random letters
                    self.restricted_letters = set(random.sample(string.ascii_lowercase, random.randint(1, 2)))
        
        attempts = 0
        while attempts < 100:  # Limit attempts to avoid infinite loop
            start = random.choice(valid_words)
            target = random.choice(valid_words)
            if start != target and start not in self.banned_words and target not in self.banned_words:
                # Verify that a path exists
                if self.a_star(start, target):
                    return start, target
            attempts += 1
            
        # If we couldn't find a pair with obstacles, clear them and try again
        self.banned_words = set()
        self.restricted_letters = set()
        return self.get_random_word_pair(difficulty)

    def get_hint(self, current_word: str, target_word: str, algorithm: str = 'a_star') -> Dict:
        """Get the next best word in the optimal path using the specified algorithm."""
        if algorithm == 'bfs':
            path = self.bfs(current_word, target_word)
        elif algorithm == 'ucs':
            path = self.ucs(current_word, target_word)
        else:  # Default to A*
            path = self.a_star(current_word, target_word)
            
        if not path or len(path) <= 1:
            return {
                'next_word': None,
                'explanation': "No valid path found.",
                'full_path': None
            }
            
        next_word = path[1]
        
        # Generate explanation
        diff_index = next(i for i, (a, b) in enumerate(zip(current_word, next_word)) if a != b)
        explanation = f"Change letter {diff_index + 1} from '{current_word[diff_index]}' to '{next_word[diff_index]}'."
        
        return {
            'next_word': next_word,
            'explanation': explanation,
            'full_path': path
        }

    def validate_move(self, current_word: str, next_word: str) -> bool:
        """Validate if the move is legal."""
        if next_word not in self.dictionary or next_word in self.banned_words:
            return False
        
        # Check if the move uses any restricted letters
        for c in next_word:
            if c in self.restricted_letters:
                return False
                
        differences = sum(1 for a, b in zip(current_word, next_word) if a != b)
        return differences == 1

    def bfs(self, start_word: str, target_word: str) -> Optional[List[str]]:
        """Breadth-First Search implementation."""
        if start_word not in self.dictionary or target_word not in self.dictionary:
            return None
            
        queue = deque([(start_word, [start_word])])
        visited = {start_word}
        
        while queue:
            current_word, path = queue.popleft()
            
            if current_word == target_word:
                return path
                
            for neighbor in self._get_neighbors(current_word):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        
        return None

    def ucs(self, start_word: str, target_word: str) -> Optional[List[str]]:
        """Uniform Cost Search implementation."""
        if start_word not in self.dictionary or target_word not in self.dictionary:
            return None
            
        priority_queue = [(0, start_word, [start_word])]
        visited = set()
        
        while priority_queue:
            cost, current_word, path = heapq.heappop(priority_queue)
            
            if current_word == target_word:
                return path
                
            if current_word in visited:
                continue
                
            visited.add(current_word)
            
            for neighbor in self._get_neighbors(current_word):
                if neighbor not in visited:
                    new_cost = cost + 1
                    heapq.heappush(priority_queue, (new_cost, neighbor, path + [neighbor]))
        
        return None

    def _calculate_heuristic(self, word: str, target: str) -> int:
        """Calculate heuristic value (number of different letters) for A* search."""
        return sum(1 for a, b in zip(word, target) if a != b)

    def a_star(self, start_word: str, target_word: str) -> Optional[List[str]]:
        """A* Search implementation."""
        if start_word not in self.dictionary or target_word not in self.dictionary:
            return None
            
        open_set = [(self._calculate_heuristic(start_word, target_word), 0, start_word, [start_word])]
        visited = set()
        g_scores = defaultdict(lambda: float('inf'))
        g_scores[start_word] = 0
        
        while open_set:
            _, g_score, current_word, path = heapq.heappop(open_set)
            
            if current_word == target_word:
                return path
                
            if current_word in visited:
                continue
                
            visited.add(current_word)
            
            for neighbor in self._get_neighbors(current_word):
                tentative_g_score = g_score + 1
                
                if tentative_g_score < g_scores[neighbor]:
                    g_scores[neighbor] = tentative_g_score
                    f_score = tentative_g_score + self._calculate_heuristic(neighbor, target_word)
                    heapq.heappush(open_set, (f_score, tentative_g_score, neighbor, path + [neighbor]))
        
        return None
        
    def check_valid_word_pair(self, start_word: str, target_word: str) -> bool:
        """Check if a custom word pair is valid and has a solution."""
        if (start_word not in self.dictionary or 
            target_word not in self.dictionary or 
            len(start_word) != len(target_word)):
            return False
            
        # Check if a path exists
        return bool(self.a_star(start_word, target_word))

class WordLadderGame:
    def __init__(self, dictionary_path: str = None):
        # If no dictionary provided, use a default set of words
        if dictionary_path:
            with open(dictionary_path, 'r') as f:
                dictionary = set(word.strip().lower() for word in f)
        else:
            # Default dictionary for demo
            dictionary = {'cat', 'cot', 'cog', 'dog', 'dot', 'lot', 'log', 'hot', 
                        'hat', 'rat', 'sat', 'sit', 'pit', 'put', 'but', 'bat',
                        'plate', 'slate', 'slant', 'plant', 'plane', 'crane',
                        'brain', 'train', 'trace', 'track', 'stack', 'stark',
                        'start', 'smart', 'chart', 'charm', 'chasm', 'chase',
                        'phase', 'phone', 'prone', 'prune', 'prude', 'pride',
                        'prize', 'price', 'slice', 'spice', 'spine', 'shine',
                        'shone', 'stone', 'store', 'score', 'scare', 'share'}
        
        self.word_ladder = WordLadder(dictionary)
        self.current_game = None
        self.history = []
        self.hint_algorithm = 'a_star'  # Default algorithm
        
    def start_game(self, difficulty: str = 'BEGINNER', custom_words: Tuple[str, str] = None) -> Dict:
        """Start a new game with the specified difficulty or custom words."""
        if custom_words and all(custom_words):
            start_word, target_word = custom_words
            start_word = start_word.lower()
            target_word = target_word.lower()
            
            # Validate custom words
            if not self.word_ladder.check_valid_word_pair(start_word, target_word):
                raise ValueError("Invalid word pair. Both words must exist in the dictionary and have a valid transformation path.")
                
            # Determine difficulty based on word length
            word_length = len(start_word)
            if word_length <= 4:
                difficulty = 'BEGINNER'
            elif word_length <= 5:
                difficulty = 'ADVANCED'
            else:
                difficulty = 'CHALLENGE'
        else:
            start_word, target_word = self.word_ladder.get_random_word_pair(difficulty)
            
        max_moves = self.word_ladder.difficulty_levels[difficulty]['max_moves']
        
        self.current_game = {
            'start_word': start_word,
            'current_word': start_word,
            'target_word': target_word,
            'moves': 0,
            'max_moves': max_moves,
            'path': [start_word],
            'status': 'PLAYING',
            'difficulty': difficulty,
            'banned_words': list(self.word_ladder.banned_words),
            'restricted_letters': list(self.word_ladder.restricted_letters)
        }
        
        return self.current_game
    
    def make_move(self, next_word: str) -> Dict:
        """Make a move in the current game."""
        if not self.current_game or self.current_game['status'] != 'PLAYING':
            raise ValueError("No active game in progress")
            
        if not self.word_ladder.validate_move(self.current_game['current_word'], next_word):
            raise ValueError("Invalid move")
            
        self.current_game['moves'] += 1
        self.current_game['current_word'] = next_word
        self.current_game['path'].append(next_word)
        
        # Check win/lose conditions
        if next_word == self.current_game['target_word']:
            self.current_game['status'] = 'WON'
        elif self.current_game['moves'] >= self.current_game['max_moves']:
            self.current_game['status'] = 'LOST'
            
        # Add to history if game is over
        if self.current_game['status'] != 'PLAYING':
            self.history.append(dict(self.current_game))
            
        return self.current_game
    
    def set_hint_algorithm(self, algorithm: str) -> None:
        """Set the algorithm to use for hints."""
        if algorithm not in ['bfs', 'ucs', 'a_star']:
            raise ValueError("Invalid algorithm. Choose from 'bfs', 'ucs', or 'a_star'.")
        self.hint_algorithm = algorithm
    
    def get_hint(self, detail_level: str = 'basic') -> Dict:
        """Get a hint for the current position with the specified detail level."""
        if not self.current_game or self.current_game['status'] != 'PLAYING':
            return {'next_word': None, 'explanation': "No active game in progress."}
            
        hint_data = self.word_ladder.get_hint(
            self.current_game['current_word'],
            self.current_game['target_word'],
            self.hint_algorithm
        )
        
        if detail_level == 'full' and hint_data['full_path']:
            return hint_data
        else:
            return {
                'next_word': hint_data['next_word'],
                'explanation': hint_data['explanation']
            }
            
    def get_dictionary_words(self, length: int = None) -> List[str]:
        """Get a list of dictionary words, optionally filtered by length."""
        if length:
            return [word for word in self.word_ladder.dictionary if len(word) == length]
        return list(self.word_ladder.dictionary)

if __name__ == "__main__":
    game = WordLadderGame()
    game.start_game('BEGINNER')