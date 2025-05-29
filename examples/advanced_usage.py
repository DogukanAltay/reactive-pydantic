"""Advanced example demonstrating all reactive Pydantic features."""

import asyncio
import time
from typing import List

import reactivex as rx
import reactivex.operators as ops
from reactive_pydantic import ReactiveModel, reactive_field
from reactive_pydantic.operators import (
    where_field,
    map_to_value,
    debounce_changes,
    buffer_changes,
    where_event_type,
)
from reactive_pydantic.events import EventType


class User(ReactiveModel):
    """A reactive user model with various field types."""

    name: str = reactive_field(default="")
    age: int = reactive_field(default=0)
    email: str = reactive_field(default="")
    tags: List[str] = reactive_field(default_factory=list)


class Product(ReactiveModel):
    """A reactive product model."""

    name: str = reactive_field(default="")
    price: float = reactive_field(default=0.0)
    in_stock: bool = reactive_field(default=True)


def demonstrate_basic_observation():
    """Demonstrate basic field observation."""
    print("=== Basic Field Observation ===")

    changes = []

    # Subscribe to all name changes across all User instances
    User.observe_field("name").pipe(
        ops.distinct_until_changed(),  # Only emit when value actually changes
        map_to_value(),  # Extract just the new value
    ).subscribe(lambda value: changes.append(f"Name changed to: {value}"))

    # Create and modify users
    user1 = User(name="Alice", age=25)
    user1.name = "Alice Smith"
    user1.name = "Alice Smith"  # This won't emit due to distinct_until_changed
    user1.name = "Dr. Alice Smith"

    user2 = User(name="Bob")
    user2.name = "Robert"

    print(f"Observed changes: {changes}")
    print()


def demonstrate_debounced_observation():
    """Demonstrate debounced field observation."""
    print("=== Debounced Observation ===")

    changes = []

    # Subscribe to age changes with debouncing
    User.observe_field("age").pipe(
        debounce_changes(0.1),  # Wait 100ms before emitting
        map_to_value(),
    ).subscribe(lambda value: changes.append(f"Debounced age: {value}"))

    user = User(name="Test User", age=20)

    # Rapid changes - only the last one should be emitted after debounce
    user.age = 21
    user.age = 22
    user.age = 23
    user.age = 24

    # Wait for debounce to complete
    time.sleep(0.2)

    print(f"Debounced changes: {changes}")
    print()


def demonstrate_buffered_observation():
    """Demonstrate buffered field observation."""
    print("=== Buffered Observation ===")

    buffers = []

    # Buffer every 3 changes
    User.observe_field("email").pipe(
        buffer_changes(3), ops.map(lambda buffer: [event.new_value for event in buffer])
    ).subscribe(lambda values: buffers.append(values))

    user = User(name="Buffer Test")

    # Make several changes
    user.email = "test1@example.com"
    user.email = "test2@example.com"
    user.email = "test3@example.com"  # This should trigger the buffer
    user.email = "test4@example.com"
    user.email = "test5@example.com"
    user.email = "test6@example.com"  # This should trigger another buffer

    print(f"Buffered changes: {buffers}")
    print()


def demonstrate_instance_observation():
    """Demonstrate instance-specific observation."""
    print("=== Instance-Specific Observation ===")

    user1_events = []
    user2_events = []

    user1 = User(name="User1")
    user2 = User(name="User2")

    # Subscribe to events from specific instances
    user1.observe_instance().subscribe(
        lambda event: user1_events.append(f"User1: {event.event_type.value}")
    )

    user2.observe_instance().subscribe(
        lambda event: user2_events.append(f"User2: {event.event_type.value}")
    )

    # Make changes to both users
    user1.name = "Updated User1"
    user1.age = 30

    user2.name = "Updated User2"
    user2.email = "user2@example.com"

    print(f"User1 events: {user1_events}")
    print(f"User2 events: {user2_events}")
    print()


def demonstrate_multiple_models():
    """Demonstrate observation across different model types."""
    print("=== Multiple Model Types ===")

    all_changes = []

    # Create a combined observable for all field changes
    user_changes = User.observe_field("name").pipe(
        ops.map(lambda event: f"User name: {event.new_value}")
    )

    product_changes = Product.observe_field("price").pipe(
        ops.map(lambda event: f"Product price: {event.new_value}")
    )

    # Merge streams from different models
    rx.merge(user_changes, product_changes).subscribe(
        lambda change: all_changes.append(change)
    )

    # Create instances and make changes
    user = User(name="Customer")
    product = Product(name="Widget", price=10.0)

    user.name = "John Doe"
    product.price = 15.0
    user.name = "Jane Doe"
    product.price = 20.0

    print(f"All changes: {all_changes}")
    print()


def demonstrate_filtering():
    """Demonstrate event filtering by type."""
    print("=== Event Type Filtering ===")

    field_changes = []
    validation_events = []

    # Filter by event type
    User.observe_model().pipe(where_event_type(EventType.FIELD_CHANGED)).subscribe(
        lambda event: field_changes.append(f"Field changed: {event.field_name}")
    )

    User.observe_model().pipe(where_event_type(EventType.VALIDATION_SUCCESS)).subscribe(
        lambda event: validation_events.append("Validation success")
    )

    # Create and modify user
    user = User(name="Filter Test", age=25)
    user.name = "Updated Name"
    user.age = 30
    user.email = "test@example.com"

    print(f"Field changes: {field_changes}")
    print(f"Validation events: {validation_events}")
    print()


async def demonstrate_async_observation():
    """Demonstrate async observation patterns."""
    print("=== Async Observation ===")

    changes = []

    def async_handler(event):
        """Async event handler."""
        changes.append(f"Async: {event.field_name} = {event.new_value}")

    # Subscribe to async observations
    User.observe_field("tags").subscribe(async_handler)

    user = User(name="Async Test")

    # Make changes
    user.tags = ["tag1"]
    user.tags = ["tag1", "tag2"]
    user.tags = ["tag1", "tag2", "tag3"]

    # Give async operations time to complete
    await asyncio.sleep(0.1)

    print(f"Async changes: {changes}")
    print()


def main():
    """Run all demonstrations."""
    print("Reactive Pydantic Advanced Examples")
    print("=" * 40)
    print()

    demonstrate_basic_observation()
    demonstrate_debounced_observation()
    demonstrate_buffered_observation()
    demonstrate_instance_observation()
    demonstrate_multiple_models()
    demonstrate_filtering()

    # Run async demonstration
    asyncio.run(demonstrate_async_observation())

    print("All demonstrations completed!")


if __name__ == "__main__":
    main()
