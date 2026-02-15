from neuroarcade.transforms.base import BaseTransform
from neuroarcade.core.direction import Direction
from neuroarcade.ui.instructions_html import INSTRUCTIONS_HEAD

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
    
    def get_instructions(self) -> str:
        return f"""
        <html>
            {INSTRUCTIONS_HEAD}
        <body>

            <h1>Inverted X</h1>

            <div class="section">
                <p>
                    This transformer inverts the X controls.
                </p>
            </div>

            <h2>How It Works</h2>
            <div class="box">
                <ul>
                    <li>You move LEFT -> The transform gives you RIGHT</li>
                    <li>You move RIGHT -> The transform gives you LEFT</li>
                    <li>You move UP -> The transform gives you UP</li>
                    <li>You move DOWN -> The transform gives you DOWN</li>
                </ul>
            </div>
        </body>
        </html>
        """