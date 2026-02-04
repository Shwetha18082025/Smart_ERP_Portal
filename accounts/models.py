from django.db import models
from django.urls import reverse
from django.contrib.auth.models import AbstractUser, UserManager
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.db.models import Q
from PIL import Image

from course.models import Program
from .validators import ASCIIUsernameValidator


# DEGREE OPTIONS
PRIMARY = _("Primary")
SECONDARY = _("Secondary")
HIGH_SCHOOL = _("High School")

LEVEL = (
    (PRIMARY, _("Primary")),
    (SECONDARY, _("Secondary")),
    (HIGH_SCHOOL, _("High School")),
)

# PARENT RELATION OPTIONS
FATHER = _("Father")
MOTHER = _("Mother")
BROTHER = _("Brother")
SISTER = _("Sister")
GRAND_MOTHER = _("Grand mother")
GRAND_FATHER = _("Grand father")
OTHER = _("Other")

RELATION_SHIP = (
    (FATHER, _("Father")),
    (MOTHER, _("Mother")),
    (BROTHER, _("Brother")),
    (SISTER, _("Sister")),
    (GRAND_MOTHER, _("Grand mother")),
    (GRAND_FATHER, _("Grand father")),
    (OTHER, _("Other")),
)


# --------------------------------------------------------
# USER MANAGER
# --------------------------------------------------------
class CustomUserManager(UserManager):
    def search(self, query=None):
        queryset = self.get_queryset()
        if query:
            or_lookup = (
                Q(username__icontains=query)
                | Q(first_name__icontains=query)
                | Q(last_name__icontains=query)
                | Q(email__icontains=query)
            )
            queryset = queryset.filter(or_lookup).distinct()
        return queryset

    def get_student_count(self):
        return self.model.objects.filter(is_student=True).count()

    def get_lecturer_count(self):
        return self.model.objects.filter(is_lecturer=True).count()

    def get_superuser_count(self):
        return self.model.objects.filter(is_superuser=True).count()


# --------------------------------------------------------
# CUSTOM USER MODEL
# --------------------------------------------------------
GENDERS = ((_("M"), _("Male")), (_("F"), _("Female")))


class User(AbstractUser):
    is_student = models.BooleanField(default=False)
    is_lecturer = models.BooleanField(default=False)
    is_parent = models.BooleanField(default=False)
    is_dep_head = models.BooleanField(default=False)

    gender = models.CharField(max_length=1, choices=GENDERS, blank=True, null=True)
    phone = models.CharField(max_length=60, blank=True, null=True)
    address = models.CharField(max_length=60, blank=True, null=True)

    picture = models.ImageField(
        upload_to="profile_pictures/%y/%m/%d/", default="default.png", null=True
    )

    email = models.EmailField(blank=True, null=True)

    username_validator = ASCIIUsernameValidator()

    # ⭐ NEW FIELD for school-level system
    grade = models.CharField(max_length=10, null=True, blank=True)

    # Parent of the child (if user is_parent)
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="children",
    )

    objects = CustomUserManager()

    class Meta:
        ordering = ("-date_joined",)

    @property
    def get_full_name(self):
        full_name = self.username
        if self.first_name and self.last_name:
            full_name = self.first_name + " " + self.last_name
        return full_name

    def __str__(self):
        return f"{self.username} ({self.get_full_name})"

    @property
    def get_user_role(self):
        if self.is_superuser:
            return _("Admin")
        elif self.is_student:
            return _("Student")
        elif self.is_lecturer:
            return _("Lecturer")
        elif self.is_parent:
            return _("Parent")
        elif self.is_dep_head:
            return _("Department Head")
        return _("User")

    def get_picture(self):
        try:
            return self.picture.url
        except:
            return settings.MEDIA_URL + "default.png"

    def get_absolute_url(self):
        return reverse("profile_single", kwargs={"id": self.id})

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Resize image if large
        try:
            img = Image.open(self.picture.path)
            if img.height > 300 or img.width > 300:
                img.thumbnail((300, 300))
                img.save(self.picture.path)
        except:
            pass

    def delete(self, *args, **kwargs):
        if self.picture.url != settings.MEDIA_URL + "default.png":
            self.picture.delete()
        super().delete(*args, **kwargs)


# --------------------------------------------------------
# STUDENT MODEL
# --------------------------------------------------------
class StudentManager(models.Manager):
    def search(self, query=None):
        qs = self.get_queryset()
        if query:
            or_lookup = Q(level__icontains=query) | Q(program__icontains=query)
            qs = qs.filter(or_lookup).distinct()
        return qs


class Student(models.Model):
    student = models.OneToOneField(User, on_delete=models.CASCADE)
    level = models.CharField(max_length=25, choices=LEVEL, null=True)
    program = models.ForeignKey(Program, on_delete=models.CASCADE, null=True)

    objects = StudentManager()

    class Meta:
        ordering = ("-student__date_joined",)

    def __str__(self):
        return self.student.get_full_name

    @classmethod
    def get_gender_count(cls):
        males = cls.objects.filter(student__gender="M").count()
        females = cls.objects.filter(student__gender="F").count()
        return {"M": males, "F": females}

    def get_absolute_url(self):
        return reverse("profile_single", kwargs={"id": self.id})

    def delete(self, *args, **kwargs):
        self.student.delete()
        super().delete(*args, **kwargs)


# --------------------------------------------------------
# PARENT MODEL
# --------------------------------------------------------
class Parent(models.Model):
    """
    Connect student with their parent, parents can
    only view their connected students information
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="parent_profile"   # ⭐ FIXED HERE
    )

    student = models.OneToOneField(Student, null=True, on_delete=models.SET_NULL)

    first_name = models.CharField(max_length=120)
    last_name = models.CharField(max_length=120)
    phone = models.CharField(max_length=60, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    relation_ship = models.TextField(choices=RELATION_SHIP, blank=True)

    class Meta:
        ordering = ("-user__date_joined",)

    def __str__(self):
        return self.user.username


# --------------------------------------------------------
# DEPARTMENT HEAD
# --------------------------------------------------------
class DepartmentHead(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.ForeignKey(Program, on_delete=models.CASCADE, null=True)

    class Meta:
        ordering = ("-user__date_joined",)

    def __str__(self):
        return f"{self.user}"
