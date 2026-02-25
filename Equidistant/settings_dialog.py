# -*- coding: utf-8 -*-
# ============================================================
# Equidistant Site Center - QGIS Plugin
#
# Copyright (c) 2026 Achmad Amrulloh
#
# Released under the MIT License.
# See LICENSE file for full license information.
# ============================================================

from qgis.PyQt.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGroupBox,
    QLabel, QPushButton, QColorDialog, QSpinBox,
    QDoubleSpinBox, QComboBox, QLineEdit, QCheckBox
)

from qgis.PyQt.QtGui import QColor
from qgis.PyQt.QtCore import Qt
from .settings_manager import EquidistantCenterSettings


class ColorButton(QPushButton):
    """
    Simple color picker button
    """

    def __init__(self, color: QColor, parent=None):
        super().__init__(parent)
        self._color = color
        self.clicked.connect(self.pick_color)
        self._update_style()

    def pick_color(self):
        color = QColorDialog.getColor(self._color, self.parent())
        if color.isValid():
            self._color = color
            self._update_style()

    def color(self) -> QColor:
        return self._color

    def _update_style(self):
        self.setStyleSheet(
            "background-color: {};".format(self._color.name())
        )


class EquidistantCenterSettingsDialog(QDialog):

    def __init__(self, parent=None, plugin=None):
        super().__init__(parent)
        self.setWindowTitle("Equidistant Center – Visual Settings")
        self.setMinimumWidth(420)

        self.plugin = plugin
        self.settings = EquidistantCenterSettings()
        self._build_ui()


    # ---------------------------------------------------------
    # UI BUILDER
    # ---------------------------------------------------------

    def _build_ui(self):
        layout = QVBoxLayout(self)

        layout.addWidget(self._build_center_group())
        layout.addWidget(self._build_line_group())
        layout.addWidget(self._build_label_group())
        layout.addLayout(self._build_buttons())

    # ---------------------------------------------------------
    # GROUPS
    # ---------------------------------------------------------

    def _build_center_group(self):
        box = QGroupBox("Center Result")
        v = QVBoxLayout(box)
        
        shapes = [
            "circle", 
            "square", 
            "diamond", 
            "pentagon", 
            "hexagon", 
            "triangle", 
            "equilateral_triangle", 
            "star", 
            "arrow",
            "cross", 
            "cross_fill", 
            "cross2"
        ]

        # ===== FEASIBLE CENTER =====
        self.feasible_color = ColorButton(self.settings.feasible_color(), self)
        v.addLayout(self._row("Feasible color", self.feasible_color))

        self.feasible_size = self._spin_float(
            self.settings.feasible_size(), 1.0, 20.0
        )
        v.addLayout(self._row("Feasible size", self.feasible_size))

        self.feasible_shape = QComboBox()
        self.feasible_shape.addItems(shapes)
        self.feasible_shape.setCurrentText(self.settings.feasible_shape())
        v.addLayout(self._row("Feasible shape", self.feasible_shape))

        # ===== NOT FEASIBLE CENTER =====
        self.not_feasible_color = ColorButton(self.settings.not_feasible_color(), self)
        v.addLayout(self._row("Not feasible color", self.not_feasible_color))

        self.not_feasible_size = self._spin_float(
            self.settings.not_feasible_size(), 1.0, 20.0
        )
        v.addLayout(self._row("Not feasible size", self.not_feasible_size))

        self.not_feasible_shape = QComboBox()
        self.not_feasible_shape.addItems(shapes)
        self.not_feasible_shape.setCurrentText(self.settings.not_feasible_shape())
        v.addLayout(self._row("Not feasible shape", self.not_feasible_shape))

        return box


    def _build_line_group(self):
        box = QGroupBox("Distance Line")
        v = QVBoxLayout(box)

        self.line_color = ColorButton(self.settings.line_color(), self)
        v.addLayout(self._row("Line color", self.line_color))

        self.line_width = self._spin_float(
            self.settings.line_width(), 0.1, 5.0
        )
        v.addLayout(self._row("Line width", self.line_width))

        self.line_style = QComboBox()
        self.line_style.addItems(["solid", "dash"])
        self.line_style.setCurrentText(self.settings.line_style())
        v.addLayout(self._row("Line style", self.line_style))
        
        self.show_lines = QCheckBox("Show distance lines")
        self.show_lines.setChecked(self.settings.show_distance_lines())
        v.addWidget(self.show_lines)

        return box

    def _build_label_group(self):
        box = QGroupBox("Distance Label")
        v = QVBoxLayout(box)

        self.label_font = self._spin_int(
            self.settings.label_font_size(), 6, 20
        )
        v.addLayout(self._row("Font size", self.label_font))

        self.label_color = ColorButton(self.settings.label_color(), self)
        v.addLayout(self._row("Text color", self.label_color))

        self.label_buffer_size = self._spin_float(
            self.settings.label_buffer_size(), 0.0, 5.0
        )
        v.addLayout(self._row("Buffer size", self.label_buffer_size))

        self.label_buffer_color = ColorButton(self.settings.label_buffer_color(), self)
        v.addLayout(self._row("Buffer color", self.label_buffer_color))

        self.label_precision = self._spin_int(
            self.settings.label_precision(), 0, 3
        )
        v.addLayout(self._row("Precision", self.label_precision))

        self.label_unit = QLineEdit(self.settings.label_unit_suffix())
        v.addLayout(self._row("Unit suffix", self.label_unit))

        return box

    # ---------------------------------------------------------
    # BUTTONS
    # ---------------------------------------------------------

    def _build_buttons(self):
        h = QHBoxLayout()

        btn_apply = QPushButton("Apply")
        btn_reset = QPushButton("Reset to Default")
        btn_close = QPushButton("Close")

        btn_apply.clicked.connect(self.apply_settings)
        btn_reset.clicked.connect(self.reset_settings)
        btn_close.clicked.connect(self.close)

        h.addStretch()
        h.addWidget(btn_apply)
        h.addWidget(btn_reset)
        h.addWidget(btn_close)

        return h

    # ---------------------------------------------------------
    # HELPERS
    # ---------------------------------------------------------

    def _row(self, label_text, widget):
        h = QHBoxLayout()
        h.addWidget(QLabel(label_text))
        h.addStretch()
        h.addWidget(widget)
        return h

    def _spin_float(self, value, min_v, max_v):
        s = QDoubleSpinBox()
        s.setRange(min_v, max_v)
        s.setDecimals(2)
        s.setValue(float(value))
        return s

    def _spin_int(self, value, min_v, max_v):
        s = QSpinBox()
        s.setRange(min_v, max_v)
        s.setValue(int(value))
        return s

    # ---------------------------------------------------------
    # ACTIONS
    # ---------------------------------------------------------
    def apply_settings(self):
        s = self.settings

        s.set_value("center/feasible/color", self.feasible_color.color().name())
        s.set_value("center/feasible/size", self.feasible_size.value())
        s.set_feasible_shape(self.feasible_shape.currentText())

        s.set_value("center/not_feasible/color", self.not_feasible_color.color().name())
        s.set_value("center/not_feasible/size", self.not_feasible_size.value())
        s.set_not_feasible_shape(self.not_feasible_shape.currentText())

        s.set_value("line/color", self.line_color.color().name())
        s.set_value("line/width", self.line_width.value())
        s.set_value("line/style", self.line_style.currentText())
        s.set_value("line/show", self.show_lines.isChecked())

        s.set_value("label/font_size", self.label_font.value())
        s.set_value("label/color", self.label_color.color().name())
        s.set_value("label/buffer_size", self.label_buffer_size.value())
        s.set_value("label/buffer_color", self.label_buffer_color.color().name())

        # REALTIME APPLY
        if self.plugin:
            self.plugin.apply_visual_settings_realtime()



    def reset_settings(self):

        # Reset stored values
        self.settings.reset_to_default()

        # Reload UI values from defaults
        self.feasible_color._color = self.settings.feasible_color()
        self.feasible_color._update_style()
        self.feasible_size.setValue(self.settings.feasible_size())
        self.feasible_shape.setCurrentText(self.settings.feasible_shape())

        self.not_feasible_color._color = self.settings.not_feasible_color()
        self.not_feasible_color._update_style()
        self.not_feasible_size.setValue(self.settings.not_feasible_size())
        self.not_feasible_shape.setCurrentText(self.settings.not_feasible_shape())

        self.line_color._color = self.settings.line_color()
        self.line_color._update_style()
        self.line_width.setValue(self.settings.line_width())
        self.line_style.setCurrentText(self.settings.line_style())
        self.show_lines.setChecked(self.settings.show_distance_lines())

        self.label_font.setValue(self.settings.label_font_size())
        self.label_color._color = self.settings.label_color()
        self.label_color._update_style()
        self.label_buffer_size.setValue(self.settings.label_buffer_size())
        self.label_buffer_color._color = self.settings.label_buffer_color()
        self.label_buffer_color._update_style()

        # Apply immediately
        if self.plugin:
            self.plugin.apply_visual_settings_realtime()
