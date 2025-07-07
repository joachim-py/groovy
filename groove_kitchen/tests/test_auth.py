import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from groove_kitchen.models import Customer
from groove_kitchen.utils import is_valid_email

@pytest.mark.django_db
class TestAuthentication:
    def test_registration_view_get(self, client):
        response = client.get(reverse('registration'))
        assert response.status_code == 200
        assert 'registration/registration.html' in [t.name for t in response.templates]

    def test_registration_view_post_success(self, client):
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email_address': 'john.doe@example.com',
            'password': 'testpassword123'
        }
        response = client.post(reverse('registration'), data)
        assert response.status_code == 200
        response_data = response.json()
        assert response_data['status'] == 200
        assert response_data['message'] == 'Your account was successfully created!'
        
        # Verify user was created
        user = User.objects.get(email='john.doe@example.com')
        assert user.first_name == 'John'
        assert user.last_name == 'Doe'
        assert user.check_password('testpassword123')

    def test_registration_email_taken(self, client):
        # Create a user first
        User.objects.create_user(
            username='existing@example.com',
            email='existing@example.com',
            password='testpass123'
        )
        
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email_address': 'existing@example.com',
            'password': 'testpassword123'
        }
        response = client.post(reverse('registration'), data)
        assert response.status_code == 200
        response_data = response.json()
        assert response_data['status'] == 'email_taken'

    def test_registration_short_password(self, client):
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email_address': 'john.doe@example.com',
            'password': 'short'
        }
        response = client.post(reverse('registration'), data)
        assert response.status_code == 200
        response_data = response.json()
        assert response_data['status'] == 'short_password'

    def test_registration_invalid_email(self, client):
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email_address': 'invalid-email',
            'password': 'testpassword123'
        }
        response = client.post(reverse('registration'), data)
        assert response.status_code == 200
        response_data = response.json()
        assert response_data['status'] == 'invalid_email'

    def test_login_view_get(self, client):
        response = client.get(reverse('login_view'))
        assert response.status_code == 200
        assert 'registration/login.html' in [t.name for t in response.templates]

    def test_login_view_post_success(self, client):
        # Create a user first
        user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='testpass123',
            is_staff=False
        )
        
        data = {
            'email_address': 'test@example.com',
            'password': 'testpass123'
        }
        response = client.post(reverse('login_view'), data)
        assert response.status_code == 302  # Redirect to home
        assert response.url == reverse('home')

    def test_login_view_post_invalid_credentials(self, client):
        data = {
            'email_address': 'nonexistent@example.com',
            'password': 'wrongpass'
        }
        response = client.post(reverse('login_view'), data)
        assert response.status_code == 200
        response_data = response.json()
        assert response_data['status'] == 404

    @pytest.mark.django_db
    def test_password_reset_flow(self, client):
        # Create a user
        user = User.objects.create_user(
            username='reset@example.com',
            email='reset@example.com',
            password='oldpass123',
            first_name='Reset',
            last_name='User'
        )

        # Test password form
        response = client.post(reverse('password_form'), {'email_address': 'reset@example.com'})
        assert response.status_code == 200
        response_data = response.json()
        assert response_data['status'] == 200
        
        # Verify customer record was created with validation code
        customer = Customer.objects.get(user=user)
        assert customer.validation_code is not None

        # Test validation code verification
        response = client.post(reverse('password_done'), {'validation_code': customer.validation_code})
        assert response.status_code == 200
        response_data = response.json()
        assert response_data['status'] == 200
        assert response_data['uid'] == user.pk

        # Test password confirmation
        new_password = 'newpass123'
        response = client.post(reverse('password_confirm', kwargs={'uidb64': user.pk}), {
            'password': new_password,
            'confirm_password': new_password
        })
        assert response.status_code == 200
        response_data = response.json()
        assert response_data['status'] == 200

        # Verify password was actually changed
        user.refresh_from_db()
        assert user.check_password(new_password)

    def test_is_valid_email(self):
        assert is_valid_email('test@example.com') == True
        assert is_valid_email('invalid-email') == False
        assert is_valid_email('test@example') == False
        assert is_valid_email('test.email+alias@example.co.uk') == True
