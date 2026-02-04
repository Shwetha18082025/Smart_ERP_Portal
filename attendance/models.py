from django.db import models
from accounts.models import User
from course.models import Course   # Link each period to a subject (course)


ATTENDANCE_STATUS = [
    ('P', 'Present'),
    ('A', 'Absent'),
    ('L', 'Late'),
]


class Attendance(models.Model):

    # Student being marked
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'is_student': True},
        related_name='attendance_records'
    )

    # Grade of student (1–10)
    grade = models.CharField(max_length=10, null=True, blank=True)

    # Subject taught during that period
    course = models.ForeignKey(
        Course,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='attendance_course'
    )

    # Attendance details
    date = models.DateField()
    period = models.IntegerField()       # 1–6 periods
    status = models.CharField(max_length=1, choices=ATTENDANCE_STATUS)

    # Marked by lecturer
    marked_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'is_lecturer': True},
        related_name='attendance_marked'
    )

    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'date', 'period')
        ordering = ['-date', 'period']

    def __str__(self):
        return f"{self.student} - {self.date} - Period {self.period}"
