"""Supplier model for Inventory API."""


class Supplier:
    """Simple supplier record."""

    def __init__(self, supplier_id: str, name: str, priority: int = 1) -> None:
        """Create a supplier record."""
        if priority < 1:
            raise ValueError("Supplier priority must be positive")

        self.supplier_id = supplier_id
        self.name = name
        self.priority = priority

    def is_priority_supplier(self) -> bool:
        """Return True for high-priority suppliers."""
        return self.priority == 1

    def to_dict(self) -> dict:
        """Serialize the supplier record."""
        return {
            "supplier_id": self.supplier_id,
            "name": self.name,
            "priority": self.priority,
            "priority_supplier": self.is_priority_supplier(),
        }
