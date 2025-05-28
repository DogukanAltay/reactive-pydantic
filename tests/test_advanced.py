"""Advanced feature tests for reactive Pydantic models."""

import pytest
from typing import List, Optional
import time

import reactivex as rx
from reactive_pydantic import ReactiveModel, reactive_field
from reactive_pydantic.operators import debounce_changes, buffer_changes

class Product(ReactiveModel):
    name: str = reactive_field(default="")
    price: float = reactive_field(default=0.0, debounce_ms=100)
    quantity: int = reactive_field(default=0)

class Order(ReactiveModel):
    items: List[str] = reactive_field(default_factory=list)
    total: float = reactive_field(default=0.0)
    customer_id: Optional[str] = reactive_field(default=None)

def test_debounced_field_changes():
    """Test debouncing of rapid field changes."""
    events: List = []
    
    # Subscribe with debounce
    Product.observe_field("price").pipe(
        debounce_changes(0.1)
    ).subscribe(events.append)
    
    product = Product(name="Widget")
    
    # Rapid price changes
    product.price = 10.0
    product.price = 15.0
    product.price = 20.0
    
    # Should only get the last value after debounce
    time.sleep(0.15)
    assert len(events) == 1
    assert events[0].new_value == 20.0

def test_complex_data_types():
    """Test reactive behavior with complex data types."""
    events: List = []
    
    Order.observe_field("items").subscribe(events.append)
    
    order = Order()
    order.items = ["item1", "item2"]
    order.items = ["item1", "item2", "item3"]
    
    assert len(events) == 2

def test_buffered_changes():
    """Test buffering multiple changes."""
    events: List = []
    
    Product.observe_field("quantity").pipe(
        buffer_changes(3)
    ).subscribe(events.append)
    
    product = Product()
    product.quantity = 1
    product.quantity = 2
    product.quantity = 3
    
    # Should have one buffer with 3 events
    assert len(events) == 1
    assert len(events[0]) == 3

def test_chained_reactions():
    """Test creating reactive chains between models."""
    price_changes: List = []
    total_changes: List = []
    
    # Create a reactive chain: product price -> order total
    def update_order_total(price_event):
        # Simulate order total calculation
        if hasattr(update_order_total, 'order'):
            update_order_total.order.total = price_event.new_value * 2
    
    Product.observe_field("price").subscribe(update_order_total)
    Order.observe_field("total").subscribe(total_changes.append)
    
    product = Product(name="Widget", price=10.0)
    order = Order()
    update_order_total.order = order
    
    # Change product price should trigger order total change
    product.price = 25.0
    
    assert len(total_changes) >= 1
    assert total_changes[-1].new_value == 50.0

def test_computed_properties():
    """Test implementing computed properties that react to changes."""
    
    class Rectangle(ReactiveModel):
        width: float = reactive_field(default=0.0)
        height: float = reactive_field(default=0.0)
        area: float = reactive_field(default=0.0)
        
        def __init__(self, **data):
            super().__init__(**data)
            self._setup_computed_area()
        
        def _setup_computed_area(self):
            """Set up reactive area calculation."""
            def update_area(event):
                self.area = self.width * self.height
            
            self.observe_instance_field("width").subscribe(update_area)
            self.observe_instance_field("height").subscribe(update_area)
    
    area_changes: List = []
    
    rect = Rectangle(width=5.0, height=3.0)
    rect.observe_instance_field("area").subscribe(area_changes.append)
    
    # Changing width should update area
    rect.width = 10.0
    
    assert len(area_changes) >= 1
    assert rect.area == 30.0

def test_model_validation_events():
    """Test validation event emission."""
    
    class ValidatedProduct(ReactiveModel):
        name: str = reactive_field(min_length=3)
        price: float = reactive_field(gt=0)
    
    # This would require extending the validation system
    # For now, test basic validation still works
    
    with pytest.raises(ValueError):
        ValidatedProduct(name="AB", price="-5")
    
    # Valid model should work
    product = ValidatedProduct(name="Valid Product", price=10.0)
    assert product.name == "Valid Product"
    assert product.price == 10.0