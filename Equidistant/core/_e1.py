# -*- coding: utf-8 -*-
# ============================================================
# Equidistant Site Center - QGIS Plugin
#
# Copyright (c) 2026 Achmad Amrulloh
#
# Released under the MIT License.
# See LICENSE file for full license information.
# ============================================================

import math

def _a(p, q):
    x = p.x() - q.x()
    y = p.y() - q.y()
    return math.sqrt(x * x + y * y)

def _k(v, i=100, s=0.1, t=0.01):
    n = len(v)
    if n == 0:
        return None

    cx = sum(p.x() for p in v) / n
    cy = sum(p.y() for p in v) / n
    c = v[0].__class__(cx, cy)

    for _ in range(i):
        d = [_a(c, p) for p in v]
        m = sum(d) / n if n else 0.0

        gx = 0.0
        gy = 0.0

        for p, r in zip(v, d):
            if r == 0:
                continue
            u = r - m
            gx += u * (c.x() - p.x()) / r
            gy += u * (c.y() - p.y()) / r

        nc = v[0].__class__(
            c.x() - s * gx,
            c.y() - s * gy
        )

        if _a(c, nc) < t:
            break

        c = nc

    return c
