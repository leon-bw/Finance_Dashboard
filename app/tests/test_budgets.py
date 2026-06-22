from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
from fastapi import status

from app.models import Budget, Category


@pytest.fixture
def auth_headers(client, test_user):
    """
    Get authentication headers for the test user
    """
    response = client.post(
        "/auth/login", data={"username": "testuser", "password": "test1234"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def test_category(test_db):
    """
    A default category budgets can reference
    """
    category = Category(
        name="Groceries",
        type="expense",
        description="Grocery and household shopping",
        icon="🛒",
        colour="#D4C6E0",
        is_default=True,
    )
    test_db.add(category)
    test_db.commit()
    test_db.refresh(category)
    return category


@pytest.fixture
def budget_payload(test_category):
    """
    A valid budget creation payload
    """
    start = datetime.now(timezone.utc)
    end = start + timedelta(days=30)
    return {
        "amount": 500.0,
        "period": "monthly",
        "category_id": str(test_category.id),
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        "alert_threshold": 0.8,
    }


@pytest.fixture
def test_budget(test_db, test_user, test_category):
    """
    An existing budget owned by the test user
    """
    start = datetime.now(timezone.utc)
    budget = Budget(
        user_id=test_user.id,
        category_id=test_category.id,
        amount=300.0,
        period="monthly",
        start_date=start,
        end_date=start + timedelta(days=30),
        alert_threshold=0.8,
    )
    test_db.add(budget)
    test_db.commit()
    test_db.refresh(budget)
    return budget


class TestCreateBudget:
    def test_requires_auth(self, client, budget_payload):
        response = client.post("/budgets/", json=budget_payload)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_budget(self, client, auth_headers, budget_payload):
        response = client.post(
            "/budgets/", json=budget_payload, headers=auth_headers
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["amount"] == 500.0
        assert data["period"] == "monthly"
        assert data["is_active"] is True
        assert "id" in data

    def test_create_with_unknown_category(self, client, auth_headers, budget_payload):
        budget_payload["category_id"] = str(uuid4())
        response = client.post(
            "/budgets/", json=budget_payload, headers=auth_headers
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_create_with_end_before_start_is_rejected(
        self, client, auth_headers, budget_payload
    ):
        start = datetime.now(timezone.utc)
        budget_payload["start_date"] = start.isoformat()
        budget_payload["end_date"] = (start - timedelta(days=1)).isoformat()
        response = client.post(
            "/budgets/", json=budget_payload, headers=auth_headers
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestGetBudgets:
    def test_list_budgets(self, client, auth_headers, test_budget):
        response = client.get("/budgets/", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == str(test_budget.id)

    def test_filter_by_active(self, client, auth_headers, test_budget):
        response = client.get("/budgets/?is_active=false", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    def test_get_single_budget(self, client, auth_headers, test_budget):
        response = client.get(f"/budgets/{test_budget.id}", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["id"] == str(test_budget.id)

    def test_get_missing_budget(self, client, auth_headers):
        response = client.get(f"/budgets/{uuid4()}", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestUpdateBudget:
    def test_update_budget(self, client, auth_headers, test_budget):
        response = client.put(
            f"/budgets/{test_budget.id}",
            json={"amount": 750.0, "is_active": False},
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["amount"] == 750.0
        assert data["is_active"] is False

    def test_update_missing_budget(self, client, auth_headers):
        response = client.put(
            f"/budgets/{uuid4()}", json={"amount": 100.0}, headers=auth_headers
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_end_before_start_is_rejected(
        self, client, auth_headers, test_budget
    ):
        new_end = (test_budget.start_date - timedelta(days=1)).isoformat()
        response = client.put(
            f"/budgets/{test_budget.id}",
            json={"end_date": new_end},
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestDeleteBudget:
    def test_delete_budget(self, client, auth_headers, test_budget):
        response = client.delete(
            f"/budgets/{test_budget.id}", headers=auth_headers
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT

        follow_up = client.get(f"/budgets/{test_budget.id}", headers=auth_headers)
        assert follow_up.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_missing_budget(self, client, auth_headers):
        response = client.delete(f"/budgets/{uuid4()}", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND
