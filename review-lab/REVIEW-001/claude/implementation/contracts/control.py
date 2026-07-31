"""Control contract v1.0.0 — PayloadDriver lifecycle (ADR-CL-004).

The supervisor owns liveness (health polling, restart, rollback).
The driver owns its own cadence internally between start() and stop().
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping


class ContractError(Exception):
    """Base class for contract-level failures."""


class PolicyRejected(ContractError):
    """Raised by configure() when the supplied policy is invalid for this payload.

    Failure contract: supervisor keeps the previous policy in force.
    """


class CommandRejected(ContractError):
    """Raised by handle_command() for unknown/unauthorised commands (fail closed)."""


class HealthStatus(str, Enum):
    OK = "ok"
    DEGRADED = "degraded"
    FAILED = "failed"


@dataclass(frozen=True)
class PayloadPolicy:
    """Signed, platform-verified configuration handed to a payload."""

    revision: int
    settings: Mapping[str, Any]


@dataclass(frozen=True)
class HealthReport:
    status: HealthStatus
    detail: str = ""
    metrics: Mapping[str, float] = field(default_factory=dict)


@dataclass(frozen=True)
class Command:
    name: str
    args: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class CommandResult:
    ok: bool
    detail: str = ""
    data: Mapping[str, Any] = field(default_factory=dict)


class PayloadDriver(ABC):
    """Control-plane contract implemented by every payload (v1)."""

    @abstractmethod
    def configure(self, policy: PayloadPolicy) -> None:
        """Apply verified policy. Raise PolicyRejected on invalid policy."""

    @abstractmethod
    def start(self) -> None:
        """Begin domain work. Must return promptly; cadence is driver-internal."""

    @abstractmethod
    def stop(self, deadline_s: float) -> None:
        """Stop domain work within deadline_s seconds. Idempotent."""

    @abstractmethod
    def health(self) -> HealthReport:
        """Cheap, non-blocking health snapshot for the supervisor."""

    @abstractmethod
    def handle_command(self, cmd: Command) -> CommandResult:
        """Execute an allowlisted operator command. Unknown -> CommandRejected."""
