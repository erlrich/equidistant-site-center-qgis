# -*- coding: utf-8 -*-
# ============================================================
# Equidistant Site Center - QGIS Plugin
#
# Copyright (c) 2026 Achmad Amrulloh
#
# Released under the MIT License.
# See LICENSE file for full license information.
# ============================================================

from qgis.PyQt.QtWidgets import QDialog, QLabel, QSpinBox, QPushButton, QVBoxLayout, QHBoxLayout


class EquidistantCenterDialog(QDialog):

    def __init__(self, selected_count=0, crs_authid="", parent=None):
        super().__init__(parent)
        self.setWindowTitle("Equidistant Site Center")
        self.setMinimumWidth(300)

        self.label_selected = QLabel(f"Selected sites: {selected_count}")
        self.label_crs = QLabel(f"CRS: {crs_authid}")

        self.spin = QSpinBox()
        self.spin.setRange(1, 1000)
        self.spin.setValue(25)

        btn_ok = QPushButton("Calculate")
        btn_close = QPushButton("Close")

        lay = QVBoxLayout()
        lay.addWidget(self.label_selected)
        lay.addWidget(self.label_crs)

        h = QHBoxLayout()
        h.addWidget(QLabel("Tolerance (m):"))
        h.addWidget(self.spin)
        lay.addLayout(h)

        hb = QHBoxLayout()
        hb.addStretch()
        hb.addWidget(btn_ok)
        hb.addWidget(btn_close)
        lay.addLayout(hb)

        self.setLayout(lay)

        btn_close.clicked.connect(self.reject)
        btn_ok.clicked.connect(self.accept)

    def get_tolerance(self):
        return self.spin.value()
