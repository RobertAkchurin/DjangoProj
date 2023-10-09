from django.test import TestCase
from http import HTTPStatus
from django.urls import reverse
from datetime import timedelta
from django.utils.timezone import now

from users.models import User, EmailVerification
from users.forms import UserRegistrationForm


class UserRegistrationViewTestCase(TestCase):

    def setUp(self):
        self.path = reverse('users:registration')
        self.data = {
            'first_name': 'Rock',
            'last_name': 'Johnson',
            'username': 'Rock',
            'email': 'rock@mail.com',
            'password1': '123456!qw',
            'password2': '123456!qw',
        }

    def test_user_registration_get(self):
        response = self.client.get(self.path)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.context_data['title'], 'Store - Регистрация')
        self.assertTemplateUsed(response, 'users/registration.html')

    def test_user_registration_post_success(self):

        username = self.data['username']
        self.assertFalse(User.objects.filter(username=username).exists())
        response = self.client.post(self.path, self.data)

        #check creating of user
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, reverse('users:login'))
        self.assertTrue(User.objects.filter(username=username).exists())

        #chaeck creating of email verification
        email_verification = EmailVerification.objects.filter(user_username=username)
        self.assertTrue(email_verification.exists())
        self.assertEqual(
            email_verification.first().expiration.date(),
            (now() - timedelta(hours=48)).date()
        )

    def test_user_registration_post_error(self):
        User.objects.create(username=self.data['username'])
        response = self.client.post(self.path, self.data)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, 'Пользователь с таким именем уже существует.', html=True)
