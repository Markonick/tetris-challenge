#!/usr/bin/env python3
import copy
import logging
from typing import Generator

SIZE_MAP = {
    "Q": {"h": 2, "w":2, "array": [["q","q"], ["q","q"]]},
    "Z": {"h": 2, "w":3, "array": [[".","z","z"], ["z","z","."]]},
    "S": {"h": 2, "w":3, "array": [["s","s","."], [".","s","s"]]},
    "T": {"h": 2, "w":3, "array": [[".","t","."], ["t","t","t"]]},
    "I": {"h": 1, "w":4, "array": [["i","i","i","i"]]},
    "L": {"h": 4, "w":2, "array": [["l","l"], ["l","."], ["l","."], ["l","."]]},
    "J": {"h": 4, "w":2, "array": [["j","j"], [".","j"], [".","j"], [".","j"]]},
}

logger = logging.getLogger("Tetris Debugger")
logging.basicConfig(level=logging.DEBUG)

class Tetris():
    """
    Tetris class responsible for initialising and updating grid while reading inputs"
    """

    def __init__(self, width: int, height: int) -> None:
        self._width = width
        self._height = height
        self._grid = self.initialise_grid(width, height)
        self._row_deletions = 0
        self.list_of_available_symbols = ["q", "z", "s", "t", "i", "l", "j"]

    def initialise_grid(self, width: int, height: int) -> list[list]:
        """Public method to initialise an empty grid"""

        zero_list = [".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ]
        return [[x for x in copy.deepcopy(zero_list)] for x in range(height)]

    def update_grid_per_shape(self, name: str, x_offset: int, shape: list[list], height: int, width: int):
        """
        Public method to add a shape to the grid:
        1) Find optimal non colliding y-offset and place shape
        2) Check if any full rows and delete if so
        """

        # we want to check if we can place shape at bottom of grid so
        # check that y-coordinates to place the shape are unimpeded
        logger.debug(f"Incoming shape {name}{x_offset}...updating state of grid")
        # y_offset = self._find_y_offset_to_place_shape(shape, x_offset, height, width)
        self._check_where_to_place_incoming_shape(x_offset, shape)
        self._clear_row_or_not()

    @staticmethod
    def parse_line_to_array(line: str) -> list:
        """
        Public method to parse an string input line into a list of symbol pairs eg:
        'Q0,Q1' -> ['Q0', 'Q1']
        """

        parsed_line = line.strip().split(',')
        logger.debug(parsed_line)
        return parsed_line

    def height_of_remaining_blocks(self) -> int:
        """
        Public method to return max accumulated height of remaining blocks in grid
        """
        cnt = 0
        for line in self._get_current_grid():
            if line == ['.', '.', '.', '.', '.', '.', '.', '.', '.', '.']:
                break
            cnt += 1
        return cnt
    
    def _get_current_grid(self) -> list[list]:
        """
        Public method to return current frid state
        """

        return self._grid
    
    def print_grid(self, all=True):
        """
        Public method to print current grid layout in a human readable format
        """
        
        # Flip to human readable representation
        real_representation = reversed(self._get_current_grid())
        if all:
            for item in real_representation:
                logger.debug(item)
        else:
            logger.debug(real_representation[0:2])

    def _check_where_to_place_incoming_shape(self, x_offset: int, shape: list[list]) -> None:
        """
        Private method to check optimal y-offset where no more collisions occur and 
        update the grid by placing incoming shape accordingly,.
        """
        
        y_offset = 5
        is_collision = self._detected_collision(shape, x_offset, y_offset)  # initialise colision flag value
        while not is_collision:
            y_offset -= 1
            is_collision = self._detected_collision(shape, x_offset, y_offset)
        
        y_offset += 1  # + 1 because we have to go up 1 on y-axis since collision 
        # Place shape on grid at (x, y) offsets
        for r, line in enumerate(shape):
            logger.debug(f"{r=}")
            logger.debug(f"{line=}")

            y = y_offset + r
            for c, box in enumerate(line):
                x = x_offset + c
                if box != '.':     
                    # Now set grid!
                    logger.debug(f"!!!!!!Placing shape at {x=}, {y=}!!!!!")
                    self._get_current_grid()[y][x] = box

        self.print_grid()
        return None
    
    def _detected_collision(self, shape: list[list], x_offset: int, y_offset: int) -> bool:
        """
        Private method to detect any collision between a shape and the current grid.
        Return true if collision.
        """
        
        logger.debug(f"Performing Collision Detection..for shape {shape}.")
        
        # Compare all shape coordinates to corresponding grid coordinates 
        # and if grid coords activated then we have a collision.
        # For each box in shape check if corresponding grid box is occupied

        for r, line in enumerate(shape):
            y = y_offset + r
            if y < 0:
                return True
            for c, box in enumerate(line):
                logger.debug(f"{box=}")
                x = x_offset + c
                if box != '.':
                    # Now check that these coords are not taken already in the grid
                    logger.debug(f"grid point value at {x=}, {y=}")
                    logger.debug(f"grid point value at {x=}, {y=}: {self._get_current_grid()[y][x]}")

                    # Found collision, exit this loop by returning True
                    if self._get_current_grid()[y][x] != ".":  
                        logger.debug(f"Found collision at coords {x=}, {y=}")
                        return True

        # If we reached this far, no collision       
        return False

    def _clear_row_or_not(self):
        """
        Private method to clear a grid row if it is fully occupied
        """
        
        def full_row_exists() -> int:
            for h_idx in range(self._height):
                if '.' not in self._get_current_grid()[h_idx]:
                    return h_idx
            
            return None
            
        h_idx = full_row_exists()
        is_grid_updated = False
        while h_idx is not None:
            logger.debug(f"Deleting row #{h_idx} and shifting down rows above this row")
            self._row_deletions += 1
            for i in range(h_idx, self._height - 1):
                self._get_current_grid()[i] = self._get_current_grid()[i + 1]

            h_idx = full_row_exists()
            is_grid_updated = True
        logger.debug(f"NO MORE FULL ROWS AT THIS POINT..........")
        if is_grid_updated:
            logger.debug(f"****************NEW GRID*****************") 
        
        logger.debug(f"Deleted {self._row_deletions} rows so far!!!")

    
def run_process() -> str: 
    import sys

    for i, line in enumerate(sys.stdin):
        tetris = Tetris(10, 100)
        logger.debug(f"Processing input line #{i}.........")
        input_line_array = tetris.parse_line_to_array(line)

        for symbol_pair in input_line_array:  # Get each shape symbol-pair eg. Q2 in this line
            shape_name, shape_origin_x = symbol_pair[0], int(symbol_pair[1])  # Get symbol eg. Q and x-origin eg. 0
            shape_array = SIZE_MAP[shape_name]["array"]
            shape_height = SIZE_MAP[shape_name]["h"]
            shape_width = SIZE_MAP[shape_name]["w"]
            # on each shape, update grid (place shape, check if row to be deleted etc...)
            tetris.update_grid_per_shape(shape_name, shape_origin_x, shape_array, shape_height, shape_width)

        logger.debug("********************************")
        logger.debug("*********FINISH LINE!!!*********")
        logger.debug("********************************")

        output = tetris.height_of_remaining_blocks()

        tetris.print_grid()
        logger.debug(f"Height of remaining blocks is: {output}")
        print(output)  # For STDOUT
    
if __name__ == "__main__":
    run_process()
