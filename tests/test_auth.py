from fastapi import status


class TestUserRegistration:
    def test_registration_success(self, client):
        """
        Test successful user registration
        """
        response = client.post(
            "/auth/register",
            json={
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "passw0rd123",
                "first_name": "New",
                "last_name": "User",
                "currency_preference": "GBP",
                "monthly_budget": 2500,
            },
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["username"] == "newuser"
        assert data["email"] == "newuser@example.com"
        assert "hashed_password" not in data
        assert "id" in data

    def test_registration_duplicate_username(self, client, test_user):
        """
        Test registration fails with duplicate usernames
        """
        response = client.post(
            "/auth/register",
            json={
                "username": "testuser",
                "email": "differentuser@example.com",
                "password": "passw0rd123",
                "first_name": "Different",
                "last_name": "User",
                "currency_preference": "GBP",
                "monthly_budget": 2500,
            },
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Username already registered" in response.json()["detail"]

    def test_registration_duplicate_email(self, client, test_user):
        """
        Test registration fails with duplicate email
        """
        response = client.post(
            "/auth/register",
            json={
                "username": "differentuser",
                "email": "test@test.com",
                "password": "passw0rd123",
                "first_name": "Different",
                "last_name": "User",
                "currency_preference": "GBP",
                "monthly_budget": 2500,
            },
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Email already registered" in response.json()["detail"]

    def test_registration_invalid_email(self, client):
        """
        Test registration fails with invalid email format
        """
        response = client.post(
            "/auth/register",
            json={
                "username": "invaliduser",
                "email": "invalid-email-address",
                "password": "passw0rd123",
                "first_name": "Invalid",
                "last_name": "User",
                "currency_preference": "GBP",
                "monthly_budget": 2500,
            },
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


class TestUserLogin:
    def test_login_success(self, client, test_user):
        """
        Test successful login
        """
        response = client.post(
            "/auth/login", data={"username": "testuser", "password": "test1234"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_incorrect_pw(self, client):
        """
        Test login fails with incorrect password
        """
        response = client.post(
            "/auth/login", data={"username": "newuser", "password": "wrong_passw0rd123"}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid username or password" in response.json()["detail"]

    def test_login_nonexistent_user(self, client):
        """
        Test login fails for non-existent user
        """
        response = client.post(
            "/auth/login",
            data={"username": "nonexistentuser", "password": "passw0rd123"},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestDemoLogin:
    def test_demo_login_success(self, client, test_demo_user):
        """
        Test demo login works without password
        """
        response = client.post("/auth/demo-login")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_demo_login_no_demo_account(self, client):
        """
        Test demo login fails when no demo account exists
        """
        response = client.post("/auth/demo-login")

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestProtectedEndpoint:
    def test_current_user_success(self, client, test_user):
        """
        Test accessing protected endpoint with valid token
        """
        login_response = client.post(
            "/auth/login", data={"username": "testuser", "password": "test1234"}
        )

        token = login_response.json()["access_token"]

        response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@test.com"

    def test_current_user_no_token(self, client):
        """
        Test accessing protected endpoint with no token
        """
        response = client.get("/auth/me")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_current_user_invalid_token(self, client):
        """
        Test accessing protected endpoint with invalid token
        """
        response = client.get(
            "/auth/me", headers={"Authorization": "Bearer invalid_token"}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestDemoUserRestrictions:
    def test_demo_user_cannot_update_profile(self, client, test_demo_user):
        """
        Test demo user cannot update their profile
        """

        login_response = client.post("/auth/demo-login")
        token = login_response.json()["access_token"]

        response = client.put(
            "/users/me",
            headers={"Authorization": f"Bearer {token}"},
            json={"first_name": "Updated"},
        )

        assert response.status_code in [
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND,
        ]
