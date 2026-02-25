# equidistant-site-center-qgis
Advanced QGIS plugin for equidistant site center calculation
# Equidistant Site Center  
### Engineering-Grade Spatial Optimization for QGIS

Equidistant Site Center is a professional QGIS plugin designed for RF engineers, telecom planners, and GIS analysts who require a spatially balanced center point derived from multiple site locations.

Unlike simple centroid calculations, this plugin applies a least-squares distance optimization approach to minimize distance variance across all selected sites.

---

## 🚀 Overview

In network planning and infrastructure deployment, selecting a center reference using geometric centroid methods can introduce spatial bias.

Equidistant Site Center computes a technically balanced center by minimizing radial deviation between the center and all selected site coordinates.

This produces a more neutral and engineering-relevant reference point for:

- RF planning
- Cluster hub analysis
- Infrastructure balancing
- Deployment feasibility assessment
- Spatial optimization workflows

---

## 🎯 Core Capabilities

- Least-Squares Equidistant Center Calculation
- Automatic CRS Handling (Global UTM-safe)
- Radial Distance Mapping
- Real-time Visual Customization
- Interactive Center Adjustment Tool
- Multi-Result Session Management
- Export to Excel (XLSX)
- Export to GeoPackage (GPKG)
- License-protected deployment

---

## 🧠 How It Works

1. Select 2 or more point features in QGIS.
2. The plugin automatically detects an appropriate projected CRS.
3. Coordinates are transformed safely.
4. A least-squares optimization engine computes the balanced center.
5. Radial deviation lines are generated.
6. Results can be stored in session and exported.

The system is fully CRS-aware and handles global datasets reliably.

---

## 🛠 Technical Architecture

- Built for QGIS 3.40 LTR+
- CRS-safe transformation pipeline
- Automatic UTM zone detection
- Memory-layer lifecycle control
- Reload-safe toolbar management
- Export modules hardened for production
- Visual settings applied without recalculation

This plugin is designed to behave as a stable engineering tool — not a prototype script.

---

## 📦 Session Management

Multiple optimization results can be stored within a session.

Session outputs can be exported to:

- XLSX (structured report format)
- GeoPackage (CRS-safe vector layers)

All exported geometries preserve spatial integrity.

---

## 🧩 Use Cases

- RF cluster balancing
- Hub location pre-feasibility study
- Site distribution evaluation
- Distance neutrality analysis
- Multi-site infrastructure planning

---

## 🔐 Licensing

This plugin uses device-based license activation.

For activation inquiries:
Please contact the author.

---

## 👨‍💻 Author

Achmad Amrulloh  
Telecom Engineer → Spatial Software Developer  

© 2026 Dinzo. All rights reserved.

---

## 📌 Roadmap

Future development may include:

- Weighted site optimization
- Batch scenario processing
- Sector-based balancing
- Automated PDF reporting
- Enterprise multi-user licensing
- Integration with RF KPI datasets

---

## 🤝 Collaboration

If you work in:

- RF Planning
- Network Optimization
- Telecom Infrastructure Strategy
- GIS-based Spatial Analysis

Feel free to connect and exchange ideas.

---

## ⚖️ Disclaimer

This tool assists spatial decision-making and should be used as a technical support system within professional engineering workflows.
