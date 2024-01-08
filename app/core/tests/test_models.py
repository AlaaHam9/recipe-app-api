from django.contrib.auth import get_user_model
from django.test import TestCase
from decimal import Decimal
from core import models


def create_user(email='test@example.com', password='testpass123'):
    return get_user_model().objects.create_user(email, password)


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


    def test_create_recipe(self):
        user = get_user_model().objects.create_user(
            email = 'test@example.com',
            password = 'pass451'
        )

        recipe = models.Recipe.objects.create(
            user = user,
            title= 'Sample recipe name',
            time_minutes=5,
            price=Decimal('5.50'),
            description='Sample recipe description'
        )

        self.assertEqual(str(recipe), recipe.title)

    # def test_create_tag(self):
    #     user = create_user()
    #     tag = models.Tag.objects.create(
    #         user=user, name='Tags1'
    #     )

    #     self.assertEqual(str(tag), tag.title)