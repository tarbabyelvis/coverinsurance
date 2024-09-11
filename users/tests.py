from django.contrib.auth import get_user_model
from django.test import TestCase


class UsersManagersTests(TestCase):

    def test_create_user(self):
        User = get_user_model()
        user = User.objects.create_user(email='normal@user.com', password='normal')
        self.assertTrue(user.email, 'normal@user.com')
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

        try:
            # AbstractUser or AbstractBaseUser has no username
            self.assertIsNone(user.username)
        except AttributeError:
            pass

        with self.assertRaises(TypeError):
            user = User.objects.create_user()
        with self.assertRaises(TypeError):
            user = User.objects.create_user(email='')
        with self.assertRaises(ValueError):
            user = User.objects.create_user(email='', password='foo')

    def test_create_superuser(self):
        User = get_user_model()
        user = User.objects.create_superuser(email='super@user.com', password='super')
        self.assertTrue(user.email, 'super@user.com')
        self.assertTrue(user.is_active)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

        try:
            # AbstractUser or AbstractBaseUser has no username
            self.assertIsNone(user.username)
        except AttributeError:
            pass

        with self.assertRaises(ValueError):
            user = User.objects.create_superuser(
                email='super2@user.com', password='foo', is_superuser=False)

