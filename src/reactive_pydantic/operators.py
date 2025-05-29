"""RxPY operators for reactive Pydantic models."""

from typing import Any, Callable

import reactivex.operators as ops
from reactivex import Observable

from .events import EventType, FieldChangeEvent


def where_field(
    field_name: str,
) -> Callable[[Observable], Observable[FieldChangeEvent]]:
    """Filter events to only field changes for a specific field."""

    def _where_field(source: Observable) -> Observable[FieldChangeEvent]:
        return source.pipe(
            ops.filter(
                lambda event: isinstance(event, FieldChangeEvent)
                and event.field_name == field_name
            )
        )

    return _where_field


def where_model(model_id: str) -> Callable[[Observable], Observable]:
    """Filter events to only those from a specific model instance."""

    def _where_model(source: Observable) -> Observable:
        return source.pipe(
            ops.filter(
                lambda event: hasattr(event, "model_id") and event.model_id == model_id
            )
        )

    return _where_model


def where_event_type(event_type: EventType) -> Callable[[Observable], Observable]:
    """Filter events by event type."""

    def _where_event_type(source: Observable) -> Observable:
        return source.pipe(ops.filter(lambda event: event.event_type == event_type))

    return _where_event_type


def debounce_changes(duration: float) -> Callable[[Observable], Observable]:
    """Debounce field change events."""

    def _debounce_changes(source: Observable) -> Observable:
        return source.pipe(ops.debounce(duration))

    return _debounce_changes


def map_to_value() -> Callable[[Observable[FieldChangeEvent]], Observable[Any]]:
    """Extract just the new value from field change events."""

    def _map_to_value(source: Observable[FieldChangeEvent]) -> Observable[Any]:
        return source.pipe(ops.map(lambda event: event.new_value))

    return _map_to_value


def buffer_changes(count: int) -> Callable[[Observable], Observable]:
    """Buffer field changes into groups."""

    def _buffer_changes(source: Observable) -> Observable:
        return source.pipe(ops.buffer_with_count(count))

    return _buffer_changes
