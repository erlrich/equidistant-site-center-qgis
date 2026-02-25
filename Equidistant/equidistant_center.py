# -*- coding: utf-8 -*-
# ============================================================
# Equidistant Site Center - QGIS Plugin
#
# Copyright (c) 2026 Achmad Amrulloh
#
# Released under the MIT License.
# See LICENSE file for full license information.
# ============================================================

import os

from qgis.PyQt.QtWidgets import QAction, QMessageBox
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtCore import Qt, QSettings

from qgis.core import (
    QgsProject, QgsCoordinateTransform, QgsCoordinateReferenceSystem,
    QgsSimpleMarkerSymbolLayerBase, QgsWkbTypes,
    QgsFeature, QgsGeometry,
    QgsUnitTypes, QgsSymbol, QgsSingleSymbolRenderer,
    QgsRuleBasedRenderer, Qgis
)

from .equidistant_center_dialog import EquidistantCenterDialog
from .settings_manager import EquidistantCenterSettings
from .core._engine import _r1, _r2
from .settings_dialog import EquidistantCenterSettingsDialog
from .ui_about_dialog import EquidistantCenterAboutDialog
from .core.adjust_center_tool import AdjustCenterTool


class EquidistantCenterPlugin:

    def __init__(self, iface):
        self.iface = iface
        self.action = None
        self._adjust_center_active = False

    # =========================================================
    # FIRST RUN MESSAGE
    # =========================================================
    def show_first_run_message(self):
        settings = QSettings()
        key = "Equidistant_Site_Center/first_run_done"

        if settings.value(key, False, bool):
            return

        QMessageBox.information(
            self.iface.mainWindow(),
            "Equidistant Site Center",
            "Equidistant Site Center Plugin\n\n"
            "Finds the most balanced center point\n"
            "from multiple site locations using\n"
            "least-squares distance optimization.\n\n"
            "© 2026 Dinzo."
        )

        settings.setValue(key, True)

    # =========================================================
    # INIT GUI
    # =========================================================
    def initGui(self):

        main_menu = "Equidistant Site Center"

        # MAIN RUN
        self.action = QAction(
            QIcon(self._icon_path()),
            "Equidistant Site Center",
            self.iface.mainWindow()
        )
        self.action.triggered.connect(self.run)
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu(main_menu, self.action)

        # ADJUST CENTER
        icon_path = os.path.join(
            os.path.dirname(__file__),
            "icon",
            "center.png"
        )

        self.adjust_center_action = QAction(
            QIcon(icon_path),
            "Adjust Center",
            self.iface.mainWindow()
        )
        self.adjust_center_action.triggered.connect(
            self.activate_center_context_tool
        )
        self.iface.addToolBarIcon(self.adjust_center_action)
        self.iface.addPluginToMenu(main_menu, self.adjust_center_action)

        # VISUAL SETTINGS
        self.settings_action = QAction(
            QIcon(self._icon_settings_path()),
            "Visual Settings",
            self.iface.mainWindow()
        )
        self.settings_action.triggered.connect(self.open_settings)
        self.iface.addPluginToMenu(main_menu, self.settings_action)

        # ABOUT
        self.about_action = QAction(
            QIcon(self._icon_info_path()),
            "About",
            self.iface.mainWindow()
        )
        self.about_action.triggered.connect(self.open_about)
        self.iface.addPluginToMenu(main_menu, self.about_action)

    # =========================================================
    # UNLOAD
    # =========================================================
    def unload(self):
        main_menu = "Equidistant Site Center"

        for attr in [
            "action",
            "adjust_center_action",
            "settings_action",
            "about_action",
        ]:
            if hasattr(self, attr):
                try:
                    self.iface.removeToolBarIcon(getattr(self, attr))
                    self.iface.removePluginMenu(main_menu, getattr(self, attr))
                except Exception:
                    pass

        self._adjust_center_active = False

    # =========================================================
    # MAIN RUN LOGIC
    # =========================================================
    def run(self):

        self.show_first_run_message()

        layer = self.iface.activeLayer()

        if not layer or layer.geometryType() != QgsWkbTypes.PointGeometry:
            self.iface.messageBar().pushCritical(
                "Equidistant Site Center",
                "Select a POINT layer"
            )
            return

        selected = sorted(layer.selectedFeatures(), key=lambda f: f.id())

        if len(selected) < 2:
            self.iface.messageBar().pushMessage(
                "Equidistant Site Center",
                "Select at least 2 point features",
                level=Qgis.Warning,
                duration=5
            )
            return

        dlg = EquidistantCenterDialog(
            len(selected),
            layer.crs().authid(),
            self.iface.mainWindow()
        )

        if dlg.exec_() != dlg.Accepted:
            return

        tolerance = dlg.get_tolerance()

        ctx = QgsProject.instance().transformContext()
        target_crs = self._get_projected_crs(layer, selected)

        to_proj = QgsCoordinateTransform(layer.crs(), target_crs, ctx)
        back = QgsCoordinateTransform(target_crs, layer.crs(), ctx)

        pts_geo = [f.geometry().asPoint() for f in selected]
        pts_proj = [to_proj.transform(p) for p in pts_geo]

        self._adjust_source_points = pts_proj
        self._adjust_crs_authid = target_crs.authid()

        res = _r1(
            pts_proj,
            target_crs.authid(),
            self.iface.mapCanvas(),
            ctx
        )

        center_m = res["c_map"]
        center_final = back.transform(center_m)

        delta = res["delta"]
        valid = delta <= tolerance

        # REMOVE OLD LAYERS
        for lyr in list(QgsProject.instance().mapLayers().values()):
            if lyr.name().startswith("Equidistant_Center"):
                QgsProject.instance().removeMapLayer(lyr.id())

        line_layer, center_layer = _r2(layer.crs())
        pr = line_layer.dataProvider()

        for p_proj in pts_proj:

            dist = ((center_m.x() - p_proj.x())**2 +
                    (center_m.y() - p_proj.y())**2) ** 0.5

            p_geo = back.transform(p_proj)

            f = QgsFeature()
            f.setGeometry(QgsGeometry.fromPolylineXY([center_final, p_geo]))
            f.setAttributes([round(dist, 2)])
            pr.addFeature(f)

        QgsProject.instance().addMapLayer(line_layer)

        symbol = QgsSymbol.defaultSymbol(line_layer.geometryType())
        line_layer.setRenderer(QgsSingleSymbolRenderer(symbol))

        pr = center_layer.dataProvider()

        lon = round(center_final.x(), 6)
        lat = round(center_final.y(), 6)

        f = QgsFeature()
        f.setGeometry(QgsGeometry.fromPointXY(center_final))
        f.setAttributes([
            "least_squares",
            round(delta, 2),
            valid,
            lon,
            lat,
            f"{lon}, {lat}",
            "AUTO"
        ])
        pr.addFeature(f)

        QgsProject.instance().addMapLayer(center_layer)

        self.apply_visual_settings_realtime()

        self.iface.messageBar().pushInfo(
            "Equidistant Site Center",
            f"Δ={round(delta, 2)} m"
        )

    # =========================================================
    # ADJUST CENTER TOOL
    # =========================================================
    def activate_center_context_tool(self):

        if not hasattr(self, "_adjust_source_points") or not self._adjust_source_points:
            QMessageBox.warning(
                self.iface.mainWindow(),
                "Adjust Center",
                "Run calculation first."
            )
            return

        self._adjust_center_active = True

        self.adjust_center_tool = AdjustCenterTool(
            self.iface.mapCanvas(),
            self.iface,
            self._adjust_source_points,
            self._adjust_crs_authid
        )

        self.iface.mapCanvas().setMapTool(self.adjust_center_tool)

    # =========================================================
    # VISUAL SETTINGS
    # =========================================================
    def apply_visual_settings_realtime(self):

        settings = EquidistantCenterSettings()
        project = QgsProject.instance()

        center_layer = None
        line_layer = None

        for lyr in project.mapLayers().values():
            if lyr.name() == "Equidistant_Center_Result":
                center_layer = lyr
            elif lyr.name() == "Equidistant_Center_Distance":
                line_layer = lyr

        # =================================================
        # CENTER RESULT (2 RULES)
        # =================================================
        if center_layer:

            root = QgsRuleBasedRenderer.Rule(None)

            # FEASIBLE
            sym_ok = QgsSymbol.defaultSymbol(center_layer.geometryType())
            sym_ok.setColor(settings.feasible_color())
            sym_ok.setSize(settings.feasible_size())
            self._apply_marker_shape(sym_ok, settings.feasible_shape())

            r_ok = QgsRuleBasedRenderer.Rule(sym_ok)
            r_ok.setFilterExpression('"valid" = true')
            r_ok.setLabel("FEASIBLE Center")

            # NOT FEASIBLE
            sym_bad = QgsSymbol.defaultSymbol(center_layer.geometryType())
            sym_bad.setColor(settings.not_feasible_color())
            sym_bad.setSize(settings.not_feasible_size())
            self._apply_marker_shape(sym_bad, settings.not_feasible_shape())

            r_bad = QgsRuleBasedRenderer.Rule(sym_bad)
            r_bad.setFilterExpression('"valid" = false')
            r_bad.setLabel("NOT FEASIBLE Center")

            root.appendChild(r_ok)
            root.appendChild(r_bad)

            center_layer.setRenderer(QgsRuleBasedRenderer(root))
            center_layer.triggerRepaint()

        # =================================================
        # DISTANCE LINE (WITH LABEL RESTORED)
        # =================================================
        if line_layer:

            symbol = QgsSymbol.defaultSymbol(line_layer.geometryType())
            sl = symbol.symbolLayer(0)
            sl.setWidth(settings.line_width())
            sl.setColor(settings.line_color())
            sl.setPenStyle(
                Qt.DashLine if settings.line_style() == "dash" else Qt.SolidLine
            )

            line_layer.setRenderer(QgsSingleSymbolRenderer(symbol))

            # -------------------------------
            # LABELING (RESTORED)
            # -------------------------------
            from qgis.core import (
                QgsPalLayerSettings,
                QgsTextFormat,
                QgsTextBufferSettings,
                QgsVectorLayerSimpleLabeling
            )

            pal = QgsPalLayerSettings()
            pal.fieldName = 'round("distance_m") || \' m\''
            pal.isExpression = True
            pal.placement = QgsPalLayerSettings.Curved
            pal.enabled = True

            tf = QgsTextFormat()
            tf.setSize(settings.label_font_size())
            tf.setColor(settings.label_color())

            buf = QgsTextBufferSettings()
            buf.setEnabled(True)
            buf.setSize(settings.label_buffer_size())
            buf.setColor(settings.label_buffer_color())

            tf.setBuffer(buf)
            pal.setFormat(tf)

            line_layer.setLabeling(QgsVectorLayerSimpleLabeling(pal))
            line_layer.setLabelsEnabled(True)

            line_layer.triggerRepaint()

        self.iface.mapCanvas().refresh()

    # =========================================================
    # SETTINGS / ABOUT
    # =========================================================
    def open_settings(self):
        dlg = EquidistantCenterSettingsDialog(self.iface.mainWindow(), plugin=self)
        dlg.exec_()

    def open_about(self):
        dlg = EquidistantCenterAboutDialog(self.iface.mainWindow())
        dlg.exec_()

    # =========================================================
    # HELPERS
    # =========================================================
    def _icon_path(self):
        return os.path.join(os.path.dirname(__file__), "icon", "new_site.png")

    def _icon_settings_path(self):
        return os.path.join(os.path.dirname(__file__), "icon", "settings.png")

    def _icon_info_path(self):
        return os.path.join(os.path.dirname(__file__), "icon", "info.png")

    def _apply_marker_shape(self, symbol, shape_name):

        sl = symbol.symbolLayer(0)
        if not isinstance(sl, QgsSimpleMarkerSymbolLayerBase):
            return

        mapping = {
            "circle": QgsSimpleMarkerSymbolLayerBase.Circle,
            "square": QgsSimpleMarkerSymbolLayerBase.Square,
            "diamond": QgsSimpleMarkerSymbolLayerBase.Diamond,
            "pentagon": QgsSimpleMarkerSymbolLayerBase.Pentagon,
            "hexagon": QgsSimpleMarkerSymbolLayerBase.Hexagon,
            "triangle": QgsSimpleMarkerSymbolLayerBase.Triangle,
            "equilateral_triangle": QgsSimpleMarkerSymbolLayerBase.EquilateralTriangle,
            "star": QgsSimpleMarkerSymbolLayerBase.Star,
            "arrow": QgsSimpleMarkerSymbolLayerBase.Arrow,
            "cross": QgsSimpleMarkerSymbolLayerBase.Cross,
            "cross_fill": QgsSimpleMarkerSymbolLayerBase.CrossFill,
            "cross2": QgsSimpleMarkerSymbolLayerBase.Cross2,
        }

        sl.setShape(mapping.get(shape_name.lower(), QgsSimpleMarkerSymbolLayerBase.Circle))

    def _get_projected_crs(self, layer, selected_features):

        layer_crs = layer.crs()

        if layer_crs.mapUnits() == QgsUnitTypes.DistanceMeters:
            return layer_crs

        lons = [f.geometry().asPoint().x() for f in selected_features]
        lats = [f.geometry().asPoint().y() for f in selected_features]

        avg_lon = sum(lons) / len(lons)
        avg_lat = sum(lats) / len(lats)

        zone = int((avg_lon + 180) / 6) + 1

        if avg_lat >= 0:
            epsg = 32600 + zone
        else:
            epsg = 32700 + zone

        return QgsCoordinateReferenceSystem(f"EPSG:{epsg}")