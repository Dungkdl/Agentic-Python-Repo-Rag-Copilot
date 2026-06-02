"""API layer for supplier operations."""

from app.services.supplier_service import SupplierService


def register_supplier(supplier_id: str, name: str, priority: int = 1) -> dict:
    """Register a supplier through the service layer."""
    service = SupplierService()
    return service.register_supplier(
        supplier_id=supplier_id,
        name=name,
        priority=priority,
    )


def get_supplier(supplier_id: str) -> dict:
    """Return supplier details."""
    service = SupplierService()
    return service.get_supplier(supplier_id=supplier_id)
