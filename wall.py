from brick import Brick
import random 

class Wall:    
    """
    A class representing a brick wall, consisting of Brick objects, with various bonding patterns.
    
    The wall can be constructed in different patterns (English, Wild, or Stretcher bond)
    and provides functionality for simulating brick-by-brick construction within a
    movable robot frame.
    
    Attributes:
        width (int): Total wall width in millimeters
        height (int): Total wall height in millimeters
        type (str): Type of wall bonding pattern ("English", "Wild", or "Stretcher")
        brick_matrix (List[List[Brick]]): 2D grid representing the wall structure, where each cell 
            contains a Brick object with its build state
        wall_layout (List[List[Brick]]): Temporary storage for wall layout during construction,
            used to track pattern constraints when building rows
    """
    def __init__(self, width, height, type):
        """
        Initialize a new wall with specified dimensions and bonding pattern.
        
        Args:
            width (int): Wall width in millimeters
            height (int): Wall height in millimeters
            type (str): Bonding pattern type ("English", "Wild", or "Stretcher")
        """
        self.width = width  # Total wall width in mm
        self.height = height  # Total wall height in mm
        self.type = type # Type of wall
        self.brick_matrix = self._create_empty_wall(type) # Actual wall, a nested list of Brick objects
        self.wall_layout = [] # Frame of wall, a nested list of Brick objects (built=False)
    
    def _create_wild_bond_row(self, row_number, width, top=False):
        """
        Creates a single row of Wild bond pattern following the following rules
        1. No adjacent half bricks except at start (positions 0,1) and end (positions -2,-1)
        2. No head joints on top of eachother
        3. No more than 6 consecutive staggered steps pattern (not implemented)
        
        Args:
            row_number (int): The current row number (0-based)
            width (int): The total width of the wall in millimeters
            top (bool): Whether this is the top row of bricks
            
        Returns:
            List[Brick]: A list of bricks forming a complete row
        """
        current_row = []
        current_width = 0

        def is_allowed_half(position, current_row):
            """
            Check if the to be placed brick is allowed to be a half brick
            """
            # If position is at start or end, half bricks are allowed
            if position == 1 or position == 0:
                return True
            
            # If the previous brick is not a half brick, a half brick is allowed
            if not current_row[position - 1].half:
                return True
            
            # If between the start and end of row, and the previous brick is a half brick, a half brick is not allowed
            if position > 0 and current_row[position - 1].half:
                return False
            
            return True

        def get_row_widths(row):
            """
            Returns a list of cumulative widths for each brick position in a row.
            For example, if bricks are 220mm, 110mm, 220mm wide, returns [220, 330, 550]
            
            Args:
                row_number (int): The row to analyze
                
            Returns:
                List[int]: List of cumulative widths at each brick position
            """
            rolling_widths = []
            current_sum = 0
            
            for brick in row:
                current_sum += brick.width
                rolling_widths.append(current_sum)
                
            return rolling_widths
            
        def check_if_vertical_alignment(row_number, position, current_row):
            """
            Checks if adding a brick at the current position would create vertical alignment with joints in previous row.
            
            Args:
                row_number (int): Current row number
                position (int): Position where brick would be added
                current_row (List[Brick]): Current row being built
                
            Returns:
                bool: True if adding either brick type would create vertical alignment, False otherwise
            """
            if row_number == 0:
                return False
                
            previous_row_widths = get_row_widths(self.wall_layout[row_number-1])
            current_row_widths = get_row_widths(current_row)
            
            # Calculate width up to current position
            current_width = current_row_widths[position-1] if position > 0 else 0
            
            # Calculate potential widths with full or half brick
            potential_width_full = current_width + Brick(half=False, top=False, end=False).width
            potential_width_half = current_width + Brick(half=True, top=False, end=False).width
            
            # Check if either potential width matches any previous row joint
            for prev_width in previous_row_widths:
                if potential_width_full == prev_width or potential_width_half == prev_width:

                    #return True
                    # todo Bypass for now to show a bit more representative result
                    return False
                    
            return False
        
        # Get widths of possible bricks
        full_brick = Brick(half=False, top=top, end=False).width
        half_brick = Brick(half=True, top=top, end=False).width
        full_end = Brick(half=False, top=top, end=True).width
        half_end = Brick(half=True, top=top, end=True).width

        # Continue adding bricks until we reach or slightly exceed the width
        while current_width < width:
            position = len(current_row)
            remaining_space = width - current_width
            
            # If we can fit exactly one more full brick or one more half brick (end brick)
            if remaining_space <= full_brick:
                if remaining_space >= full_end:
                    brick = Brick(half=False, top=top, end=True)
                elif remaining_space >= half_end:
                    brick = Brick(half=True, top=top, end=True)
                current_row.append(brick)
                current_width += brick.width
                break

            # Otherwise add a non-end brick
            attempts = 0
            max_attempts = 10  # Prevent infinite loop
            brick_placed = False
            
            # Try to find a fitting brick to place
            while attempts < max_attempts and not brick_placed:
                random_brick_is_half = random.choice([True, False])
                would_align = check_if_vertical_alignment(row_number, position, current_row)
                
                # Try placing a half brick
                if random_brick_is_half and is_allowed_half(position, current_row) and not would_align:
                    next_brick = Brick(half=True, top=top, end=False)
                    brick_placed = True
                # Try placing a full brick
                elif not random_brick_is_half and not would_align:
                    next_brick = Brick(half=False, top=top, end=False)
                    brick_placed = True
                    
                attempts += 1
            
            # If we couldn't find a non-aligning brick after max attempts, just place a full brick
            if not brick_placed:
                next_brick = Brick(half=False, top=top, end=False)
            
            current_row.append(next_brick)
            current_width += next_brick.width

        # Double check if we still have space to fill
        remaining_space = width - current_width
        if remaining_space > 0:
            if remaining_space >= full_end:
                brick = Brick(half=False, top=top, end=True)
            elif remaining_space >= half_end:
                brick = Brick(half=True, top=top, end=True)
            current_row.append(brick)

        return current_row

    def _create_english_bond_row(self, row_number, width, top=False):
        """
        Creates a single row of English bond pattern.
        
        English bond alternates between stretcher courses (full bricks laid lengthwise)
        and header courses (half bricks), always starting with a half brick. 
        
        Args:
            row_number (int): Current row number (0-based, odd rows are header courses)
            width (int): Total width of the wall in millimeters
            top (bool): Whether this is the top row of bricks
            
        Returns:
            List[Brick]: A list of bricks forming a complete row
        """
        current_row = []
        current_width = 0
        
        # Always start with half brick
        first_brick = Brick(half=True, top=top, end=False)
        current_row.append(first_brick)
        current_width += first_brick.width
        
        # Determine if this is a row of half bricks (odd rows) or full bricks (even rows)
        is_half_brick_row = row_number % 2 == 1
        
        # Calculate space needed for end brick
        end_brick_width = Brick(half=True, top=top, end=True).width if is_half_brick_row else Brick(half=False, top=top, end=True).width
        
        # Fill the row
        while current_width + end_brick_width + (
            Brick(half=True, top=top, end=False).width if is_half_brick_row 
            else Brick(half=False, top=top, end=False).width
        ) <= width:
            brick = Brick(half=is_half_brick_row, top=top, end=False)
            current_row.append(brick)
            current_width += brick.width
        
        # Add end brick
        if is_half_brick_row:
            end_brick = Brick(half=True, top=top, end=True)
            current_row.append(end_brick)
        else:
            remaining_space = width - current_width
            if remaining_space >= Brick(half=False, top=top, end=True).width:
                brick = Brick(half=False, top=top, end=True)
                current_row.append(brick)
            elif remaining_space >= Brick(half=True, top=top, end=True).width:
                brick = Brick(half=True, top=top, end=True)
                current_row.append(brick)
        
        return current_row

    def _create_empty_wall(self, type):
        """
        Initialize the wall structure with the specified bonding pattern.
        
        Creates a complete wall layout row by row, handling:
        - Pattern-specific row creation (Stretcher, English, or Wild bond)
        - Top row identification and special handling
        - Proper brick alternation for each pattern type
        - End-of-wall height calculations
        
        Args:
            type (str): Bonding pattern type ("English", "Wild", or "Stretcher")
            
        Returns:
            List[List[Brick]]: Complete 2D grid of unbuilt bricks representing the wall
        """
        current_height = 0
        row_number = 0
        self.wall_layout = []

        while current_height < self.height:
            if current_height + Brick(half=False, top=True, end=False).height < self.height:
                top = False
            current_row = []
            current_width = 0
            if type == "English":
                current_row = self._create_english_bond_row(row_number, self.width, top)
            elif type == "Wild":
                current_row = self._create_wild_bond_row(row_number, self.width, top)
            # Build a wall with stretcher bonds
            else:
                # start first row with half brick 
                if current_height == 0:
                    start_with_half = True
                # check if first brick of underlying row is a half brick
                elif self.wall_layout[-1][0].half:
                    start_with_half = False
                # if not, start with a full brick
                else:
                    start_with_half = True

                if start_with_half:
                    half_brick = Brick(half=True, top=top, end=False)
                    current_row.append(half_brick)
                    current_width += half_brick.width
                else:
                    brick = Brick(half=False, top=top, end=False)
                    current_row.append(brick)
                    current_width += brick.width

                # add bricks until the end of the grid is reached
                while current_width + Brick(half=False, top=top, end=False).width <= self.width:
                    # Add a full brick if there's room
                    brick = Brick(half=False, top=top, end=False)
                    current_row.append(brick)
                    current_width += brick.width

                # Check the remaining space for the final brick
                remaining_space = self.width - current_width

                # If there's enough space for a full brick, add it
                if remaining_space >= Brick(half=False, top=top, end=True).width:
                    brick = Brick(half=False, top=top, end=True)
                    current_row.append(brick)
                    current_width += brick.width
                # If there's only enough space for a half brick, add it
                elif remaining_space >= Brick(half=True, top=top, end=True).width:
                    brick = Brick(half=True, top=top, end=True)
                    current_row.append(brick)
                    current_width += brick.width

            self.wall_layout.append(current_row)
            row_number += 1
            current_height += Brick(half=False, top=top, end=False).height
            if top:
                break

        self.current_height = current_height
        self.current_width = current_width
        return self.wall_layout

    def visualize_wall(self):
        """
        Creates a text-based visualization of the wall layout.
        
        The visualization is stored in self.wall_visual and shows the wall
        from bottom (row 0) to top.
        """
        # Define patterns for different frame positions
        patterns = [
            ('▓▓', '▓▓▓▓▓'),  
            ('░░', '░░░░░'),  
            ('@@', '@@@@@'),  
            ('██', '█████'),  
            ('##', '#####'),  
            ('$$', '$$$$$'),  
            ('&&', '&&&&&'),  
            ('▒▒', '▒▒▒▒▒'),  
            ('++', '+++++'), 
            ('==', '=====')
        ]
        
        wall_lines = []
        # Reverse wall so that row 0 is the bottom row
        for row in reversed(self.brick_matrix):
            row_visual = ""
            for position, element in enumerate(row):
                if element.built:
                    half_pattern, full_pattern = patterns[element.frame_counter % len(patterns)]
                    brick_visual = half_pattern if element.half else full_pattern
                else:
                    brick_visual = ".." if element.half else "....."
                
                row_visual += brick_visual
                if position < len(row) - 1:
                    row_visual += "|"
            wall_lines.append(row_visual)
        
        self.wall_visual = "\n".join(wall_lines)