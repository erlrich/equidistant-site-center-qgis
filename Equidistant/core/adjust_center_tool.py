# -*- coding: utf-8 -*-
# ============================================================
# Equidistant Site Center - QGIS Plugin
#
# Copyright (c) 2026 Achmad Amrulloh
#
# Released under the MIT License.
# See LICENSE file for full license information.
# ============================================================

from qgis.gui import QgsMapTool, QgsRubberBand

from qgis.core import (
    QgsProject, QgsGeometry, QgsVectorLayer, QgsFeature, QgsWkbTypes,
    QgsCoordinateTransform, QgsCoordinateReferenceSystem,
    QgsPalLayerSettings, QgsTextFormat, QgsTextBufferSettings,
    QgsVectorLayerSimpleLabeling, QgsSymbol, QgsSingleSymbolRenderer,
    QgsField, QgsMessageLog, Qgis
)
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtCore import QMetaType


class AdjustCenterTool(QgsMapTool):
    """
    UX:
    - Realtime preview
    - Click finalize
    - ESC cancel
    """

    def __init__(self, canvas, iface, source_points, crs_authid):
        super().__init__(canvas)

        self.canvas = canvas
        self.iface = iface

        self._v = source_points
        self._c = crs_authid

        self.setCursor(Qt.CursorShape.CrossCursor)

        prj = QgsProject.instance()
        self._x = prj.transformContext()

        self._l = QgsCoordinateReferenceSystem(self._c)
        self._m = self.canvas.mapSettings().destinationCrs()
        self._t = QgsCoordinateTransform(self._l, self._m, self._x)

        self._rb0 = QgsRubberBand(self.canvas, QgsWkbTypes.PointGeometry)
        self._rb0.setColor(Qt.GlobalColor.red)
        self._rb0.setWidth(8)

        self._rb1 = QgsRubberBand(self.canvas, QgsWkbTypes.LineGeometry)
        self._rb1.setColor(Qt.GlobalColor.yellow)
        self._rb1.setWidth(1)

        self._a = True

        self.iface.mainWindow().statusBar().showMessage(
            "Adjust Center: move mouse to preview, click to set, ESC to finish",
            5000
        )

    # -------------------------------------------------
    # Mouse move → preview
    # -------------------------------------------------
    def canvasMoveEvent(self, event):
        if not self._a:
            return

        c0 = self.toMapCoordinates(event.pos())

        self._rb0.reset(QgsWkbTypes.PointGeometry)
        self._rb1.reset(QgsWkbTypes.LineGeometry)

        self._rb0.addPoint(c0)

        for p in self._v:
            pm = self._t.transform(p)
            self._rb1.addGeometry(
                QgsGeometry.fromPolylineXY([c0, pm]),
                None
            )

    # -------------------------------------------------
    # Left click → finalize
    # -------------------------------------------------
    def canvasPressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            c0 = self.toMapCoordinates(event.pos())
            self._z()
            self._x1(c0)

    # -------------------------------------------------
    # ESC → cancel
    # -------------------------------------------------
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self._z()
            self._a = False
            self.setCursor(Qt.CursorShape.ArrowCursor)
            self.iface.mainWindow().statusBar().clearMessage()

            try:
                self.iface.plugin()._adjust_center_active = False
            except (AttributeError, RuntimeError) as e:
                QgsMessageLog.logMessage(
                    f"Adjust Center: failed to release flag — {e}",
                    "Equidistant Site Center",
                    Qgis.Info
                )

            self.canvas.unsetMapTool(self)

    # -------------------------------------------------
    # CLEAR PREVIEW
    # -------------------------------------------------
    def _z(self):
        self._rb0.reset(QgsWkbTypes.PointGeometry)
        self._rb1.reset(QgsWkbTypes.LineGeometry)

    # =================================================
    # GENERATE FINAL LAYERS
    # =================================================
    def _x1(self, c0):

        prj = QgsProject.instance()
        ctx = prj.transformContext()

        old_renderer = None
        old_labeling = None

        for lyr in prj.mapLayers().values():
            if lyr.name() == "Equidistant_Center_Distance":
                if lyr.renderer():
                    old_renderer = lyr.renderer().clone()
                if lyr.labeling():
                    old_labeling = lyr.labeling().clone()
                break

        projected_crs = QgsCoordinateReferenceSystem(self._c)
        map_crs = self.canvas.mapSettings().destinationCrs()

        to_projected = QgsCoordinateTransform(map_crs, projected_crs, ctx)
        to_map = QgsCoordinateTransform(projected_crs, map_crs, ctx)
        to_geo = QgsCoordinateTransform(
            projected_crs,
            QgsCoordinateReferenceSystem("EPSG:4326"),
            ctx
        )

        cm_proj = to_projected.transform(c0)

        for lyr in list(prj.mapLayers().values()):
            if lyr.name() in (
                "Equidistant_Center_Result",
                "Equidistant_Center_Distance"
            ):
                prj.removeMapLayer(lyr.id())

        ln = QgsVectorLayer(
            f"LineString?crs={map_crs.authid()}",
            "Equidistant_Center_Distance",
            "memory"
        )
        dp = ln.dataProvider()
        success = dp.addAttributes([QgsField("distance_m", QMetaType.Type.Double)])
        if not success:
            QgsMessageLog.logMessage(
                "Adjust Center: addAttributes failed for "
                "'Equidistant_Center_Distance' (line layer).",
                "Equidistant Site Center",
                Qgis.Warning
            )
        ln.updateFields()

        d = []

        for p_proj in self._v:
            dist = ((cm_proj.x() - p_proj.x()) ** 2 +
                    (cm_proj.y() - p_proj.y()) ** 2) ** 0.5

            cm_map = to_map.transform(cm_proj)
            p_map = to_map.transform(p_proj)

            g = QgsGeometry.fromPolylineXY([cm_map, p_map])

            f = QgsFeature()
            f.setGeometry(g)
            f.setAttributes([round(dist, 2)])
            success = dp.addFeature(f)
            if not success:
                QgsMessageLog.logMessage(
                    "Adjust Center: addFeature failed for "
                    "distance feature.",
                    "Equidistant Site Center",
                    Qgis.Warning
                )

            d.append(dist)

        ln.updateExtents()
        prj.addMapLayer(ln)

        if old_renderer:
            ln.setRenderer(old_renderer)
        if old_labeling:
            ln.setLabeling(old_labeling)
            ln.setLabelsEnabled(True)

        ln.triggerRepaint()

        pt = QgsVectorLayer(
            f"Point?crs={map_crs.authid()}",
            "Equidistant_Center_Result",
            "memory"
        )
        dp = pt.dataProvider()
        success = dp.addAttributes([
            QgsField("method", QMetaType.Type.QString),
            QgsField("delta_m", QMetaType.Type.Double),
            QgsField("valid", QMetaType.Type.Bool),
            QgsField("longitude", QMetaType.Type.Double),
            QgsField("latitude", QMetaType.Type.Double),
            QgsField("location", QMetaType.Type.QString),
            QgsField("status", QMetaType.Type.QString)
        ])
        if not success:
            QgsMessageLog.logMessage(
                "Adjust Center: addAttributes failed for "
                "'Equidistant_Center_Result' (point layer).",
                "Equidistant Site Center",
                Qgis.Warning
            )
        pt.updateFields()

        dl = max(d) - min(d) if d else 0.0

        cg = to_geo.transform(cm_proj)
        lon = round(cg.x(), 6)
        lat = round(cg.y(), 6)

        cm_map = to_map.transform(cm_proj)

        f = QgsFeature()
        f.setGeometry(QgsGeometry.fromPointXY(cm_map))
        f.setAttributes([
            "manual",
            round(dl, 2),
            True,
            lon,
            lat,
            f"{lon}, {lat}",
            "ADJUSTED"
        ])
        success = dp.addFeature(f)
        if not success:
            QgsMessageLog.logMessage(
                "Adjust Center: addFeature failed for "
                "center feature.",
                "Equidistant Site Center",
                Qgis.Warning
            )

        pt.updateExtents()
        prj.addMapLayer(pt)

        sm = QgsSymbol.defaultSymbol(pt.geometryType())
        sm.setSize(6)
        sm.setColor(Qt.GlobalColor.red)
        pt.setRenderer(QgsSingleSymbolRenderer(sm))
        pt.triggerRepaint()

        # Apply visual settings from plugin (ensure labeling active)
        try:
            self.iface.plugin().apply_visual_settings_realtime()
        except (AttributeError, RuntimeError) as e:
            QgsMessageLog.logMessage(
                f"Adjust Center: failed to apply visual settings — {e}",
                "Equidistant Site Center",
                Qgis.Info
            )