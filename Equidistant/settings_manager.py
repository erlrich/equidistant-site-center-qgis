# -*- coding: utf-8 -*-
# ============================================================
# Equidistant Site Center - QGIS Plugin
#
# Copyright (c) 2026 Achmad Amrulloh
#
# Released under the MIT License.
# See LICENSE file for full license information.
# ============================================================

from qgis.PyQt.QtCore import QSettings
from qgis.PyQt.QtGui import QColor
from qgis.PyQt.QtWidgets import QCheckBox


class EquidistantCenterSettings:
    """
    Centralized settings manager for Equidistant Center plugin
    Storage: QSettings (native QGIS)
    Scope: Visual only
    """

    ORG_NAME = "Dinzo"
    APP_NAME = "EquidistantCenter"

    def __init__(self):
        self._settings = QSettings(self.ORG_NAME, self.APP_NAME)

    # ------------------------------------------------------------------
    # DEFAULT VALUES (PLUGIN MUST WORK WITHOUT USER CONFIG)
    # ------------------------------------------------------------------

    DEFAULTS = {
        # Center - feasible
        "center/feasible/color": "#00FFFF",   # cyan
        "center/feasible/size": 6.5,

        # Center - not feasible
        "center/not_feasible/color": "#FF00FF",  # magenta
        "center/not_feasible/size": 6.5,

        # Center shape
        "center/feasible/shape": "circle",
        "center/not_feasible/shape": "diamond",

        # Distance line
        "line/color": "#FFFF00",   # yellow
        "line/width": 1.2,
        "line/style": "solid",

        # Distance label
        "label/font_size": 9,
        "label/color": "#222222",
        "label/buffer_size": 1.2,
        "label/buffer_color": "#FFFFFF",
        "label/precision": 1,
        "label/unit_suffix": " m",

        "line/show": True,
    }

    # ------------------------------------------------------------------
    # INTERNAL HELPERS
    # ------------------------------------------------------------------

    def _get(self, key):
        if self._settings.contains(key):
            return self._settings.value(key)
        return self.DEFAULTS[key]

    def _set(self, key, value):
        self._settings.setValue(key, value)

    # ------------------------------------------------------------------
    # CENTER SETTINGS
    # ------------------------------------------------------------------

    def feasible_color(self) -> QColor:
        return QColor(self._get("center/feasible/color"))

    def feasible_size(self) -> float:
        return float(self._get("center/feasible/size"))

    def not_feasible_color(self) -> QColor:
        return QColor(self._get("center/not_feasible/color"))

    def not_feasible_size(self) -> float:
        return float(self._get("center/not_feasible/size"))

    # ------------------------------------------------------------------
    # LINE SETTINGS
    # ------------------------------------------------------------------

    def line_color(self) -> QColor:
        return QColor(self._get("line/color"))

    def line_width(self) -> float:
        return float(self._get("line/width"))

    def line_style(self) -> str:
        """
        Returns: 'solid' or 'dash'
        """
        return str(self._get("line/style"))
    
    def show_distance_lines(self) -> bool:
        return self._get("line/show") in [True, "true", "True", 1]


    # ------------------------------------------------------------------
    # LABEL SETTINGS
    # ------------------------------------------------------------------

    def label_font_size(self) -> int:
        return int(self._get("label/font_size"))

    def label_color(self) -> QColor:
        return QColor(self._get("label/color"))

    def label_buffer_size(self) -> float:
        return float(self._get("label/buffer_size"))

    def label_buffer_color(self) -> QColor:
        return QColor(self._get("label/buffer_color"))

    def label_precision(self) -> int:
        return int(self._get("label/precision"))

    def label_unit_suffix(self) -> str:
        return str(self._get("label/unit_suffix"))
        
        
    # ===== CENTER SHAPE SETTINGS =====

    def feasible_shape(self) -> str:
        return str(self._get("center/feasible/shape"))

    def set_feasible_shape(self, v: str):
        self._set("center/feasible/shape", v)

    def not_feasible_shape(self) -> str:
        return str(self._get("center/not_feasible/shape"))

    def set_not_feasible_shape(self, v: str):
        self._set("center/not_feasible/shape", v)



    # ------------------------------------------------------------------
    # PUBLIC API (OPTIONAL – FOR FUTURE UI)
    # ------------------------------------------------------------------

    def set_value(self, key: str, value):
        """
        Generic setter (used later by Settings Dialog UI)
        """
        if key not in self.DEFAULTS:
            raise KeyError(f"Unknown setting key: {key}")
        self._set(key, value)

    def reset_to_default(self):
        """
        Reset all settings to default
        """
        for key, value in self.DEFAULTS.items():
            self._set(key, value)
