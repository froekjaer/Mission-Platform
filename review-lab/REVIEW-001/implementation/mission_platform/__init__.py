"""mission_platform — vertical slice root package.

This package is the executable proof for REVIEW-001 (Z.ai submission). It
implements the contract spike (Migration Step 0): a minimal platform core
+ a timelapse payload that wraps existing capture logic behind the contract
+ a stub second payload to prove Extensibility.

It is NOT a feature-complete reimplementation of TimeLapse Pro's 82
requirements. It proves:
  - the contract fits reality (ADR-Z-001);
  - isolation/enforcement is real and fail-closed (ADR-Z-002);
  - a second payload loads without platform changes (Extensibility).
"""
