import pytest

pytestmark = pytest.mark.asyncio


# ─── CREATE LOAN ───────────────────────────────────────────────────────────────

async def test_create_loan_returns_201(client, loan_payload):
    response = await client.post("/loans", json=loan_payload)
    assert response.status_code == 201


async def test_create_loan_returns_correct_schema(client, loan_payload):
    response = await client.post("/loans", json=loan_payload)
    body = response.json()

    # All these fields must be present
    assert "loan_id" in body
    assert "applicant_name" in body
    assert "amount" in body
    assert "status" in body

    # Types must be correct — amount should be a number, not a string
    assert isinstance(body["amount"], (int, float))
    assert isinstance(body["applicant_name"], str)


async def test_new_loan_status_is_pending(client, loan_payload):
    response = await client.post("/loans", json=loan_payload)
    assert response.json()["status"] == "pending"


async def test_create_loan_saves_correct_data(client, loan_payload):
    response = await client.post("/loans", json=loan_payload)
    body = response.json()
    assert body["applicant_name"] == "Suhas Choudary"
    assert body["amount"] == 50000
    assert body["term_months"] == 24


async def test_create_loan_rejects_negative_amount(client):
    bad_payload = {"applicant_name": "Test", "amount": -1000, "purpose": "test", "term_months": 12}
    response = await client.post("/loans", json=bad_payload)
    # 422 = Unprocessable Entity — the data shape was wrong
    assert response.status_code == 422


async def test_create_loan_rejects_zero_amount(client):
    bad_payload = {"applicant_name": "Test", "amount": 0, "purpose": "test", "term_months": 12}
    response = await client.post("/loans", json=bad_payload)
    assert response.status_code == 422


# ─── GET ALL LOANS ─────────────────────────────────────────────────────────────

async def test_get_all_loans_returns_200(client):
    response = await client.get("/loans")
    assert response.status_code == 200


async def test_get_all_loans_returns_list(client):
    response = await client.get("/loans")
    assert isinstance(response.json(), list)


async def test_get_all_loans_shows_created_loans(client, loan_payload):
    await client.post("/loans", json=loan_payload)
    await client.post("/loans", json=loan_payload)

    response = await client.get("/loans")
    assert len(response.json()) == 2


# ─── GET ONE LOAN ──────────────────────────────────────────────────────────────

async def test_get_one_loan_returns_correct_data(client, loan_payload):
    created = await client.post("/loans", json=loan_payload)
    loan_id = created.json()["loan_id"]

    response = await client.get(f"/loans/{loan_id}")
    assert response.status_code == 200
    assert response.json()["loan_id"] == loan_id


async def test_get_nonexistent_loan_returns_404(client):
    response = await client.get("/loans/fake-id-999")
    assert response.status_code == 404


# ─── UPDATE STATUS ─────────────────────────────────────────────────────────────

async def test_approve_loan_updates_status(client, loan_payload):
    created = await client.post("/loans", json=loan_payload)
    loan_id = created.json()["loan_id"]

    response = await client.put(f"/loans/{loan_id}/status", params={"status": "approved"})
    assert response.status_code == 200
    assert response.json()["status"] == "approved"


async def test_reject_loan_updates_status(client, loan_payload):
    created = await client.post("/loans", json=loan_payload)
    loan_id = created.json()["loan_id"]

    response = await client.put(f"/loans/{loan_id}/status", params={"status": "rejected"})
    assert response.json()["status"] == "rejected"


async def test_invalid_status_returns_400(client, loan_payload):
    created = await client.post("/loans", json=loan_payload)
    loan_id = created.json()["loan_id"]

    response = await client.put(f"/loans/{loan_id}/status", params={"status": "flying"})
    assert response.status_code == 400


async def test_update_status_on_missing_loan_returns_404(client):
    response = await client.put("/loans/fake-id/status", params={"status": "approved"})
    assert response.status_code == 404


async def test_status_is_always_valid_value(client, loan_payload):
    created = await client.post("/loans", json=loan_payload)
    loan_id = created.json()["loan_id"]

    await client.put(f"/loans/{loan_id}/status", params={"status": "approved"})
    response = await client.get(f"/loans/{loan_id}")

    allowed_statuses = ["pending", "approved", "rejected"]
    assert response.json()["status"] in allowed_statuses


# ─── DELETE LOAN ───────────────────────────────────────────────────────────────

async def test_delete_loan_returns_204(client, loan_payload):
    created = await client.post("/loans", json=loan_payload)
    loan_id = created.json()["loan_id"]

    response = await client.delete(f"/loans/{loan_id}")
    assert response.status_code == 204


async def test_deleted_loan_is_gone(client, loan_payload):
    created = await client.post("/loans", json=loan_payload)
    loan_id = created.json()["loan_id"]

    await client.delete(f"/loans/{loan_id}")

    # After deleting, trying to get it should return 404
    response = await client.get(f"/loans/{loan_id}")
    assert response.status_code == 404


async def test_delete_nonexistent_loan_returns_404(client):
    response = await client.delete("/loans/fake-id-000")
    assert response.status_code == 404
