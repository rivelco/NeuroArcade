from neuroarcade.transforms.base import BaseTransform
from neuroarcade.core.direction import Direction
from neuroarcade.ui.instructions_html import INSTRUCTIONS_HEAD

class Rotated90Right(BaseTransform):
    """
    Rotates the direction 90 degrees to the right.
    """

    def apply(self, direction: Direction) -> Direction:
        if direction == Direction.UP:
            return Direction.RIGHT
        if direction == Direction.RIGHT:
            return Direction.DOWN
        if direction == Direction.DOWN:
            return Direction.LEFT
        if direction == Direction.LEFT:
            return Direction.UP
        return direction
    
    def get_config_schema(self) -> dict:
        """
        Parameters that the UI can expose dynamically.
        """
        return {}
    
    def get_instructions(self) -> str:
        return f"""
        <html>
            {INSTRUCTIONS_HEAD}
        <body>

            <h1>Inverted Y</h1>

            <div class="section">
                <p>
                    This transformer rotates the controllers 90 degrees clockwise.
                </p>
            </div>

            <h2>How It Works</h2>
            <div class="box">
                <ul>
                    <li>You move LEFT -> The transform gives you UP</li>
                    <li>You move RIGHT -> The transform gives you DOWN</li>
                    <li>You move UP -> The transform gives you RIGHT</li>
                    <li>You move DOWN -> The transform gives you LEFT</li>
                </ul>
            </div>
        </body>
        </html>
        """