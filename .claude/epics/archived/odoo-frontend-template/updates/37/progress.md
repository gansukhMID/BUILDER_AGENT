# Issue #37: FastAPI Foundation — Progress

## Status: COMPLETE

## Commit
`ce78894` — Issue #37: FastAPI foundation — routers wired, health endpoints, test conftest

## Files Created/Updated

### New router stubs
- `routers/auth.py` — GET /auth/health-auth
- `routers/wms.py` — GET /wms/health
- `routers/ecommerce.py` — GET /ecommerce/health
- `routers/users.py` — GET /users/health

### Updated
- `main.py` — Full FastAPI app with CORS, all 4 routers mounted, /health and /stats endpoints
- `pyproject.toml` — Fixed addopts (removed unsupported --cov-omit standalone arg)

### Test infrastructure
- `tests/conftest.py` — SQLite test engine, setup_db session fixture, client fixture with get_db override
- `tests/test_health.py` — 5 tests covering /health, /stats, /wms/health, /ecommerce/health, /users/health

## Test Results
```
5 passed in 0.39s — 94% coverage
```

## Notes
- `--cov-omit` in pyproject.toml addopts was invalid with pytest-cov 7.1.0 when used without explicit `--cov` being the first arg. Simplified addopts to `--cov=. --cov-report=term-missing`.
- App imports cleanly; no circular import issues.
