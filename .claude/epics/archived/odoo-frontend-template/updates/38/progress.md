# Issue #38 Progress: Auth API (register, login, JWT)

## Status: COMPLETE

## What was done

### Files created/updated
- `auth_utils.py` — JWT helpers (`hash_password`, `verify_password`, `create_access_token`, `get_current_user`) using python-jose + passlib[bcrypt]
- `schemas/auth.py` — Pydantic schemas: `RegisterRequest`, `LoginRequest`, `TokenResponse`, `MeResponse`
- `routers/auth.py` — Full implementation replacing stub: `POST /auth/register`, `POST /auth/login`, `GET /auth/me`
- `tests/test_auth.py` — 6 tests covering register, duplicate email, login success, wrong password, /me with token, /me without token
- `pyproject.toml` — Added `bcrypt>=3.2,<4.1` pin and `pydantic[email]` for EmailStr support

### Fix applied
- bcrypt 5.x is incompatible with passlib; pinned to `bcrypt<4.1` to ensure `passlib` works correctly

## Test results
All 6 tests passed:
- test_register — PASSED
- test_register_duplicate — PASSED
- test_login_success — PASSED
- test_login_wrong_password — PASSED
- test_me — PASSED
- test_me_no_token — PASSED

Coverage: auth_utils.py 89%, routers/auth.py 94%, schemas/auth.py 100%
