from uuid import uuid4

import pytest
from fastapi import status

from app.models import Category, Transaction


@pytest.fixture
def auth_headers(client, test_user):
    """
    Get auth headers for test user
    """
    response = client.post(
        "/auth/login", data={"username": "testuser", "password": "test1234"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def default_category(test_db):
    """
    A default category created in the db
    """
    category = Category(
        name="Groceries",
        type="expense",
        description="Grocery and household items shopping",
        icon="🛒",
        colour="#D4C6E0",
        is_default=True,
    )
    test_db.add(category)
    test_db.commit()
    test_db.refresh(category)
    return category


@pytest.fixture
def user_category(test_db, test_user):
    """
    A custom category created by the user
    """
    category = Category(
        name="Side Hustle",
        type="income",
        description="Freelance and side project",
        icon="💻",
        colour="#7851A9",
        is_default=False,
        user_id=test_user.id,
    )
    test_db.add(category)
    test_db.commit()
    test_db.refresh(category)
    return category


class TestGetCategories:
    def test_get_categories_with_auth(self, client):
        response = client.get("/categories/")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_categories_returns_default(
        self, client, auth_headers, default_category, user_category
    ):
        response = client.get("/categories/", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        names = {c["name"] for c in data}
        assert "Groceries" in names
        assert "Side Hustle" in names


class TestGetSingleCategory:
    def test_get_single_category(self, client, auth_headers, default_category):
        """
        Test getting a single category
        """
        response = client.get(
            f"/categories/{default_category.id}", headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == str(default_category.id)
        assert data["name"] == default_category.name

    def test_get_category_not_found(self, client, auth_headers):
        """
        Test getting non-existent category
        """
        invalid_id = uuid4()
        response = client.get(f"/categories/{invalid_id}", headers=auth_headers)

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestCreateCategory:
    def test_create_category_success(self, client, auth_headers):
        """
        Test creating a category successfully
        """
        response = client.post(
            "/categories/",
            headers=auth_headers,
            json={
                "name": "Vacation",
                "type": "expense",
                "description": "Travel and holidays",
                "icon": "✈️",
                "colour": "#82C8E5",
            },
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "Vacation"
        assert data["is_default"] is False

    def test_create_category_duplicate_name(
        self, client, auth_headers, default_category
    ):
        """
        Test creating a category with the same name
        """
        response = client.post(
            "/categories/",
            headers=auth_headers,
            json={
                "name": "Groceries",
                "type": "expense",
                "description": "Duplicate name",
                "icon": "🛒",
                "colour": "#D4C6E0",
            },
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_category_require_auth(self, client):
        """
        Test create category without auth
        """
        response = client.post(
            "/categories/",
            json={
                "name": "NoAuth",
                "type": "expense",
                "description": "Test",
                "icon": "❌",
                "colour": "#FF0000",
            },
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestUpdateCategory:
    def test_update_category(self, client, auth_headers, user_category):
        """
        Test user updating category
        """
        response = client.post(
            f"/categories/{user_category.id}",
            headers=auth_headers,
            json={"name": "Side Income", "description": "Updated description"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Side Income"
        assert data["description"] == "Updated description"

    def test_update_default_category_unauthorised(
        self, client, auth_headers, default_category
    ):
        response = client.put(
            f"/categories/{default_category.id}",
            headers=auth_headers,
            json={"name": "Update Name Attempt"},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_update_category_not_found(self, client, auth_headers):
        invalid_id = uuid4()
        response = client.put(
            f"/categories/{invalid_id}",
            headers=auth_headers,
            json={"name": "Unknown category"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestDeleteCategory:
    def test_delete_category(self, client, auth_headers, test_db, test_user):
        """
        Test user updating category
        """
        cat = Category(
            name="Delete this",
            type="expense",
            description="Temporary",
            icon="🗑️",
            colour="#000000",
            is_default=False,
            user_id=test_user.id,
        )
        test_db.add(cat)
        test_db.commit()
        test_db.refresh(cat)

        response = client.delete(f"/categories/{cat.id}", headers=auth_headers)
        assert response.status_code == status.HTTP_204_NO_CONTENT

        get_response = client.get(f"categories/{cat.id}", headers=auth_headers)
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_default_category(self, client, auth_headers, default_category):
        """
        Test deletion of default category
        """
        response = client.delete(
            f"/categories/{default_category.id}", headers=auth_headers
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_category_with_transaction(
        self, client, auth_headers, test_db, test_user
    ):
        transaction = Transaction(
            user_id=test_user.id,
            category_id=user_category.id,
            amount=20.00,
            description="Test transaction",
            date=None,
            type="expense",
            account="Main",
            currency="GBP",
            status="completed",
        )
        test_db.add(transaction)
        test_db.commit()

        response = client.delete(
            f"/categories/{user_category.id}", headers=auth_headers
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
