# -*- coding: utf-8 -*-
# ============================================================
# Equidistant Site Center - QGIS Plugin
#
# Copyright (c) 2026 Achmad Amrulloh
#
# Released under the MIT License.
# See LICENSE file for full license information.
# ============================================================

from qgis.PyQt.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
from qgis.PyQt.QtGui import QFont
from qgis.PyQt.QtCore import Qt


class EquidistantCenterAboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About Equidistant Site Center")
        self.setFixedWidth(440)

        layout = QVBoxLayout(self)

        title = QLabel("Equidistant Site Center")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)

        subtitle = QLabel("Spatial Balancing Tool for QGIS")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: gray; margin-bottom: 8px;")

        info = QLabel(
            "Equidistant Site Center QGIS Plugin\n\n"
            "Computes an optimized spatial center point\n"
            "from multiple site locations using\n"
            "Equal-Distance Optimization.\n\n"
            "The algorithm iteratively minimizes\n"
            "distance variance between the center\n"
            "and all selected sites, producing\n"
            "a more spatially balanced result\n"
            "compared to simple centroid methods.\n\n"
            "Professional Edition available for\n"
            "advanced workflow automation,\n"
            "multi-session management,\n"
            "and structured reporting.\n\n"
            "Author  : Achmad Amrulloh\n"
            "LinkedIn: https://www.linkedin.com/in/achmad-amrulloh/\n\n"
            "© 2026 Achmad Amrulloh. Released under the MIT License."
        )

        info.setAlignment(Qt.AlignCenter)
        info.setWordWrap(True)
        info.setStyleSheet("margin-top: 10px; margin-bottom: 10px;")

        btn = QPushButton("OK")
        btn.setFixedWidth(80)
        btn.clicked.connect(self.accept)

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(info)
        layout.addStretch()
        layout.addWidget(btn, 0, Qt.AlignCenter)

