from PyQt6.QtWidgets import (
    QLabel, QSpinBox, QDoubleSpinBox,
    QCheckBox, QLineEdit, QFormLayout, QWidget,
    QPushButton, QAbstractSpinBox, QVBoxLayout,
    QComboBox,
)
from PyQt6.QtCore import Qt


def clear_layout(layout):
    while layout.rowCount():
        layout.removeRow(0)


def widget_from_default(param_name, spec):
    default = spec.get("default")
    tooltip = spec.get("description", "")

    label = QLabel(spec.get("name", param_name))
    label.setToolTip(tooltip)
    
    # ---- Options ----
    if spec.get("type", "") == "enum":
        widget = QComboBox()
        widget.addItems(spec.get("options", []))
        widget.setCurrentText(default)
    
    # ---- BOOL ----
    elif isinstance(default, bool):
        widget = QCheckBox()
        widget.setChecked(default)
        widget.setFocusPolicy(Qt.FocusPolicy.ClickFocus)

    # ---- INT ----
    elif isinstance(default, int):
        widget = QSpinBox()
        widget.setMinimum(spec.get("min", -999999))
        widget.setMaximum(spec.get("max", 999999))
        widget.setValue(default)
        widget.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        widget.setSingleStep(1)
        widget.setCorrectionMode(QAbstractSpinBox.CorrectionMode.CorrectToNearestValue)

    # ---- FLOAT ----
    elif isinstance(default, float):
        widget = QDoubleSpinBox()
        widget.setMinimum(spec.get("min", -999999.0))
        widget.setMaximum(spec.get("max", 999999.0))
        widget.setValue(default)
        widget.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        widget.setSingleStep(0.1)
        widget.setCorrectionMode(QAbstractSpinBox.CorrectionMode.CorrectToNearestValue)

    # ---- STRING ----
    else:
        widget = QLineEdit(str(default))
        widget.setFocusPolicy(Qt.FocusPolicy.ClickFocus)

    widget.setToolTip(tooltip)

    return label, widget


def update_box_options(schema: dict, box_widget: QWidget, set_function=None):
    """
    Dynamically populate a Qt box with config options from schema
    using a QFormLayout.
    """

    layout = box_widget.layout()

    # Ensure the layout is a QFormLayout
    if not isinstance(layout, QFormLayout):
        layout = QFormLayout()
        box_widget.setLayout(layout)

    # Clear old widgets
    clear_layout(layout)

    # Store widgets for later retrieval
    box_widget._config_widgets = {}

    # No config case
    if not schema:
        layout.addRow(QLabel("This element is not configurable."))
        return

    for param, spec in schema.items():
        label, widget = widget_from_default(param, spec)

        # Tooltip from description
        if "description" in spec:
            widget.setToolTip(spec["description"])
            label.setToolTip(spec["description"])

        layout.addRow(label, widget)

        box_widget._config_widgets[param] = widget
    
    if set_function:
        set_button_widget = QPushButton("Set options")
        set_button_widget.clicked.connect(set_function)
        layout.addRow(set_button_widget)

def read_config(box_widget):
    values = {}
    for key, w in box_widget._config_widgets.items():
        if hasattr(w, "value"):
            values[key] = w.value()
        elif hasattr(w, "isChecked"):
            values[key] = w.isChecked()
        elif hasattr(w, "currentText"):
            values[key] = w.currentText()
        else:
            values[key] = w.text()
    return values
