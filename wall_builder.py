from brick import Brick
from wall import Wall

class WallBuilder:
    """
    Handles the construction process of a wall using a movable robot frame.
    Works with a Wall instance to manage the building process.
    
    Attributes:
        wall (Wall): Reference to the wall being built
        frame_x (int): Current frame's horizontal position in mm
        frame_y (int): Current frame's vertical position in mm
        frame_width (int): Frame width in mm (default: 800)
        frame_height (int): Frame height in mm (default: 1300)
        total_moves (int): Counter for frame movements
        current_brick_position (int): Index of leftmost brick in frame
        current_row_position (int): Index of bottom row in frame
    """
    def __init__(self, wall):
        """Initialize builder with a wall instance and default frame dimensions."""
        self.wall = wall
        # Frame properties
        self.frame_x = 0
        self.frame_y = 0
        self.frame_width = 800
        self.frame_height = 1300
        # Movement tracking
        self.total_moves = 0
        self.current_brick_position = 0
        self.current_row_position = 0
    
    def move_frame(self, direction):
        """
        Move frame one brick-width or brick-height in specified direction.
        
        Args:
            direction (str): One of 'right', 'left', 'up', 'down'
            
        Returns:
            bool: True if movement succeeded, False if blocked
        """
        if direction == 'right':
            # Check if we can move right
            next_brick = self.current_brick_position + 1
            if next_brick < len(self.wall.brick_matrix[0]):
                new_width = self.wall.brick_matrix[0][self.current_brick_position].width
                self.frame_x += new_width
                self.current_brick_position = next_brick

                return True
                    
        elif direction == 'left':
            # Check if we can move left
            if self.current_brick_position > 0:
                next_brick = self.current_brick_position - 1
                # Get brick width directly from previous brick
                new_width = self.wall.brick_matrix[0][next_brick].width
                self.frame_x -= new_width
                self.current_brick_position = next_brick

                return True
                
        elif direction == 'up':
            # Check if we can move up
            next_row = self.current_row_position + 1
            if next_row < len(self.wall.brick_matrix):
                new_height = self.wall.brick_matrix[0][0].height  # All bricks in a row have same height
                self.frame_y += new_height
                self.current_row_position = next_row

                return True
                
        elif direction == 'down':
            # Check if we can move down
            if self.current_row_position > 0:
                next_row = self.current_row_position - 1
                new_height = self.wall.brick_matrix[0][0].height  # All bricks in a row have same height
                self.frame_y -= new_height
                self.current_row_position = next_row

                return True
                
        return False

    def get_brick_position(self, row_idx, brick_idx):
        """
        Calculate absolute position of a brick in the wall.
        
        Returns:
            tuple: (x, y) position in millimeters
        """
        # Calculate y position
        brick_y = 0
        for i in range(row_idx):
            brick_y += self.wall.brick_matrix[i][0].height  

        # Calculate x position
        brick_x = 0
        for i in range(brick_idx):
            prev_brick = self.wall.brick_matrix[row_idx][i]
            brick_x += prev_brick.width
            
        return brick_x, brick_y
    
    def is_within_frame(self, brick_x, brick_y, brick_width, brick_height):
        """Check if a brick position is within the current frame."""
        return (brick_x >= self.frame_x and 
                brick_x + brick_width <= self.frame_x + self.frame_width and
                brick_y >= self.frame_y and
                brick_y + brick_height <= self.frame_y + self.frame_height)
    
    def has_support(self, row_idx, brick_idx):
        """
        Verify if a brick has full support from the row below.
        
        A brick needs all supporting bricks below it to be built first,
        except for the foundation row which is always supported.
        """
        if row_idx == 0:  # First row is always supported (foundation)
            return True
            
        current_brick = self.wall.brick_matrix[row_idx][brick_idx]
        brick_width = current_brick.width
        
        # Calculate the start position of this brick
        brick_x = 0
        for i in range(brick_idx):
            prev_brick = self.wall.brick_matrix[row_idx][i]
            brick_x += prev_brick.width
            
        brick_end = brick_x + brick_width
            
        # Check support in the row below
        below_row = self.wall.brick_matrix[row_idx - 1]
        below_x = 0
        
        # Check each position that overlaps with our target brick
        for brick in below_row:
            below_end = below_x + brick.width
            
            # If this brick overlaps with our target brick's position
            if not (below_end <= brick_x or below_x >= brick_end):
                if not brick.built:
                    return False
                    
            below_x += brick.width
            
        return True
    
    def get_buildable_bricks(self):
        """Returns list of buildable bricks from current frame position"""
        buildable = []
        current = self.find_next_brick()
        while current is not None:
            row_idx, brick_idx = current
            buildable.append((row_idx, brick_idx))
            # Simulate building this brick
            self.wall.brick_matrix[row_idx][brick_idx].built = True
            current = self.find_next_brick()
        # Reset the simulated builds
        for row_idx, brick_idx in buildable:
            self.wall.brick_matrix[row_idx][brick_idx].built = False
        return buildable

    def find_next_brick(self):
        """
        Find the next valid brick that can be laid within the frame
        Returns:
            tuple: (row_index, brick_index) or None if no buildable brick found
        """
        for row_idx, row in enumerate(self.wall.brick_matrix):
            for brick_idx, brick in enumerate(row):
                if not brick.built:
                    # Get brick position and dimensions
                    brick_x, brick_y = self.get_brick_position(row_idx, brick_idx)
                    
                    # Check if brick is within frame and has support
                    if (self.is_within_frame(brick_x, brick_y, brick.width, brick.height) and 
                        self.has_support(row_idx, brick_idx)):
                        return row_idx, brick_idx
        return None
    
    def find_best_horizontal_position(self):
        """
        Find frame position allowing construction of most bricks.
        
        Returns:
            tuple: (steps_to_move, num_buildable_bricks) or None
            Positive steps indicate right movement, negative for left
        """
        best_buildable = 0
        best_steps = 0
        
        # Store original position
        orig_x = self.frame_x
        orig_brick_pos = self.current_brick_position
        
        # Try positions to the right
        steps_right = 0
        while True:
            if not self.move_frame('right'):
                break
            steps_right += 1
            buildable = len(self.get_buildable_bricks())
            if buildable > best_buildable:
                best_buildable = buildable
                best_steps = steps_right
        
        # Reset position
        self.frame_x = orig_x
        self.current_brick_position = orig_brick_pos
        
        # Try positions to the left
        steps_left = 0
        while True:
            if not self.move_frame('left'):
                break
            steps_left += 1
            buildable = len(self.get_buildable_bricks())
            if buildable > best_buildable:
                best_buildable = buildable
                best_steps = -steps_left
        
        # Reset position
        self.frame_x = orig_x
        self.current_brick_position = orig_brick_pos
        
        return (best_steps, best_buildable) if best_buildable > 0 else None
    
    def get_lowest_fully_built_row_height(self):
        """
        Returns the height of the lowest fully built row in mm
        """
        height = 0
        for row_idx, row in enumerate(self.wall.brick_matrix):
            # Check if all bricks in the row are built
            if all(brick.built for brick in row):
                # Calculate height up to this row
                row_height = 0
                for i in range(row_idx + 1):
                    row_height += self.wall.brick_matrix[i][0].height
                height = max(height, row_height)
        return height

    def can_move_vertically(self):
        """
        Checks if vertical movement is allowed based on conditions:
        1. Buildable bricks < 10
        2. Lowest fully built row >= 750mm
        """
        buildable_count = len(self.get_buildable_bricks())
        lowest_built_height = self.get_lowest_fully_built_row_height()
        return lowest_built_height >= 750

    def get_next_best_move(self):
        """
        Determine optimal next move based on buildable bricks and wall state.
        
        Returns:
            tuple: (move_direction, num_buildable_bricks) where move_direction is:
                - 'stay': Build bricks at current position
                - 'left'/'right'/'up'/'down': Single movement
                - (steps, 'horizontal'): Multi-step horizontal movement
                - (target_y, 'vertical'): Move to specific height
        """
        current_buildable = len(self.get_buildable_bricks())
        if current_buildable > 0:
            return ('stay', current_buildable)
            
        # Check if vertical movement is allowed
        if self.can_move_vertically():
            # If we can move vertically, move frame to 700mm height
            target_y = 750
            if self.frame_y != target_y:
                return ((target_y, 'vertical'), 0)  # Return special vertical movement command
        
        # If we can't move vertically or are already at target height,
        # find best horizontal position
        best_horizontal = self.find_best_horizontal_position()
        if best_horizontal:
            steps, buildable = best_horizontal
            return ((steps, 'horizontal'), buildable)
            
        return None

    def execute_next_best_move(self, single=False):
        """
        Execute optimal next move found by get_next_best_move
        
        Args:
            single (bool): If True, build only one brick when staying in position, else build the whole set
            
        Returns:
            tuple: (success_bool, description_string)
        """
        next_move = self.get_next_best_move()
        
        if next_move is None:
            return False, "No valid moves available!"
            
        direction, num_buildable = next_move

        if direction == 'stay' and not single:
            # If staying put is best, build all available bricks
            buildable = self.get_buildable_bricks()
            for row_idx, brick_idx in buildable:
                self.wall.brick_matrix[row_idx][brick_idx].built = True
                self.wall.brick_matrix[row_idx][brick_idx].frame_counter = self.total_moves
            return True, f"Built {len(buildable)} bricks at current position."
        elif direction == 'stay':
            # Find the first unbuildable brick
            buildable = self.get_buildable_bricks()
            if not buildable:
                return False, "No buildable bricks available."
            
            # If single is True, only build the first buildable brick
            row_idx, brick_idx = buildable[0]
            self.wall.brick_matrix[row_idx][brick_idx].built = True
            self.wall.brick_matrix[row_idx][brick_idx].frame_counter = self.total_moves
            return True, f"Built one brick at current position."
        
        elif isinstance(direction, tuple):
            if direction[1] == 'horizontal':
                # Handle horizontal movement
                steps = direction[0]
                move_dir = 'right' if steps > 0 else 'left'

                # increment move counter, we assume 1 movement action = 1 movement
                self.total_moves +=1

                for _ in range(abs(steps)):
                    self.move_frame(move_dir)
                return True, f"Moved frame {steps} steps {'right' if steps > 0 else 'left'}. {num_buildable} bricks now buildable."
            elif direction[1] == 'vertical':
                # Handle vertical movement to target height
                target_y = direction[0]
                current_y = self.frame_y
                # Calculate how many vertical moves needed
                steps_needed = (target_y - current_y) / self.wall.brick_matrix[0][0].height
                steps_needed = int(round(steps_needed))

                # increment move counter, we assume 1 movement action = 1 movement
                self.total_moves +=1
                
                # Move up or down as needed
                direction = 'up' if steps_needed > 0 else 'down'
                for _ in range(abs(steps_needed)):
                    self.move_frame(direction)
                return True, f"Moved frame vertically to {target_y}mm height"
        else:
            # Handle single direction movement
            self.move_frame(direction)
            return True, f"Moved frame {direction}. {num_buildable} bricks now buildable."