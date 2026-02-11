from neuroarcade.transforms.base import BaseTransform
from neuroarcade.core.direction import Direction

class Identity(BaseTransform):
    """
    Default transform: no remapping.
    """

    def apply(self, direction: Direction) -> Direction:
        return direction
    
    def get_config_schema(self) -> dict:
        """
        Parameters that the UI can expose dynamically.
        """
        return {}
