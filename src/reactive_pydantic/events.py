"""Event types for reactive Pydantic models."""

from typing import Any, Generic, TypeVar, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

T = TypeVar('T')

class EventType(Enum):
    """Types of events that can be emitted."""
    FIELD_CHANGED = "field_changed"
    MODEL_CREATED = "model_created"
    MODEL_UPDATED = "model_updated"
    MODEL_DELETED = "model_deleted"
    VALIDATION_ERROR = "validation_error"
    VALIDATION_SUCCESS = "validation_success"

@dataclass(frozen=True)
class BaseEvent:
    """Base class for all reactive events."""
    timestamp: datetime
    model_id: str
    event_type: EventType

@dataclass(frozen=True)
class FieldChangeEvent(BaseEvent, Generic[T]):
    """Event emitted when a field value changes."""
    field_name: str
    old_value: Optional[T]
    new_value: T
    
    def __post_init__(self):
        object.__setattr__(self, 'event_type', EventType.FIELD_CHANGED)

@dataclass(frozen=True)
class ModelEvent(BaseEvent):
    """Event emitted for model lifecycle events."""
    model_data: dict[str, Any]

@dataclass(frozen=True) 
class ValidationEvent(BaseEvent):
    """Event emitted during validation."""
    field_name: Optional[str]
    error_message: Optional[str]
    is_valid: bool