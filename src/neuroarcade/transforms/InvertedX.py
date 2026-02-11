from neuroarcade.transforms.base import BaseTransform
from neuroarcade.core.direction import Direction

class InvertedX(BaseTransform):
    """
    Default transform: no remapping.
    """

    def apply(self, direction: Direction) -> Direction:
        if direction == Direction.LEFT:
            return Direction.RIGHT
        if direction == Direction.RIGHT:
            return Direction.LEFT
        return direction
    
    def get_config_schema(self) -> dict:
        """
        Parameters that the UI can expose dynamically.
        """
        return {}