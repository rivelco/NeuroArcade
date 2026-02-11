from PyQt6.QtWidgets import (
    QLabel, QSpinBox, QDoubleSpinBox,
    QCheckBox, QLineEdit, QVBoxLayout, QWidget
)
from PyQt6.QtCore import Qt


def clear_layout(layout):
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        if widget is not None:
            widget.deleteLater()


def widget_from_default(param_name, spec):
    default = spec.get("default")
    tooltip = spec.get("description", "")

    label = QLabel(spec.get("name", param_name))
    label.setToolTip(tooltip)

    # ---- INT ----
    if isinstance(default, int):
        widget = QSpinBox()
        widget.setMinimum(spec.get("min", -999999))
        widget.setMaximum(spec.get("max", 999999))
        widget.setValue(default)
        widget.setFocusPolicy(Qt.FocusPolicy.ClickFocus)

    # ---- FLOAT ----
    elif isinstance(default, float):
        widget = QDoubleSpinBox()
        widget.setMinimum(spec.get("min", -999999.0))
        widget.setMaximum(spec.get("max", 999999.0))
        widget.setValue(default)
        widget.setFocusPolicy(Qt.FocusPolicy.ClickFocus)

    # ---- BOOL ----
    elif isinstance(default, bool):
        widget = QCheckBox()
        widget.setChecked(default)
        widget.setFocusPolicy(Qt.FocusPolicy.ClickFocus)

    # ---- STRING ----
    else:
        widget = QLineEdit(str(default))
        widget.setFocusPolicy(Qt.FocusPolicy.ClickFocus)

    widget.setToolTip(tooltip)

    return label, widget


def update_box_options(schema: dict, box_widget: QWidget):
    """
    Dynamically populate a Qt box with config options from schema.
    """

    layout = box_widget.layout()
    if layout is None:
        layout = QVBoxLayout()
        box_widget.setLayout(layout)

    # Clear old widgets
    clear_layout(layout)
    
    # Add new widgets
    box_widget._config_widgets = {}  # store for later retrieval

    # No config case
    if not schema:
        layout.addWidget(QLabel("This element has no configurable parameters."))
        return

    for param, spec in schema.items():
        label, widget = widget_from_default(param, spec)

        layout.addWidget(label)
        layout.addWidget(widget)

        box_widget._config_widgets[param] = widget

def read_config(box_widget):
    values = {}
    for key, w in box_widget._config_widgets.items():
        if hasattr(w, "value"):
            values[key] = w.value()
        elif hasattr(w, "isChecked"):
            values[key] = w.isChecked()
        else:
            values[key] = w.text()
    return values
