from neuroarcade.transforms.base import BaseTransform
from neuroarcade.core.direction import Direction

class IdentityTransform(BaseTransform):
    """
    Default transform: no remapping.
    """

    def apply(self, direction: Direction) -> Direction:
        return direction
