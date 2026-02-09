# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Browser-based double pendulum chaos demo — two pendulums side-by-side with slightly different initial conditions, demonstrating sensitivity to initial conditions. Pure HTML/JS/Canvas, no external dependencies. Just open `index.html` in a browser.

## Running

Open `index.html` directly in a browser. No server, build step, or install required.

## Architecture

- **`index.html`** — Single-file app. Contains all HTML, the `DoublePendulum` JS class (RK4 physics engine ported from the original Python), canvas rendering, animation loop, and UI event handling. Two canvases side-by-side.
- **`style.css`** — Dark theme layout with controls bar, two-panel canvas area, and status bar. Responsive (stacks vertically on mobile).
- **`double_pendulum.py`** — Original Python physics engine (kept as reference, not loaded at runtime).
- **`app.py`** — Former PyScript glue layer (kept as reference, not loaded at runtime).

## Key Technical Details

- Physics: RK4 integration, fixed dt=0.01s, accumulator pattern syncs physics to wall-clock time
- Two `DoublePendulum` instances: A uses (θ₁, θ₂), B uses (θ₁ + ε, θ₂) where ε defaults to 0.001°
- Gravity is positive (9.8) in the JS version; y-axis points down (sin for x, cos for y)
- Canvas uses DPR-aware sizing via `ResizeObserver`
- Pendulum A: blue/red bobs, orange trail. Pendulum B: green/purple bobs, cyan trail
- Trail history capped at 2000 points
