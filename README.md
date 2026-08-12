# Mission Platform

Mission Platform is an open, modular, AI-native and human-governed reference implementation of the Mission Framework.

It is documentation-first, technology-independent and designed to maintain an explicit connection between real-world purpose, architecture, implementation, operations and evidence.

## Start here

1. [Mission Book](docs/book/mission-book.md)
2. [Guiding Principles](docs/principles/guiding-principles.md)
3. [The Reality Principle](docs/principles/reality-principle.md)
4. [Architecture Overview](docs/architecture/overview.md)
5. [Trust, Edge and Device Adapter Model](docs/architecture/trust-edge-device-model.md)
6. [Mission Reference Model](docs/architecture/mission-reference-model.md)
7. [Mission Meta Model](docs/architecture/mission-meta-model.md)
8. [Mission Architecture Tests](docs/architecture/architecture-tests.md)
9. [Architecture Decision Records](docs/adr/README.md)

## Status

**Foundation 0.2 — Trust, Edge & Modularity Draft**

Foundation 0.2 adds Trust as the primary architectural quality, elevates Availability and Reliability for critical infrastructure, defines the edge as a local Policy Enforcement Point and Execution Authority, introduces signed Action Requests rather than transparent remote commands, and establishes modular Device Adapters for vendor/device support including firmware, parameters, telemetry and logging.

## Core ideas

> The model describes reality—not software.

> The headend requests; the edge decides and executes.

Architecture must preserve an unbroken and bidirectional relationship between reality, mission, implementation, operation and evidence. Essential local missions should remain autonomous when external dependencies fail.

## License

Licensed under the Apache License, Version 2.0.
