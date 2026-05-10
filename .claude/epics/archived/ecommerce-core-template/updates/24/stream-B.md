---
issue: 24
stream: Utils + Build Config
started: 2026-05-10T13:24:24Z
status: completed
commit: a52b4e6
---
## Scope
state_machine.py, pricing.py stub, pyproject.toml, alembic.ini.template, alembic/env.py

## Files Created
1. `TEMPLATE_CORE/ECOMMERCE/ecommerce_core/utils/__init__.py` — empty
2. `TEMPLATE_CORE/ECOMMERCE/ecommerce_core/utils/state_machine.py` — generic StateMachine + InvalidTransition (WMS mirror, no WMS-specific constants)
3. `TEMPLATE_CORE/ECOMMERCE/ecommerce_core/utils/pricing.py` — evaluate_pricelist stub (raises NotImplementedError until task #31)
4. `TEMPLATE_CORE/ECOMMERCE/pyproject.toml` — setuptools build config, ecommerce-core 0.1.0
5. `TEMPLATE_CORE/ECOMMERCE/alembic.ini.template` — alembic config template with ${DATABASE_URL} placeholder
6. `TEMPLATE_CORE/ECOMMERCE/alembic/__init__.py` — empty
7. `TEMPLATE_CORE/ECOMMERCE/alembic/env.py` — alembic env wired to ecommerce_core.db.Base
8. `TEMPLATE_CORE/ECOMMERCE/alembic/versions/.gitkeep` — empty placeholder
