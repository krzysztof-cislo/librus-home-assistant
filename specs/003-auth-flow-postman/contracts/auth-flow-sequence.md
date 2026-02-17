# Contract: Librus Auth Flow Sequence

**Reference**: `docs/postman/librus_api.json` → Auth folder  
**Feature**: 003-auth-flow-postman

## Overview

Credential validation MUST execute the following five steps in order. Success requires all steps to return acceptable responses. Failure at any step MUST abort the flow, discard session state, and return an error key.

## Steps

### Step 1: OAuth Init

| Property | Value |
|----------|-------|
| Method | GET |
| URL | `https://api.librus.pl/OAuth/Authorization` |
| Query params | `client_id=46`, `response_type=code`, `scope=mydata` |
| Headers | `User-Agent`: Mozilla/5.0 (…Chrome/131…) |
| Success | HTTP 200 or 302 |
| Follow redirects | Yes |

---

### Step 2: OAuth Login

| Property | Value |
|----------|-------|
| Method | POST |
| URL | `https://api.librus.pl/OAuth/Authorization?client_id=46` |
| Body | `application/x-www-form-urlencoded`: `action=login`, `login={username}`, `pass={password}` |
| Headers | `User-Agent`, `Content-Type: application/x-www-form-urlencoded` |
| Success | HTTP 200 or 302; body must NOT contain "error" or "Nieprawidłowy" |
| Follow redirects | Yes |
| Failure semantics | Body contains error → `invalid_auth` |

---

### Step 3: OAuth Grant

| Property | Value |
|----------|-------|
| Method | GET |
| URL | `https://api.librus.pl/OAuth/Authorization/Grant` |
| Query params | `client_id=46` |
| Headers | `User-Agent` |
| Success | HTTP 200 or 302 (sets session cookies on synergia.librus.pl via redirects) |
| Follow redirects | Yes |

---

### Step 4: Get Token Info

| Property | Value |
|----------|-------|
| Method | GET |
| URL | `https://synergia.librus.pl/gateway/api/2.0/Auth/TokenInfo` |
| Headers | `User-Agent` |
| Success | HTTP 200; JSON body contains `UserIdentifier` (string) |
| Output | `user_identifier` for Step 5 |
| Failure | Non-200 or missing UserIdentifier → fail validation |

---

### Step 5: Activate API Access

| Property | Value |
|----------|-------|
| Method | GET |
| URL | `https://synergia.librus.pl/gateway/api/2.0/Auth/UserInfo/{user_identifier}` |
| Path param | `user_identifier` from Step 4 |
| Headers | `User-Agent` |
| Success | HTTP 200 |
| Failure | Non-200 → fail validation |

---

## Error Key Mapping

| Condition | Error key |
|-----------|-----------|
| Step 2 body contains "error" or "Nieprawidłowy" | `invalid_auth` |
| `requests.exceptions.Timeout` | `timeout` |
| `requests.exceptions.ConnectionError` | `cannot_connect` |
| Other `requests.exceptions.RequestException` | `cannot_connect` |
| Step 3, 4, 5 non-success HTTP | Map by response (auth redirect → `invalid_auth`; 5xx/network → `cannot_connect`) |
| Unexpected exception | `unknown` |

---

## Session Contract

- One `requests.Session` per validation attempt
- Session must NOT be reused across attempts
- On any step failure: discard session (let go out of scope or call `close()`)
- Cookies from Steps 1–3 must be sent to Steps 4–5 (same session)
