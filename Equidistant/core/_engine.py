# -*- coding: utf-8 -*-
# ============================================================
# Equidistant Site Center - QGIS Plugin
#
# Copyright (c) 2026 Achmad Amrulloh
#
# Released under the MIT License.
# See LICENSE file for full license information.
# ============================================================

from qgis.core import (
    QgsGeometry,
    QgsFeature,
    QgsVectorLayer,
    QgsField,
    QgsCoordinateTransform,
    QgsCoordinateReferenceSystem,
    QgsMessageLog,
    Qgis
)
from qgis.PyQt.QtCore import QMetaType

from ._e1 import _k


def _r1(p, a, c, x):
    """
    p : list QgsPointXY (ALREADY PROJECTED CRS - meters)
    a : projected CRS authid (unused but kept for compatibility)
    c : QgsMapCanvas (unused)
    x : QgsCoordinateTransformContext (unused)
    """

    # =========================================================
    # NO CRS TRANSFORM HERE
    # Engine now assumes projected CRS input (meters)
    # =========================================================

    if not p:
        return {
            "c_map": None,
            "c_geo": None,
            "delta": 0.0,
            "valid": False
        }

    # Least squares center (already in projected CRS)
    cm = _k(p)

    # Distance spread
    d = []
    for q in p:
        dx = cm.x() - q.x()
        dy = cm.y() - q.y()
        d.append((dx * dx + dy * dy) ** 0.5)

    dl = max(d) - min(d) if d else 0.0

    return {
        "c_map": cm,      # PROJECTED CRS
        "c_geo": None,    # handled outside engine
        "delta": round(dl, 2),
        "valid": True
    }


def _r2(crs):
    l1 = QgsVectorLayer(
        f"LineString?crs={crs.authid()}",
        "Equidistant_Center_Distance",
        "memory"
    )
    success = l1.dataProvider().addAttributes([
        QgsField("distance_m", QMetaType.Type.Double)
    ])
    if not success:
        QgsMessageLog.logMessage(
            "Failed to add attributes to Equidistant_Center_Distance layer",
            "Equidistant Site Center",
            Qgis.Critical
        )
    l1.updateFields()

    l2 = QgsVectorLayer(
        f"Point?crs={crs.authid()}",
        "Equidistant_Center_Result",
        "memory"
    )
    success = l2.dataProvider().addAttributes([
        QgsField("method", QMetaType.Type.QString),
        QgsField("delta_m", QMetaType.Type.Double),
        QgsField("valid", QMetaType.Type.Bool),
        QgsField("longitude", QMetaType.Type.Double),
        QgsField("latitude", QMetaType.Type.Double),
        QgsField("location", QMetaType.Type.QString),
        QgsField("status", QMetaType.Type.QString),
    ])
    if not success:
        QgsMessageLog.logMessage(
            "Failed to add attributes to Equidistant_Center_Result layer",
            "Equidistant Site Center",
            Qgis.Critical
        )
    l2.updateFields()

    return l1, l2