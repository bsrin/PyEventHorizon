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

Each pixel launches a photon ray with position **p** and direction **d**.

Instead of traveling in straight lines, the ray is bent by gravity.

The motion is governed by:

[
\frac{d^2x^\mu}{d\lambda^2} + \Gamma^\mu_{\alpha\beta}\frac{dx^\alpha}{d\lambda}\frac{dx^\beta}{d\lambda}=0
]

These equations describe how light moves through curved spacetime.

Because solving them exactly is extremely expensive, the engine integrates the trajectory numerically using **Runge–Kutta 4th Order (RK4)**.

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

Light emitted from this gas is modified by the **relativistic Doppler factor**:

[
D = \frac{1}{\gamma (1-\beta \cos\theta)}
]

This causes:

* material moving **toward the observer** to appear brighter and bluer
* material moving **away** to appear dimmer and redder

This creates the asymmetric brightness seen in real black hole observations.

---

## Gravitational Redshift

Photons escaping the gravitational well lose energy.

Their wavelength shifts according to:

[
\nu_{obs} = \nu_{emit}\sqrt{1-\frac{r_s}{r}}
]

As rays approach the event horizon, light becomes increasingly redshifted and dim.

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

BLACKHOLE
│
├── engine
│   ├── camera.py
│   ├── fbo.py
│   ├── grid.py
│   ├── shader.py
│   └── window.py
│
├── physics
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
└── README.md

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
