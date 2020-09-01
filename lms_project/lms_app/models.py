from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.contrib.auth.models import User


# Create your models here.


class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and sauthtokenave a regular User with the given email and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)



class User(AbstractUser):
    """User model."""

    username = None
    email = models.EmailField('Email Address', unique=True)
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    mobile = models.CharField(max_length=10, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add = True)
    modified_at = models.DateTimeField(auto_now = True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['password']

    objects = UserManager()




SEMESTER_CHOICES = (
    (1, 1),
    (2, 2),
    (3, 3),
    (4, 4),
    (5, 5),
    (6, 6),
    (7, 7),
    (8, 8),
)


class Student(models.Model):
    """Student model."""

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    enrollment_no = models.CharField(max_length=16)
    semester = models.IntegerField(choices=SEMESTER_CHOICES)
    total_book_issued = models.IntegerField(default=0)

    def __str__(self):
        return self.user.email



class Staff(models.Model):
    """Staff model."""

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    staff_id = models.CharField(max_length=16)

    def __str__(self):
        return self.user.email



class Department(models.Model):
    """Department model."""

    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name



BOOK_STATUS_CHOICES = (
    ("available", "Available"),
    ("issued", "Issued"),
)


class Book(models.Model):
    """Book model."""

    name = models.CharField(max_length=20, unique=True)
    isbn = models.CharField(max_length=16)   
    author = models.CharField(max_length=20)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    total_quantity = models.IntegerField(default=1)
    issued_quantity = models.IntegerField(default=0)
    available_quantity = models.IntegerField(default=1)
    status = models.CharField(choices = BOOK_STATUS_CHOICES, max_length=16, default="available") 


    def __str__(self):
        return self.name



BOOK_ISSUE_STATUS = (
    ('pending', 'Pending'), 
    ('issued', 'Issued'), 
    ('returned', 'Returned'), 
    ('closed', 'Closed'),
    ('rejected', 'Rejected')
)


class BookIssueDetail(models.Model):
    """Book Issue Detail model."""

    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    request_date = models.DateField(blank=True, null=True)
    issue_date = models.DateField(blank=True, null=True)
    return_date = models.DateField(blank=True, null=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, blank=True, null=True)
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, blank=True, null=True)
    charge = models.IntegerField(default=0)
    status = models.CharField(choices = BOOK_ISSUE_STATUS, max_length=16, default='pending')

    def __str__(self):
        return self.book.name

