"""Core reactive Pydantic model implementation."""

import uuid
from datetime import datetime
from typing import Any, Dict, Optional, Set, TypeVar

import reactivex.operators as ops
from pydantic import BaseModel, PrivateAttr
from pydantic.fields import FieldInfo
from reactivex import Observable
from reactivex.subject import Subject

from .events import EventType, FieldChangeEvent, ModelEvent

T = TypeVar("T", bound="ReactiveModel")


class ReactiveField(FieldInfo):
    """Enhanced field info that supports reactive features."""

    def __init__(
        self, *args, reactive: bool = True, debounce_ms: Optional[int] = None, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.reactive = reactive
        self.debounce_ms = debounce_ms


def reactive_field(
    *args, reactive: bool = True, debounce_ms: Optional[int] = None, **kwargs
) -> Any:
    """Create a reactive field with additional reactive options."""
    return ReactiveField(*args, reactive=reactive, debounce_ms=debounce_ms, **kwargs)


class ReactiveModelMeta(type(BaseModel)):
    """Metaclass for reactive models to handle class-level setup."""

    def __new__(cls, name, bases, namespace, **kwargs):
        # Create the class
        new_class = super().__new__(cls, name, bases, namespace, **kwargs)

        # Initialize reactive infrastructure
        new_class._reactive_fields: Set[str] = set()
        new_class._field_subjects: Dict[str, Subject] = {}
        new_class._model_subject: Subject = Subject()
        new_class._instances: Set = set()  # Use regular set instead of WeakSet

        # Identify reactive fields
        for field_name, field_info in new_class.model_fields.items():
            if isinstance(field_info, ReactiveField) and field_info.reactive:
                new_class._reactive_fields.add(field_name)
                new_class._field_subjects[field_name] = Subject()

        return new_class


class ReactiveModel(BaseModel, metaclass=ReactiveModelMeta):
    """Base class for reactive Pydantic models."""

    # Private attributes using Pydantic's PrivateAttr
    _model_id: str = PrivateAttr(default_factory=lambda: str(uuid.uuid4()))
    _is_initializing: bool = PrivateAttr(default=True)

    def __init__(self, **data):
        # Initialize the model
        super().__init__(**data)

        # Track this instance - use the model ID string
        self.__class__._instances.add(self._model_id)

        # Emit model created event
        self._is_initializing = False
        self._emit_model_event(EventType.MODEL_CREATED)

    def __setattr__(self, name: str, value: Any) -> None:
        """Override setattr to emit change events for reactive fields."""
        if not self._is_initializing:
            # Get old value if field exists
            old_value = getattr(self, name, None) if hasattr(self, name) else None

            # Set the new value
            super().__setattr__(name, value)

            # Emit change event for reactive fields
            if name in self.__class__._reactive_fields and old_value != value:
                self._emit_field_change(name, old_value, value)
        else:
            super().__setattr__(name, value)

    def _emit_field_change(
        self, field_name: str, old_value: Any, new_value: Any
    ) -> None:
        """Emit a field change event."""
        event = FieldChangeEvent(
            timestamp=datetime.now(),
            model_id=self._model_id,
            event_type=EventType.FIELD_CHANGED,
            field_name=field_name,
            old_value=old_value,
            new_value=new_value,
        )

        # Emit to field-specific subject
        if field_name in self.__class__._field_subjects:
            self.__class__._field_subjects[field_name].on_next(event)

        # Emit to model-level subject
        self.__class__._model_subject.on_next(event)

    def _emit_model_event(self, event_type: EventType) -> None:
        """Emit a model lifecycle event."""
        event = ModelEvent(
            timestamp=datetime.now(),
            model_id=self._model_id,
            event_type=event_type,
            model_data=self.model_dump(),
        )

        self.__class__._model_subject.on_next(event)

    @classmethod
    def observe_field(cls, field_name: str) -> Observable[FieldChangeEvent]:
        """Get an observable for a specific field across all instances."""
        if field_name not in cls._field_subjects:
            cls._field_subjects[field_name] = Subject()
        return cls._field_subjects[field_name]

    @classmethod
    def observe_model(cls) -> Observable:
        """Get an observable for all model events across all instances."""
        return cls._model_subject

    def observe_instance(self) -> Observable:
        """Get an observable for events on this specific instance."""
        return self.__class__.observe_model().pipe(
            ops.filter(lambda event: event.model_id == self._model_id)
        )

    def observe_instance_field(self, field_name: str) -> Observable[FieldChangeEvent]:
        """Get an observable for a specific field on this instance."""
        return self.__class__.observe_field(field_name).pipe(
            ops.filter(lambda event: event.model_id == self._model_id)
        )

    @property
    def model_id(self) -> str:
        """Get the unique model ID."""
        return self._model_id

    def model_dump_reactive(self) -> Dict[str, Any]:
        """Dump model data including reactive metadata."""
        data = self.model_dump()
        data["_reactive_meta"] = {
            "model_id": self._model_id,
            "reactive_fields": list(self.__class__._reactive_fields),
            "timestamp": datetime.now().isoformat(),
        }
        return data
