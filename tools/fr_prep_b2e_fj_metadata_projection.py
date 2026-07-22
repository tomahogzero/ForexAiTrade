"""Strict timestamp projection for FR-Prep-B2e FJ metadata."""

from __future__ import annotations

import re
from datetime import datetime
from typing import Final


class FjMetadataTimestampValidationError(ValueError):
    """A stable, field-scoped timestamp validation failure."""

    def __init__(self, validation_code: str, field_name: str) -> None:
        self.validation_code = validation_code
        self.field_name = field_name
        super().__init__(f"{validation_code}: {field_name}")


_ALLOWED_FORMATS: Final[tuple[tuple[re.Pattern[str], str], ...]] = (
    (re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$"), "%Y-%m-%dT%H:%M:%S"),
    (re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$"), "%Y-%m-%d %H:%M:%S"),
    (re.compile(r"^\d{4}\.\d{2}\.\d{2}T\d{2}:\d{2}:\d{2}$"), "%Y.%m.%dT%H:%M:%S"),
    (re.compile(r"^\d{4}\.\d{2}\.\d{2} \d{2}:\d{2}:\d{2}$"), "%Y.%m.%d %H:%M:%S"),
)
_TIMEZONE_SUFFIX = re.compile(r"(?:Z|[+-]\d{2}:?\d{2})$", re.IGNORECASE)
_TIMEZONE_NAME = re.compile(r"(?:\s|T)(?:UTC|GMT)$", re.IGNORECASE)
_FRACTION_SUFFIX = re.compile(r"[.,]\d+(?:(?:Z|[+-]\d{2}:?\d{2}))?$", re.IGNORECASE)


def _fail(validation_code: str, field_name: str) -> None:
    raise FjMetadataTimestampValidationError(validation_code, field_name)


def canonicalize_fj_metadata_timestamp(value: object, field_name: str) -> str:
    """Return the canonical naive timestamp or raise a stable validation error."""

    if not isinstance(value, str):
        _fail("TIMESTAMP_VALUE_NOT_STRING", field_name)
    if value == "":
        _fail("TIMESTAMP_VALUE_EMPTY", field_name)
    if value != value.strip():
        _fail("TIMESTAMP_WHITESPACE_NOT_ALLOWED", field_name)
    if _TIMEZONE_SUFFIX.search(value) or _TIMEZONE_NAME.search(value):
        _fail("TIMESTAMP_TIMEZONE_NOT_ALLOWED", field_name)
    if _FRACTION_SUFFIX.search(value):
        _fail("TIMESTAMP_FRACTION_NOT_ALLOWED", field_name)

    for pattern, datetime_format in _ALLOWED_FORMATS:
        if pattern.fullmatch(value):
            try:
                parsed = datetime.strptime(value, datetime_format)
            except ValueError:
                _fail("TIMESTAMP_CALENDAR_INVALID", field_name)
            return parsed.strftime("%Y-%m-%dT%H:%M:%S")

    _fail("TIMESTAMP_FORMAT_NOT_ALLOWLISTED", field_name)


__all__ = [
    "FjMetadataTimestampValidationError",
    "canonicalize_fj_metadata_timestamp",
]
