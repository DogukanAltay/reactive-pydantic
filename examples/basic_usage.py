"""Basic example of reactive Pydantic models."""

import time

import reactivex.operators as ops
from reactive_pydantic import ReactiveModel, reactive_field
from reactive_pydantic.operators import where_field, map_to_value

class User(ReactiveModel):
    """A reactive user model."""
    name: str = reactive_field(default="")
    age: int = reactive_field(default=0)
    email: str = reactive_field(default="")

def main():
    """Demonstrate basic reactive functionality."""
    
    # Create a list to collect events
    name_changes = []
    age_changes = []
    
    # Subscribe to field changes
    User.observe_field("name").pipe(
        ops.distinct_until_changed(),
        map_to_value()
    ).subscribe(lambda value: name_changes.append(value))
    
    User.observe_field("age").subscribe(
        lambda event: age_changes.append(f"Age changed from {event.old_value} to {event.new_value}")
    )
    
    # Create and modify users
    print("Creating user...")
    user1 = User(name="Alice", age=25)
    
    print("Modifying user...")
    user1.name = "Alice Smith"
    user1.name = "Alice Smith"
    user1.name = "Alices Smith"

    user1.age = 26
    
    # Create another user
    print("Creating second user...")
    user2 = User(name="Bob", age=30)
    user2.name = "Robert"
    
    # Print collected events
    print(f"\nName changes observed: {name_changes}")
    print(f"Age changes observed: {age_changes}")
    
    # Demonstrate instance-specific observation
    print("\nDemonstrating instance-specific observation...")
    user1_changes = []
    user1.observe_instance().subscribe(
        lambda event: user1_changes.append(f"User1 event: {event.event_type.value}")
    )
    
    user1.email = "alice@example.com"
    user2.email = "bob@example.com"  # This won't appear in user1_changes
    
    print(f"User1 specific changes: {user1_changes}")

if __name__ == "__main__":
    main()