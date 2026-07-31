"""Minimal platform host for the REVIEW-001 vertical slice.

Simulates the edge agent's supervisor + data-plane spool in-process.
Honesty note: OS-level sandbox enforcement (systemd/cgroups, ADR-CL-005)
is NOT simulated here; SPIKE-01 on hardware validates that layer. What IS
real here: fail-closed manifest/policy validation, signed policy
verification, lifecycle, health-driven restart, channel enforcement,
backpressure, audit event trail.
"""
