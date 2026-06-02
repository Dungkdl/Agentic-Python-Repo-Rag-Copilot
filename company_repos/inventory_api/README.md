# Inventory API

Inventory API is a small sample Python backend used to test the Agentic Python Repo RAG Copilot.

It manages products, stock levels, and restock decisions.

## Main modules

- `app/main.py` creates the application object and registers the inventory router.
- `app/api/inventory.py` exposes API-style functions for creating items and checking stock.
- `app/services/inventory_service.py` contains the business logic for item creation, stock updates, and restock checks.
- `app/models/item.py` defines the `InventoryItem` data model.
- `app/api/suppliers.py` exposes supplier operations.
- `app/services/supplier_service.py` stores supplier records by identifier.
- `app/services/report_service.py` builds low-stock and supplier reports.

## Typical flow

1. The API layer receives item data.
2. The API layer calls `InventoryService`.
3. The service validates and updates inventory records.
4. The result is returned as a dictionary.

## Reporting Rules

- Low-stock reports include only items whose `needs_restock` value is true.
- Supplier reports count suppliers and priority suppliers.
- Supplier priority must be a positive integer.
