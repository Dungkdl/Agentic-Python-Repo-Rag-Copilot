"""Reporting helpers for Inventory API."""


class InventoryReportService:
    """Build inventory report summaries."""

    def build_low_stock_report(self, items: list[dict]) -> dict:
        """Return items that need restock."""
        low_stock_items = [
            item
            for item in items
            if item.get("needs_restock") is True
        ]

        return {
            "low_stock_count": len(low_stock_items),
            "items": low_stock_items,
        }

    def build_supplier_report(self, suppliers: list[dict]) -> dict:
        """Return a report with priority supplier counts."""
        priority_count = sum(
            1
            for supplier in suppliers
            if supplier.get("priority_supplier") is True
        )

        return {
            "supplier_count": len(suppliers),
            "priority_supplier_count": priority_count,
        }
