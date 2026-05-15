# LendQA — API Test Suite

Automated API test suite for a Loan Management REST API built with FastAPI.
Covers status codes, schema validation, data integrity, and error handling across all endpoints.

## Tech Stack
- **API:** Python, FastAPI, Pydantic
- **Testing:** pytest, pytest-asyncio, httpx

## What's Tested (19 test cases)

| Area | Scenarios |
|---|---|
| Create Loan | 201 response, correct schema, types, default status, rejects negative/zero amount |
| Get All Loans | 200 response, returns list, reflects created records |
| Get One Loan | Correct data returned, 404 for missing loan |
| Update Status | approved/rejected updates work, invalid status → 400, missing loan → 404 |
| Delete Loan | 204 on success, 404 after deletion, 404 for missing loan |

## Run Locally

```bash
# Activate your virtual environment first, then:
pip install -r requirements.txt
pytest -v
```

## CI
Tests run automatically on every push via GitHub Actions.
