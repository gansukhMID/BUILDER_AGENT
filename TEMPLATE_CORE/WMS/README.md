# WMS Core Template

Reusable SQLAlchemy 2.x base models for Warehouse Management Systems, inspired by Odoo's `stock` module. Intended as a foundational library for AI agents generating custom WMS applications.

## Model Analogues

| Template Model | Odoo Analogue | Purpose |
|---|---|---|
| `Warehouse` | `stock.warehouse` | Top-level facility |
| `Location` | `stock.location` | Hierarchical storage location |
| `Product` | `product.product` | Storable item |
| `Lot` | `stock.lot` | Lot / serial number |
| `Quant` | `stock.quant` | Materialized on-hand inventory |
| `PickingType` | `stock.picking.type` | Operation type (receive/deliver/internal) |
| `Picking` | `stock.picking` | Transfer operation header |
| `Move` | `stock.move` | Product movement between locations |
| `StockRule` | `stock.rule` | Procurement / replenishment rule |
| `Package` | `stock.quant.package` | Packaging unit (stub) |

## Quick Start

```python
from wms_core.db import Base, engine_from_url, session_factory
from wms_core.models import Warehouse, Location, Product, Quant

engine = engine_from_url("postgresql+psycopg2://user:pass@localhost/mydb")
Base.metadata.create_all(engine)
Session = session_factory(engine)
```

## Extension Pattern

Subclass any model to add client-specific fields without modifying template files:

```python
from wms_core.models.product import Product as _Product
from sqlalchemy.orm import Mapped, mapped_column

class Product(_Product):
    __tablename__ = "product"          # reuse same table
    __table_args__ = {"extend_existing": True}

    barcode: Mapped[str | None] = mapped_column(nullable=True)
    weight_kg: Mapped[float | None] = mapped_column(nullable=True)
```

## Alembic

Copy `alembic.ini.template` to `alembic.ini`, set `DATABASE_URL`, then:

```bash
alembic upgrade head
```

## Dependencies

- `sqlalchemy>=2.0`
- `alembic>=1.13`
- `python-dotenv>=1.0`

## Running Tests

```bash
pip install -e ".[dev]"
pytest tests/ -v --cov=wms_core
```
