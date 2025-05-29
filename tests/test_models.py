"""Basic functionality tests for reactive Pydantic models."""

import time
from datetime import datetime
from typing import List

import pytest
import reactivex as rx

from reactive_pydantic import FieldChangeEvent, ReactiveModel, reactive_field
from reactive_pydantic.operators import map_to_value, where_field


class User(ReactiveModel):
    name: str = reactive_field(default="")
    age: int = reactive_field(default=0)
    email: str = reactive_field(default="")
    non_reactive_field: str = "static"


def test_field_change_emission():
    """Test that field changes emit events."""
    events: List[FieldChangeEvent] = []

    # Subscribe to name changes
    User.observe_field("name").subscribe(events.append)

    # Create and modify user
    user = User(name="John", age=30)
    user.name = "Jane"

    # Should have one change event (creation doesn't count as change)
    assert len(events) == 1
    assert events[0].field_name == "name"
    assert events[0].old_value == "John"
    assert events[0].new_value == "Jane"


def test_instance_specific_observation():
    """Test observing changes on a specific instance."""
    events: List[FieldChangeEvent] = []

    user1 = User(name="User1")
    user2 = User(name="User2")

    # Subscribe to changes on user1 only
    user1.observe_instance_field("name").subscribe(events.append)

    # Modify both users
    user1.name = "Modified1"
    user2.name = "Modified2"

    # Should only see user1 changes
    assert len(events) == 1
    assert events[0].new_value == "Modified1"


def test_multiple_field_observation():
    """Test observing multiple fields."""
    name_events: List[FieldChangeEvent] = []
    age_events: List[FieldChangeEvent] = []

    User.observe_field("name").subscribe(name_events.append)
    User.observe_field("age").subscribe(age_events.append)

    user = User(name="John", age=30)
    user.name = "Jane"
    user.age = 31

    assert len(name_events) == 1
    assert len(age_events) == 1
    assert name_events[0].new_value == "Jane"
    assert age_events[0].new_value == 31


def test_reactive_operators():
    """Test reactive operators work correctly."""
    values: List[str] = []

    # Use operators to filter and transform
    User.observe_model().pipe(where_field("name"), map_to_value()).subscribe(
        values.append
    )

    user = User(name="Initial")
    user.name = "Changed"
    user.age = 25  # This should not appear in values

    assert values == ["Changed"]


def test_model_lifecycle_events():
    """Test model creation events."""
    events: List = []

    User.observe_model().subscribe(events.append)

    User(name="Test")

    # Should have model creation event
    creation_events = [e for e in events if e.event_type.value == "model_created"]
    assert len(creation_events) == 1


def test_non_reactive_fields():
    """Test that non-reactive fields don't emit events."""
    events: List = []

    User.observe_model().subscribe(events.append)

    user = User()
    initial_event_count = len(events)

    # Modify non-reactive field
    user.non_reactive_field = "changed"

    # Should not have additional events
    assert len(events) == initial_event_count


@pytest.mark.asyncio
async def test_async_observation():
    """Test async observation patterns."""
    import asyncio

    events: List[FieldChangeEvent] = []

    def on_next(event):
        events.append(event)

    User.observe_field("name").subscribe(on_next)

    user = User(name="Test")
    user.name = "Changed"

    # Allow time for async processing
    await asyncio.sleep(0.1)

    assert len(events) == 1


def test_model_dump_reactive():
    """Test reactive model dump includes metadata."""
    user = User(name="John", age=30)
    data = user.model_dump_reactive()

    assert "_reactive_meta" in data
    assert "model_id" in data["_reactive_meta"]
    assert "reactive_fields" in data["_reactive_meta"]
    assert set(data["_reactive_meta"]["reactive_fields"]) == {"name", "age", "email"}
