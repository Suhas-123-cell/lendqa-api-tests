from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from uuid import uuid4

app = FastAPI(title="LendQA Loan API", version="1.0.0")

# --- This is our fake "database" (just a dictionary in memory) ---
loans_db = {}


# --- These are the shapes of data we accept and return ---

class LoanApplication(BaseModel):
    applicant_name: str
    amount: float = Field(gt=0, description="Amount must be greater than 0")
    purpose: str
    term_months: int = Field(gt=0, le=360)


class LoanResponse(BaseModel):
    loan_id: str
    applicant_name: str
    amount: float
    purpose: str
    term_months: int
    status: str


# --- The 5 API endpoints ---

@app.post("/loans", response_model=LoanResponse, status_code=201)
def create_loan(loan: LoanApplication):
    loan_id = str(uuid4())
    new_loan = {
        "loan_id": loan_id,
        "applicant_name": loan.applicant_name,
        "amount": loan.amount,
        "purpose": loan.purpose,
        "term_months": loan.term_months,
        "status": "pending",
    }
    loans_db[loan_id] = new_loan
    return new_loan


@app.get("/loans", response_model=list[LoanResponse])
def get_all_loans():
    return list(loans_db.values())


@app.get("/loans/{loan_id}", response_model=LoanResponse)
def get_loan(loan_id: str):
    if loan_id not in loans_db:
        raise HTTPException(status_code=404, detail="Loan not found")
    return loans_db[loan_id]


@app.put("/loans/{loan_id}/status", response_model=LoanResponse)
def update_loan_status(loan_id: str, status: str):
    if loan_id not in loans_db:
        raise HTTPException(status_code=404, detail="Loan not found")
    allowed = ["pending", "approved", "rejected"]
    if status not in allowed:
        raise HTTPException(status_code=400, detail=f"Status must be one of {allowed}")
    loans_db[loan_id]["status"] = status
    return loans_db[loan_id]


@app.delete("/loans/{loan_id}", status_code=204)
def delete_loan(loan_id: str):
    if loan_id not in loans_db:
        raise HTTPException(status_code=404, detail="Loan not found")
    del loans_db[loan_id]
