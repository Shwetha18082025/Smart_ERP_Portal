from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from accounts.models import User
from .models import Attendance
import datetime

@login_required
def mark_attendance(request):
    # only lecturers or superusers
    if not request.user.is_lecturer and not request.user.is_superuser:
        return redirect("/")

    students = []
    selected_grade = None
    selected_period = None

    # grade options for the template
    grade_list = ["1","2","3","4","5","6","7","8","9","10"]

    # Load students (when the teacher clicks "Load Students")
    if request.method == "POST" and "load_students" in request.POST:
        selected_grade = request.POST.get("grade")
        selected_period = request.POST.get("period")

        # filter students by the grade field on User model
        students = User.objects.filter(is_student=True, grade=selected_grade).order_by('username')

    # Save attendance (when teacher clicks "Submit Attendance")
    elif request.method == "POST" and "save_attendance" in request.POST:
        grade = request.POST.get("grade")
        period = request.POST.get("period")
        date = datetime.date.today()

        for key in request.POST:
            if key.startswith("student_"):
                student_id = key.split("_", 1)[1]
                status = request.POST.get(key)  # 'P', 'A' or 'L'

                try:
                    student = User.objects.get(id=student_id)
                except User.DoesNotExist:
                    continue

                Attendance.objects.update_or_create(
                    student=student,
                    date=date,
                    period=period,
                    defaults={
                        "grade": grade,
                        "status": status,
                        "marked_by": request.user,
                    }
                )

        return render(request, "attendance/attendance_saved.html", {"date": date})

    return render(
        request,
        "attendance/mark_attendance.html",
        {
            "students": students,
            "selected_grade": selected_grade,
            "selected_period": selected_period,
            "grade_list": grade_list,
        },
    )
    

