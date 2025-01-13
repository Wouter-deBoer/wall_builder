class Brick:
    """
    A class representing a brick, which are the instances a Wall object is built on.
    
    Attributes:
        half (bool): Denotes if the brick is half sized 
        top (bool): Whether the brick is in the top row
        end (bool): Whether the brick is the last in a row, starting from the left
        width (int): The width of the brick including joint
        height (float): The height of the brick including joint
        built (bool): True if the brick has been built, False if not
        frame_counter (int): Keeps track which frame position in sequence built this brick
    """
    def __init__(self, half, top, end):
        self.half = half
        if half:
            self.width = 100  # mm
            self.height = 50  # mm
        else:
            self.width = 210  # mm
            self.height = 50  # mm

        # we assume that two consequent bricks always have a head and bed joint
        # if the brick is the last one in the row, do not add a head joint
        if not end:
            self.width += 10
        # if the brick is the last one in a column, do not add a bed joint
        if not top:
            self.height += 12.5
        
        self.built = False  # Indicates whether the brick has been laid

        self.frame_counter = -1 # For visualisation, track which frame position in sequence built this brick