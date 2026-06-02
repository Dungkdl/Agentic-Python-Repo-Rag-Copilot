"""Business logic for inventory suppliers."""

from app.models.supplier import Supplier


class SupplierService:
    """Manage supplier records."""

    def __init__(self) -> None:
        """Initialize the supplier store."""
        self.suppliers: dict[str, Supplier] = {}

    def register_supplier(self, supplier_id: str, name: str, priority: int = 1) -> dict:
        """Register a supplier and store it by identifier."""
        supplier = Supplier(
            supplier_id=supplier_id,
            name=name,
            priority=priority,
        )
        self.suppliers[supplier_id] = supplier
        return supplier.to_dict()

    def get_supplier(self, supplier_id: str) -> dict:
        """Return a supplier by identifier."""
        supplier = self.suppliers.get(supplier_id)

        if supplier is None:
            raise ValueError(f"Unknown supplier: {supplier_id}")

        return supplier.to_dict()
