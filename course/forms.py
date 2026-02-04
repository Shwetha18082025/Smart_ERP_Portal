# course/forms.py

from django import forms
from accounts.models import User
from .models import Program, Course, CourseAllocation, Upload, UploadVideo


# --------------------------
# PROGRAM FORM
# --------------------------
class ProgramForm(forms.ModelForm):
    class Meta:
        model = Program
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["title"].widget.attrs.update({"class": "form-control"})
        self.fields["summary"].widget.attrs.update({"class": "form-control"})


# --------------------------
# COURSE ADD FORM
# --------------------------
class CourseAddForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ["title", "code", "grade", "category", "summary"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control"})

# --------------------------
# COURSE ALLOCATION FORM  (FIXED)
# --------------------------
class CourseAllocationForm(forms.ModelForm):

    # ⚠️ FIXED — ORDER BY grade, not level
    courses = forms.ModelMultipleChoiceField(
        queryset=Course.objects.all().order_by("grade", "title"),
        widget=forms.CheckboxSelectMultiple(
            attrs={"class": "form-control", "size": 8}
        ),
        required=True,
        label="Courses (select multiple with Ctrl/Cmd)",
    )

    lecturer = forms.ModelChoiceField(
        queryset=User.objects.filter(is_lecturer=True),
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Lecturer",
    )

    class Meta:
        model = CourseAllocation
        fields = ["lecturer", "courses"]

    def __init__(self, *args, **kwargs):
        kwargs.pop("user", None)  # FIX: prevent crash if user not passed

        super().__init__(*args, **kwargs)
        self.fields["lecturer"].queryset = User.objects.filter(is_lecturer=True)
        # ensure courses always uses latest queryset (useful after migrations)
        self.fields["courses"].queryset = Course.objects.all().order_by("grade", "title")



# --------------------------
# EDIT COURSE ALLOCATION FORM (FIXED)
# --------------------------
class EditCourseAllocationForm(forms.ModelForm):
    courses = forms.ModelMultipleChoiceField(
        queryset=Course.objects.all().order_by("grade"),  # FIXED HERE TOO
        widget=forms.CheckboxSelectMultiple,
        required=True,
    )

    lecturer = forms.ModelChoiceField(
        queryset=User.objects.filter(is_lecturer=True),
        widget=forms.Select(attrs={"class": "browser-default custom-select"}),
        label="Lecturer",
    )

    class Meta:
        model = CourseAllocation
        fields = ["lecturer", "courses"]

    def __init__(self, *args, **kwargs):
        super(EditCourseAllocationForm, self).__init__(*args, **kwargs)
        self.fields["lecturer"].queryset = User.objects.filter(is_lecturer=True)
        self.fields["courses"].queryset = Course.objects.all().order_by("grade")


# --------------------------
# UPLOAD FILES FORM
# --------------------------
class UploadFormFile(forms.ModelForm):
    class Meta:
        model = Upload
        fields = ("title", "file")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["title"].widget.attrs.update({"class": "form-control"})
        self.fields["file"].widget.attrs.update({"class": "form-control"})


# --------------------------
# UPLOAD VIDEO FORM
# --------------------------
class UploadFormVideo(forms.ModelForm):
    class Meta:
        model = UploadVideo
        fields = ("title", "video")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["title"].widget.attrs.update({"class": "form-control"})
        self.fields["video"].widget.attrs.update({"class": "form-control"})
