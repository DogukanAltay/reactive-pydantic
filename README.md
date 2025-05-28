# Reactive Pydantic

A Python library that combines the power of [Pydantic](https://pydantic-docs.helpmanual.io/) models with [ReactiveX (RxPY)](https://github.com/ReactiveX/RxPY) to create reactive, observable data models.

## Features

- 🔄 **Reactive Models**: Pydantic models that emit events when fields change
- 📡 **Observable Fields**: Subscribe to changes on specific fields across all instances
- 🎯 **Instance-Specific Observation**: Observe changes on individual model instances
- ⚡ **Rich Operators**: Built-in RxPY operators for filtering, debouncing, and transforming events
- 🔍 **Type Safe**: Full type hints and IDE support
- 🧪 **Validation Events**: React to validation success/failure events
- 🎨 **Computed Properties**: Create reactive computed properties that update automatically

## Installation

```bash
pip install reactive-pydantic
```

## Quick Start

```python
from reactive_pydantic import ReactiveModel, ReactiveField

class User(ReactiveModel):
    name: str = ReactiveField(default="")
    age: int = ReactiveField(default=0)
    email: str = ReactiveField(default="")

# Subscribe to name changes across all User instances
User.observe_field("name").subscribe(
    lambda event: print(f"Name changed from {event.old_value} to {event.new_value}")
)

# Create and modify a user
user = User(name="Alice", age=25)
user.name = "Alice Smith"  # Triggers the subscription above
```

## Advanced Usage

### Instance-Specific Observation

```python
user = User(name="Bob")

# Observe changes only on this specific instance
user.observe_instance_field("age").subscribe(
    lambda event: print(f"Bob's age changed to {event.new_value}")
)

user.age = 30  # Only triggers for this user instance
```

### Reactive Operators

```python
from reactive_pydantic.operators import where_field, map_to_value, debounce_changes

# Chain operators for advanced event processing
User.observe_model().pipe(
    where_field("email"),
    map_to_value(),
    debounce_changes(0.5)  # Debounce rapid changes
).subscribe(lambda email: print(f"Email settled on: {email}"))
```

### Computed Properties

```python
class Rectangle(ReactiveModel):
    width: float = reactive_field(default=0.0)
    height: float = reactive_field(default=0.0)
    area: float = reactive_field(default=0.0)
    
    def __init__(self, **data):
        super().__init__(**data)
        
        # Set up reactive area calculation
        def update_area(_):
            self.area = self.width * self.height
            
        self.observe_instance_field("width").subscribe(update_area)
        self.observe_instance_field("height").subscribe(update_area)

rect = Rectangle(width=5, height=3)
rect.width = 10  # Automatically updates area to 30
```

## API Reference

### ReactiveModel

Base class for all reactive models. Extends Pydantic's `BaseModel`.

#### Class Methods

- `observe_field(field_name: str) -> Observable[FieldChangeEvent]`: Observe changes to a specific field across all instances
- `observe_model() -> Observable[BaseEvent]`: Observe all events for this model type

#### Instance Methods

- `observe_instance() -> Observable[BaseEvent]`: Observe all events for this instance
- `observe_instance_field(field_name: str) -> Observable[FieldChangeEvent]`: Observe changes to a specific field on this instance
- `model_dump_reactive() -> Dict[str, Any]`: Dump model data including reactive metadata

### reactive_field()

Enhanced field definition with reactive capabilities.

```python
reactive_field(
    default=None,
    reactive=True,  # Enable/disable reactive behavior
    debounce_ms=None,  # Debounce time in milliseconds
    **kwargs  # Standard Pydantic field arguments
)
```

### Events

- `FieldChangeEvent`: Emitted when a reactive field changes
- `ModelEvent`: Emitted for model lifecycle events (create, update, delete)
- `ValidationEvent`: Emitted during validation (success/failure)

### Operators

- `where_field(field_name)`: Filter events to specific field changes
- `where_model(model_id)`: Filter events to specific model instance
- `debounce_changes(duration)`: Debounce rapid changes
- `map_to_value()`: Extract just the new value from field change events

## License

MIT License. See [LICENSE](LICENSE) for details.