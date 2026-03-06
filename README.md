# Project EventHorizon (PyEventHorizon)

**Project EventHorizon** is a real-time Kerr spacetime ray tracer built from scratch in **Python and GLSL**.

Instead of relying on game engine tricks or fake post-processing effects, this engine numerically integrates **relativistic photon trajectories directly on the GPU**, producing gravitational lensing, photon rings, Doppler beaming, and gravitational redshift at interactive frame rates.

The simulation runs on a **custom OpenGL 4.3 pipeline**, where the black hole is defined purely by the **Kerr spacetime metric**, not by geometry.

---

# Overview

Every pixel launches a photon ray into curved spacetime.

That ray is numerically integrated step-by-step through the gravitational field of a rotating black hole.
The final color of each pixel represents the accumulated light along that curved path.

This produces real-time visualizations of:

* gravitational lensing
* photon rings
* relativistic Doppler beaming
* gravitational redshift

---

# How The Physics Works

## Kerr Spacetime

The black hole is modeled using the **Kerr metric**, which describes spacetime around a rotating mass.

The key parameters are:

* **M** → black hole mass
* **a** → spin parameter

These control how strongly spacetime bends and twists around the singularity.

---

## Photon Trajectories

Light rays follow the geodesics of curved spacetime.

In general relativity this is described by the geodesic equation:

d²xᵘ / dλ² + Γᵘₐᵦ (dxᵅ/dλ)(dxᵝ/dλ) = 0

Solving this equation analytically in real time is extremely expensive, so the engine integrates photon trajectories numerically using a **Runge–Kutta 4th Order (RK4)** solver on the GPU.

This allows the renderer to reproduce effects such as:

* Einstein rings
* multiple photon orbits
* extreme light bending near the event horizon

---

## Runge–Kutta Integration

At each step the engine evaluates the gravitational acceleration and updates the ray direction.

The RK4 integrator provides stable trajectories even when rays orbit the black hole multiple times.

This allows the renderer to reproduce effects like:

* Einstein rings
* multiple photon orbits
* extreme light bending near the horizon

---

## Doppler Beaming

Gas orbiting the black hole moves at relativistic speeds.

The observed brightness is modified by the relativistic Doppler factor:

D = 1 / (γ (1 − β cosθ))

Where:

* β = v / c
* γ = 1 / √(1 − β²)

This causes:

* material moving **toward the observer** to appear brighter and bluer
* material moving **away** to appear dimmer and redder

This produces the asymmetric brightness seen in real black hole observations.

---

## Gravitational Redshift

Photons escaping a gravitational well lose energy.

The observed frequency is approximately:

ν_obs = ν_emit √(1 − r_s / r)

Where:

* r_s is the Schwarzschild radius
* r is the photon distance from the black hole center

As photons approach the event horizon, their wavelength stretches and the light becomes increasingly redshifted and dim.


---

# Rendering Architecture

## GPU Ray Tracing

Each pixel runs a **GLSL fragment shader** that integrates a photon path through spacetime.

The simulation uses:

* adaptive step sizes
* volumetric light accumulation
* transmittance tracking

to simulate light propagation.

---

## Procedural Starfield

The background universe is generated using a **hash-based procedural star generator**, avoiding static skybox textures.

---

## Temporal Anti-Aliasing (TAA)

A custom **ping-pong framebuffer accumulation system** blends frames using a Halton sequence jitter pattern.

This reduces noise from volumetric sampling while preserving fine lensing detail.

---

# Project Structure

## Project Structure

PyEventHorizon
│
├── engine
│   ├── __init__.py
│   ├── camera.py
│   ├── fbo.py
│   ├── grid.py
│   ├── shader.py
│   └── window.py
│
├── physics
│   ├── __init__.py
│   ├── entities.py
│   └── params.py
│
├── shaders
│   ├── grid.frag
│   ├── grid.vert
│   ├── kerr_raytracer.frag
│   ├── quad.vert
│   └── taa_resolve.frag
│
├── main.py
├── requirements.txt
├── README.md
└── .gitignore


---

# Installation

The engine requires **Python 3.9+** and a GPU supporting **OpenGL 4.3**.

### Install Dependencies

```
pip install -r requirements.txt
```

---

# Run

```
python main.py
```

---

# Controls

| Key         | Action      |
| ----------- | ----------- |
| **W A S D** | Move camera |
| **Mouse**   | Look around |
| **ESC**     | Exit        |

---

# Technical Highlights

* Real-time relativistic ray tracing
* RK4 photon trajectory integration
* Kerr spacetime lensing
* Relativistic Doppler beaming
* Gravitational redshift
* Procedural deep-space rendering
* Temporal anti-aliasing pipeline

---

# Author

**bsrin**

