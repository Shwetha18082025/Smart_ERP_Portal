from django.contrib import admin
from .models import Attendance


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = (
        'student',
        'grade',
        'course',
        'date',
        'period',
        'status',
        'marked_by',
    )

    list_filter = (
        'grade',
        'date',
        'course',
        'period',
        'status',
    )

    search_fields = (
        'student__username',
        'student__first_name',
        'student__last_name',
    )

    ordering = ('-date', 'period')
