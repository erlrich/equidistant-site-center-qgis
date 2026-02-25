# -*- coding: utf-8 -*-
# ============================================================
# Equidistant Site Center - QGIS Plugin
#
# Copyright (c) 2026 Achmad Amrulloh
#
# Released under the MIT License.
# See LICENSE file for full license information.
# ============================================================

def classFactory(iface):
    from .equidistant_center import EquidistantCenterPlugin
    return EquidistantCenterPlugin(iface)
