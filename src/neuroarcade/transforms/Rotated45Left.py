from neuroarcade.transforms.base import BaseTransform
from neuroarcade.core.direction import Direction

class Rotated45Left(BaseTransform):
    """
    Default transform: no remapping.
    """

    def apply(self, direction: Direction) -> Direction:
        if direction == Direction.UP:
            return Direction.LEFT
        if direction == Direction.LEFT:
            return Direction.DOWN
        if direction == Direction.DOWN:
            return Direction.RIGHT
        if direction == Direction.RIGHT:
            return Direction.UP
        return direction
    
    def get_config_schema(self) -> dict:
        """
        Parameters that the UI can expose dynamically.
        """
        return {}