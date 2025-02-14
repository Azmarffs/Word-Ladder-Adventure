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
            'CHALLENGE': {'min_length': 5, 'max_length': 6, 'max_moves': 10}
        }
        
    def _get_neighbors(self, word: str) -> List[str]:
        """Generate all possible one-letter variations of the word that exist in dictionary."""
        neighbors = []
        for i in range(len(word)):
            for c in string.ascii_lowercase:
                new_word = word[:i] + c + word[i+1:]
                if new_word in self.dictionary and new_word != word:
                    neighbors.append(new_word)
        return neighbors

    def get_random_word_pair(self, difficulty: str = 'BEGINNER') -> Tuple[str, str]:
        """Generate a random word pair based on difficulty level."""
        level = self.difficulty_levels[difficulty]
        valid_words = [word for word in self.dictionary 
                      if level['min_length'] <= len(word) <= level['max_length']]
        
        while True:
            start = random.choice(valid_words)
            target = random.choice(valid_words)
            if start != target:
                # Verify that a path exists
                if self.bfs(start, target):
                    return start, target

    def get_hint(self, current_word: str, target_word: str) -> Optional[str]:
        """Get the next best word in the optimal path."""
        path = self.a_star(current_word, target_word)
        if path and len(path) > 1:
            return path[1]
        return None

    def validate_move(self, current_word: str, next_word: str) -> bool:
        """Validate if the move is legal."""
        if next_word not in self.dictionary:
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
                        'brain', 'train', 'trace', 'track', 'stack', 'stark'}
        
        self.word_ladder = WordLadder(dictionary)
        self.current_game = None
        self.history = []
        
    def start_game(self, difficulty: str = 'BEGINNER') -> Dict:
        """Start a new game with the specified difficulty."""
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
            'difficulty': difficulty
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
    
    def get_hint(self) -> Optional[str]:
        """Get a hint for the current position."""
        if not self.current_game or self.current_game['status'] != 'PLAYING':
            return None
            
        return self.word_ladder.get_hint(
            self.current_game['current_word'],
            self.current_game['target_word']
        )

def main():
    """Example usage of the WordLadderGame class."""
    game = WordLadderGame()
    
    # Start a new game
    print("\nStarting new Word Ladder game...")
    game_state = game.start_game('BEGINNER')
    print(f"Start word: {game_state['start_word']}")
    print(f"Target word: {game_state['target_word']}")
    print(f"Maximum moves: {game_state['max_moves']}")
    
    # Example game loop
    while game_state['status'] == 'PLAYING':
        print(f"\nCurrent word: {game_state['current_word']}")
        print(f"Moves used: {game_state['moves']}/{game_state['max_moves']}")
        
        # Get a hint
        hint = game.get_hint()
        print(f"Hint: Try '{hint}'")
        
        # In a real game, you would get input from the user
        # For this demo, we'll use the hint
        try:
            game_state = game.make_move(hint)
        except ValueError as e:
            print(f"Error: {e}")
            continue
    
    # Game over
    print("\nGame Over!")
    print(f"Status: {game_state['status']}")
    print(f"Path taken: {' -> '.join(game_state['path'])}")

if __name__ == "__main__":
    main()