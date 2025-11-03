from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Users must have')

        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_vetting_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_vetter', True)
        extra_fields.setdefault('is_staff', True)
        return self.create_user(email, password, **extra_fields)

    def create_verifier_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_verifier', True)
        extra_fields.setdefault('is_staff', True)
        return self.create_user(email, password, **extra_fields)

    def create_publisher_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_publisher', True, )
        return self.create_user(email, password, **extra_fields)

    def create_staff(self, email, password=None, **extra_fields):
        user = self.create_user(email, password, **extra_fields)
        user.is_staff = True
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password=None):
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user
