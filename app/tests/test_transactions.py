from datetime import datetime, timezone
from uuid import uuid4

import pytest
from fastapi import status

from app.models import Category, Transaction


@pytest.fixture
def auth_headers(client, test_user):
    """
    Get authentication headers for test user
    """
    response = client.post(
        "/auth/login", data={"username": "testuser", "password": "test1234"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def test_category(test_db):
    """
    Create a test category
    """
    category = Category(
        name="Self Care",
        type="expense",
        description="Hair appointment",
        icon="💈",
        colour="#D4C6E0",
        is_default=True,
    )
    test_db.add(category)
    test_db.commit()
    test_db.refresh(category)
    return category


@pytest.fixture
def test_transaction(test_db, test_user, test_category):
    """
    Create a test transaction
    """
    transaction = Transaction(
        user_id=test_user.id,
        category_id=test_category.id,
        amount=50.00,
        description="Tesco weekly shop",
        date=datetime.now(timezone.utc),
        type="expense",
        account="Main Account",
        currency="GBP",
        status="completed",
    )
    test_db.add(transaction)
    test_db.commit()
    test_db.refresh(transaction)
    return transaction


class TestCreateTransaction:
    def test_create_transaction_success(self, client, auth_headers, test_category):
        """
        Test creating a transaction successfully
        """
        response = client.post(
            "/transactions/",
            headers=auth_headers,
            json={
                "amount": 50.00,
                "description": "Tesco weekly shop",
                "category": "Groceries",
                "type": "expense",
                "account": "Main Account",
                "date": datetime.now(timezone.utc).isoformat(),
            },
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["amount"] == 50.00
        assert data["description"] == "Tesco weekly shop"
        assert data["type"] == "expense"
        assert "id" in data
        assert "created_at" in data

    def test_create_transaction_unauthorised(self, client, test_category):
        """
        Test create a transaction without auth
        """
        response = client.post(
            "/transactions/",
            json={
                "amount": 50.00,
                "description": "Tesco weekly shop",
                "category": "Groceries",
                "type": "expense",
                "account": "Main Account",
                "date": datetime.now(timezone.utc).isoformat(),
            },
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_transaction_invalid_amount(
        self, client, test_category, auth_headers
    ):
        """
        Test creating a transaction with a negative amount
        """
        response = client.post(
            "/transactions/",
            auth_headers,
            json={
                "amount": -50.00,
                "description": "Test",
                "category": "Entertainment",
                "type": "expense",
                "account": "Main Account",
                "date": datetime.now(timezone.utc).isoformat(),
            },
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


class TestGetTransactions:
    def test_get_transaction_empty(self, client, auth_headers):
        """
        Test getting transactions when none exist
        """
        response = client.get("/transactions/", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.json(), list)
        assert len(response.json()) == 0

    def test_get_transactions_with_data(self, client, auth_headers, test_transaction):
        """
        Test getting transactions when some exist
        """
        response = client.get("/transactions/", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["description"] == "Tesco weekly shop"

    def test_get_transactions_unauthorised(self, client):
        """
        Test getting a transaction without auth
        """
        response = client.get("/transactions/")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_transactions_by_type(self, client, auth_headers, test_transaction):
        """
        Test getting a transaction by type
        """
        response = client.get(
            "/transactions/", headers=auth_headers, params={"type": "expense"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) > 0
        assert all(t["type"] == "expense" for t in data)


class TestGetSingleTransaction:
    def test_get_transaction_success(self, client, auth_headers, test_transaction):
        """
        Test getting a single transaction
        """
        response = client.get(
            f"/transactions/{test_transaction.id}", headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == str(test_transaction.id)
        assert data["description"] == "Tesco weekly shop"

    def test_get_transaction_not_found(self, client, auth_headers):
        """
        Test getting a non-existent transaction
        """
        invalid_id = uuid4()
        response = client.get(f"/transactions/{invalid_id}", headers=auth_headers)

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestUpdateTransaction:
    def test_updating_transaction_success(self, client, auth_headers, test_transaction):
        """
        Test updating a transaction
        """
        response = client.put(
            f"/transactions/{test_transaction.id}",
            headers=auth_headers,
            json={
                "amount": 75.00,
                "description": "Updated grocery shopping",
            },
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["amount"] == 75.00
        assert data["description"] == "Updated grocery shopping"

    def test_update_transaction_not_found(self, client, auth_headers):
        """
        Test updating a non-existent transaction
        """
        invalid_id = uuid4()
        response = client.put(
            f"/transactions/{invalid_id}", headers=auth_headers, json={"amount": 100.00}
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestDeleteTransaction:
    def test_delete_transaction(self, client, auth_headers, test_transaction):
        """
        Test deleting a transaction
        """
        response = client.delete(
            f"/transactions/{test_transaction.id}", headers=auth_headers
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

        get_response = client.get(
            f"/transactions/{test_transaction.id}", headers=auth_headers
        )

        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_transaction_not_found(self, client, auth_headers):
        """
        Test deleting a non-existent transaction
        """
        invalid_id = uuid4()
        response = client.delete(f"/transactions/{invalid_id}", headers=auth_headers)

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestTransactionFilters:
    @pytest.fixture
    def multiple_transactions(self, test_db, test_user, test_category):
        """
        Create several test transactions
        """
        transactions = []
        for i in range(5):
            transaction = Transaction(
                user_id=test_user.id,
                catergory_id=test_category.id,
                amount=10.00 * (i + 1),
                description=f"transaction {i + 1}",
                date=datetime.now(timezone.utc),
                type="expense" if i % 2 == 0 else "income",
                account="Main Account",
                currency="GBP",
                status="completed",
            )
            test_db.add(transaction)
            transactions.append(transaction)

        test_db.commit()
        return transactions

    def test_pagination(self, client, auth_headers, multiple_transactions):
        """
        Test filtering by transaction type
        """
        response = client.get(
            "/transactions/", headers=auth_headers, params={"type": "expense"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert all(t["type"] == "expense" for t in data)
