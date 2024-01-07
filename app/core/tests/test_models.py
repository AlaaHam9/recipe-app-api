from django.contrib.auth import get_user_model
from django.test import TestCase

class ModelTest(TestCase):

    def test_create_user_with_email_successful(self):
        email= "test@example.com"
        password= "test123"
        # create_user added by user manager
        user = get_user_model().objects.create_user(
            password= password,
            email= email
        )
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        sample_emails= [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.COM', 'TEST3@example.com'],
            ['test4@EXAMPLE.COM', 'test4@example.com'],
        ]
        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, 'sample123')
            self.assertEqual(user.email, expected)

    def test_create_user_without_email_raises_error(self):
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('','p123')

    def test_create_superuser(self):
        user = get_user_model().objects.create_superuser(
            email = 'test@example.com',
            password = 'test123'
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)