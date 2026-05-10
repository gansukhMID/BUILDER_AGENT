---
issue: 24
stream: Core Package
started: 2026-05-10T13:24:24Z
status: completed
---
## Scope
db.py, mixins.py, ecommerce_core/__init__.py, models/__init__.py

## Files Created
- `TEMPLATE_CORE/ECOMMERCE/ecommerce_core/__init__.py` — package marker (`# ecommerce_core`)
- `TEMPLATE_CORE/ECOMMERCE/ecommerce_core/db.py` — Base, engine_factory, SessionFactory, get_session, engine_from_url, session_factory
- `TEMPLATE_CORE/ECOMMERCE/ecommerce_core/mixins.py` — TimestampMixin, ActiveMixin, NameMixin, CurrencyMixin
- `TEMPLATE_CORE/ECOMMERCE/ecommerce_core/models/__init__.py` — empty stub (`# populated in task #30`)

## Verification
Import check passed:
```
from TEMPLATE_CORE.ECOMMERCE.ecommerce_core.db import Base, engine_factory, session_factory, get_session, engine_from_url
from TEMPLATE_CORE.ECOMMERCE.ecommerce_core.mixins import TimestampMixin, ActiveMixin, NameMixin, CurrencyMixin
# All imports OK
```

## Commit
`e012d44` — Issue #24: Stream A — core package (db.py, mixins.py, CurrencyMixin)
