import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app, loans_db


# This fixture runs before every test and gives it a fresh client to talk to our API.
# "yield" means: set up → run the test → tear down after.
@pytest.fixture
async def client():
    loans_db.clear()  # Start every test with an empty database
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


# A ready-made loan payload so we don't repeat it in every test
@pytest.fixture
def loan_payload():
    return {
        "applicant_name": "Suhas Choudary",
        "amount": 50000,
        "purpose": "Home renovation",
        "term_months": 24,
    }
