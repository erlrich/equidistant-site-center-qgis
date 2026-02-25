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
    QgsField
)
from qgis.PyQt.QtCore import Qt
from PyQt5.QtCore import QVariant


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

        self.setCursor(Qt.CrossCursor)

        prj = QgsProject.instance()
        self._x = prj.transformContext()

        self._l = QgsCoordinateReferenceSystem(self._c)
        self._m = self.canvas.mapSettings().destinationCrs()
        self._t = QgsCoordinateTransform(self._l, self._m, self._x)

        self._rb0 = QgsRubberBand(self.canvas, QgsWkbTypes.PointGeometry)
        self._rb0.setColor(Qt.red)
        self._rb0.setWidth(8)

        self._rb1 = QgsRubberBand(self.canvas, QgsWkbTypes.LineGeometry)
        self._rb1.setColor(Qt.yellow)
        self._rb1.setWidth(1)

        self._a = True

        self.iface.mainWindow().statusBar().showMessage(
            "Adjust Center: move mouse to preview, click to set, ESC to finish"
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
        if event.button() == Qt.LeftButton:
            c0 = self.toMapCoordinates(event.pos())
            self._z()
            self._x1(c0)

    # -------------------------------------------------
    # ESC → cancel
    # -------------------------------------------------
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self._z()
            self._a = False
            self.setCursor(Qt.ArrowCursor)
            self.iface.mainWindow().statusBar().clearMessage()

            try:
                self.iface.plugin()._adjust_center_active = False
            except Exception:
                pass

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
        dp.addAttributes([QgsField("distance_m", QVariant.Double)])
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
            dp.addFeature(f)

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
        dp.addAttributes([
            QgsField("method", QVariant.String),
            QgsField("delta_m", QVariant.Double),
            QgsField("valid", QVariant.Bool),
            QgsField("longitude", QVariant.Double),
            QgsField("latitude", QVariant.Double),
            QgsField("location", QVariant.String),
            QgsField("status", QVariant.String)
        ])
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
        dp.addFeature(f)

        pt.updateExtents()
        prj.addMapLayer(pt)

        sm = QgsSymbol.defaultSymbol(pt.geometryType())
        sm.setSize(6)
        sm.setColor(Qt.red)
        pt.setRenderer(QgsSingleSymbolRenderer(sm))
        pt.triggerRepaint()
        
        # Apply visual settings from plugin (ensure labeling active)
        try:
            self.iface.plugin().apply_visual_settings_realtime()
        except Exception:
            pass