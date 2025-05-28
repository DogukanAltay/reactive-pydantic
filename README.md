# Reactive Pydantic

A powerful library for creating reactive Pydantic models with observable field changes using RxPY. This library extends Pydantic models with reactive capabilities, allowing you to observe and react to field changes in real-time.

## Features

- 🔄 **Reactive Models**: Extend Pydantic models with reactive capabilities
- 📡 **Field Observation**: Observe changes to specific fields across all instances
- 🎯 **Instance-Specific Observation**: Watch changes on individual model instances  
- 🚀 **Custom Reactive Operators**: Built-in operators for filtering, debouncing, and buffering
- ⚡ **Async Support**: Full support for async observation patterns
- 🔍 **Event Filtering**: Filter events by type, field, or model instance
- 🧪 **Type Safe**: Full type annotation support with modern Pydantic v2
- 🧪 **Validation Events**: React to validation success/failure events
- 🎨 **Computed Properties**: Create reactive computed properties that update automatically

## Installation

```bash
pip install reactive-pydantic
```

Or with Poetry:

```bash
poetry add reactive-pydantic
```

## Quick Start

```python
from reactive_pydantic import ReactiveModel, reactive_field
import reactivex.operators as ops

class User(ReactiveModel):
    name: str = reactive_field(default="")
    age: int = reactive_field(default=0)
    email: str = reactive_field(default="")

# Observe field changes across all User instances
User.observe_field("name").pipe(
    ops.distinct_until_changed(),
    ops.map(lambda event: event.new_value)
).subscribe(lambda value: print(f"Name changed to: {value}"))

# Create and modify users
user = User(name="Alice", age=25)
user.name = "Alice Smith"  # Prints: Name changed to: Alice Smith
```

## Core Concepts

### Reactive Models

Reactive models are Pydantic models that emit events when their fields change:

```python
from reactive_pydantic import ReactiveModel, reactive_field

class Product(ReactiveModel):
    name: str = reactive_field(default="")
    price: float = reactive_field(default=0.0)
    in_stock: bool = reactive_field(default=True)
```

### Field Observation

Observe changes to specific fields across all instances of a model:

```python
# Observe all name changes
Product.observe_field("name").subscribe(
    lambda event: print(f"Product name changed: {event.old_value} -> {event.new_value}")
)

# Observe price changes with custom operators
from reactive_pydantic.operators import map_to_value

Product.observe_field("price").pipe(
    map_to_value()  # Extract just the new value
).subscribe(lambda price: print(f"New price: ${price}"))
```

### Instance-Specific Observation

Watch changes on individual model instances:

```python
product = Product(name="Widget")

# Observe all changes to this specific instance
product.observe_instance().subscribe(
    lambda event: print(f"Field {event.field_name} changed on this product")
)

product.name = "Super Widget"  # Triggers the observer
```

## Custom Operators

The library includes several custom operators for common reactive patterns:

### Field Filtering

```python
from reactive_pydantic.operators import where_field, map_to_value

# Only observe 'email' field changes
User.observe_model().pipe(
    where_field("email"),
    map_to_value()
).subscribe(lambda email: print(f"Email updated: {email}"))
```

### Debouncing

```python
from reactive_pydantic.operators import debounce_changes

# Debounce rapid changes (wait 500ms after last change)
User.observe_field("name").pipe(
    debounce_changes(0.5),
    map_to_value()
).subscribe(lambda name: print(f"Name settled on: {name}"))
```

### Buffering

```python
from reactive_pydantic.operators import buffer_changes

# Buffer every 3 changes
User.observe_field("age").pipe(
    buffer_changes(3)
).subscribe(lambda events: print(f"Received {len(events)} age changes"))
```

### Event Type Filtering

```python
from reactive_pydantic.operators import where_event_type
from reactive_pydantic.events import EventType

# Only observe field change events (not validation events)
User.observe_model().pipe(
    where_event_type(EventType.FIELD_CHANGED)
).subscribe(lambda event: print(f"Field changed: {event.field_name}"))
```

## Advanced Usage

### Multiple Model Types

```python
import reactivex as rx

# Combine observables from different models
user_changes = User.observe_field("name")
product_changes = Product.observe_field("price")

# Merge streams
rx.merge(user_changes, product_changes).subscribe(
    lambda event: print(f"Something changed: {event}")
)
```

### Async Observation

```python
import asyncio

async def async_handler(event):
    await asyncio.sleep(0.1)  # Simulate async work
    print(f"Processed change: {event.field_name}")

User.observe_field("email").subscribe(async_handler)
```

### Complex Filtering

```python
import reactivex.operators as ops

# Complex filtering example
User.observe_model().pipe(
    ops.filter(lambda event: event.field_name in ["name", "email"]),
    ops.filter(lambda event: len(str(event.new_value)) > 3),
    ops.map(lambda event: f"{event.field_name}: {event.new_value}")
).subscribe(print)
```

## Event Types

The library defines several event types:

- `EventType.FIELD_CHANGED`: Emitted when a field value changes
- `EventType.MODEL_CREATED`: Emitted when a model instance is created
- `EventType.VALIDATION_SUCCESS`: Emitted when validation succeeds
- `EventType.VALIDATION_ERROR`: Emitted when validation fails

## API Reference

### ReactiveModel

Base class for reactive Pydantic models.

#### Class Methods

- `observe_field(field_name: str) -> Observable[FieldChangeEvent]`: Observe changes to a specific field across all instances
- `observe_model() -> Observable[BaseEvent]`: Observe all events from all instances of this model

#### Instance Methods

- `observe_instance() -> Observable[BaseEvent]`: Observe all events from this specific instance

### reactive_field

Function to create reactive fields.

```python
def reactive_field(
    default: Any = None,
    default_factory: Callable = None,
    **kwargs
) -> Any
```

### Custom Operators

All operators return functions that can be used with RxPY's `pipe()` method:

- `where_field(field_name: str)`: Filter events by field name
- `where_event_type(event_type: EventType)`: Filter events by type
- `map_to_value()`: Extract the new value from field change events
- `debounce_changes(duration: float)`: Debounce field changes
- `buffer_changes(count: int)`: Buffer field changes

## Examples

Check out the `examples/` directory for complete working examples:

- `basic_usage.py`: Basic reactive model usage
- `advanced_usage.py`: Advanced features and patterns

## Requirements

- Python 3.8+
- Pydantic v2.0+
- RxPY (reactivex) v4.0+

## Development

To set up for development:

```bash
git clone https://github.com/yourusername/reactive-pydantic.git
cd reactive-pydantic
poetry install
```

Run tests:

```bash
poetry run pytest
```

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

MIT License. See [LICENSE](LICENSE) for details.