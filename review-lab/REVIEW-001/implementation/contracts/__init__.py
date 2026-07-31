"""Mission Platform contracts v1 (REVIEW-001 vertical slice).

This package is THE seam between platform and payloads.
Rule: imports nothing from platform_host or payloads (pure).
Versioning: SemVer per contract; see CONTRACT_VERSIONS.
"""

CONTRACT_VERSIONS = {"control": "1.0.0", "data": "1.0.0", "manifest": "1.0.0"}
