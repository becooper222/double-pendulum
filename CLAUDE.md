# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Browser-based double pendulum physics simulator using **PyScript** (Python running in the browser via Pyodide/WebAssembly). No build step, no server, no package manager — just open `index.html` in a browser.

## Running

Open `index.html` directly in a browser. No server or install required. PyScript and NumPy are loaded from CDN at runtime.

## Architecture

- **`index.html`** — Entry point. Loads PyScript (2023.03.1), configures it to fetch `double_pendulum.py` and `app.py`, and defines the UI (controls + HTML5 canvas). Uses `<py-config>` for PyScript setup and `<py-script src="app.py">` to run the app.
- **`double_pendulum.py`** — Pure physics engine. `DoublePendulum` class implements equations of motion with RK4 numerical integration. Maintains state (angles, angular velocities, positions) and tip trail history. No browser/DOM dependencies.
- **`app.py`** — Browser glue layer. Uses `js` and `pyodide.ffi` to bridge Python↔JavaScript. Handles canvas drawing, animation loop (`requestAnimationFrame`), UI event binding, and simulation lifecycle (init/play/pause/restart). All DOM interaction lives here.
- **`style.css`** — Styles with an `.embedded` layout mode (compact controls, no padding) designed for iframe embedding.

## Key Technical Details

- Physics runs in Python (via Pyodide), rendering uses HTML5 Canvas API called from Python through `js` module
- Animation uses `requestAnimationFrame` with real-time delta calculation; physics steps are adjusted to match wall-clock time
- Gravity is negative (`-9.8`) in the physics model; y-axis is inverted (positive = up) in `DoublePendulum`
- Trail history defaults to 1000 points; "Full History" mode sets it to 1M points (effectively unlimited)
- `test.html`, `simple-test.html`, `minimal-test.html` are debug/test pages, not production files
