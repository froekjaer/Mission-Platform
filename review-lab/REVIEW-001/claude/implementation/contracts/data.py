"""Data contract v1.0.0 — classified channels (ADR-CL-004).

Three kinds: blob, timeseries, event. Every channel carries a data
classification and a retention class; the platform enforces both.
Personal-data classifications are forbidden on timeseries/event kinds in v1
(privacy architecture, security-compliance §3).
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping


class ChannelKind(str, Enum):
    BLOB = "blob"
    TIMESERIES = "timeseries"
    EVENT = "event"


class Classification(str, Enum):
    PERSONAL_IMAGES = "personal-images"
    PERSONAL_OTHER = "personal-other"
    PROCESS_TELEMETRY = "process-telemetry"
    OPERATIONAL = "operational"
    PUBLIC = "public"


PERSONAL_CLASSIFICATIONS = {Classification.PERSONAL_IMAGES, Classification.PERSONAL_OTHER}

# Kinds allowed to carry personal data in contract v1 (schema-enforced).
PERSONAL_DATA_KINDS = {ChannelKind.BLOB}


class DataPlaneError(Exception):
    """Base class for data-plane failures."""


class Backpressure(DataPlaneError):
    """Spool/transport is full. Payload must apply its declared strategy."""

    def __init__(self, retry_after_s: float) -> None:
        super().__init__(f"backpressure, retry after {retry_after_s}s")
        self.retry_after_s = retry_after_s


class UndeclaredChannel(DataPlaneError):
    """Write to a channel not declared in the manifest (fail closed)."""


@dataclass(frozen=True)
class ChannelDecl:
    name: str
    kind: ChannelKind
    classification: Classification
    retention_class: str


@dataclass(frozen=True)
class BlobMeta:
    content_type: str
    captured_at: str  # ISO 8601 UTC
    attributes: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class TimeseriesPoint:
    ts: str  # ISO 8601 UTC
    value: float
    labels: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class Event:
    ts: str
    kind: str
    detail: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class PutReceipt:
    channel: str
    object_id: str


class DataSink(ABC):
    """Provided BY the platform TO the payload. The payload's only data exit."""

    @abstractmethod
    def put_blob(self, channel: str, payload: bytes, meta: BlobMeta) -> PutReceipt: ...

    @abstractmethod
    def put_point(self, channel: str, point: TimeseriesPoint) -> PutReceipt: ...

    @abstractmethod
    def put_event(self, channel: str, event: Event) -> PutReceipt: ...
