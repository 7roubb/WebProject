from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from .models import Student,SupportMessage,studentsReg,Courses,Prerequisties
from django.urls import reverse_lazy
from .models import Courses
from .form import CourseForm
from django.contrib.auth import logout
from .models import *
import random
from django.db.models import Q
from django.shortcuts import get_object_or_404
from .form import *
from django.views.generic import DetailView
import time

#add new user to the moddel
def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        name = request.POST['name']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']
        if password == password2:
            #valid email
            if User.objects.filter(email=email).exists():
                messages.info(request, 'Email Taken')
                return render(request, 'signup.html')
            #valid usename

            elif User.objects.filter(username=username).exists():
                messages.info(request, 'Username Taken')
                return render(request, 'signup.html')
            else:
                # if user is dont match any other user create the user 
                # and sign in 
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()
                user_login = auth.authenticate(username=username, password=password)
                auth.login(request, user_login)
                request.session['last_activity'] = time.time()  # Set session activity time
                user_model = User.objects.get(username=username)
                new_student = Student.objects.create(user=user_model, id_user=user_model.id,fullname=name,email=email)
                new_student.save()
                return redirect('/')
        else:
            messages.info(request, 'Password Not Matching')
            return render(request, 'signup.html') 
    else:
        return render(request, 'sign.html')
#sign in to the account 
def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            request.session['last_activity'] = time.time()  # Set session activity time
            return redirect('/')
        else:
            messages.info(request, 'Credentials Invalid')
            return render(request, 'sign.html')
    else:
        return render(request, 'sign.html')
def test(request):
    pass

@login_required(login_url='/login'  )
def home(request):
    userl = request.user#used to return user to the home page also i used this for the user photo in the navigatior u will see that i do the same thing may time becouse i 
    #need to return user to each page to get the user image 
    print(f'Logged-in user: {userl}')  
    student = Student.objects.filter(user=userl).first()
    print(f'Student found: {student}')
    courseAdmin = Courses.objects.all()
    courses = []
    students = Student.objects.all()
    #used to return the courses that the student register on it 
    if student:
        registrations = studentsReg.objects.filter(student_id=student)
        print(f'Registrations found: {registrations.count()}')
        for registration in registrations:
            course = registration.course_id
            courses.append(course)
            print(f'Registered Course: {course.name}, Code: {course.code}')
    return render(request, 'index.html', {'student': student, 'courses': courses,'courseAdmin':courseAdmin,'users':students} )


@login_required(login_url='login')
def logout_view(request):
    auth.logout(request)  
    return redirect('/')

# this page is additonal page to send a support message by the student to the admin and aslo admin will see the message 
@login_required(login_url='login')
def support(request):
    userl = request.user
    print(f'Logged-in user: {userl}')
    student = Student.objects.filter(user=userl).first()
    print(f'Student found: {student}')
    support_messages = []
    if userl.is_staff:  # Check if the user is an admin
        support_messages = SupportMessage.objects.all()
    return render(request, 'support.html', {'student': student, 'support_messages': support_messages})


@login_required(login_url='login')
def support_message(request):
    userl = request.user
    print(f'Logged-in user: {userl}')
    student = Student.objects.filter(user=userl).first()
    studentEmail = student.email
    if request.method == "POST":
        message = request.POST.get('message')
        if message:
            SupportMessage.objects.create(email=studentEmail, message=message)
        else:
            pass
    return redirect('support')


def signupview(request):
    return render(request, 'signup.html')

@login_required(login_url='login')
def profile(request):
    userl = request.user
    print(f'Logged-in user: {userl}') 
    student = Student.objects.filter(user=userl).first()
    print(f'Student found: {student}')
    return render(request, 'userd.html', {'student': student})

@login_required
def search_courses(request):
    userl = request.user
    print(f'Logged-in user: {userl}')
    student = Student.objects.filter(user=userl).first()
    print(f'Student found: {student}')  
    if request.method == "GET":
        query = request.GET.get('search', '')
        if query:
            courses = Courses.objects.filter(
                Q(code__icontains=query) | Q(name__icontains=query) | Q(instractor__icontains=query)
            )
            return render(request, 'search_results.html', {'courses': courses, 'student': student})
        else:
            return render(request, 'index.html')
    return redirect('')
@login_required
def register_course(request, course_code):
    if request.method == "POST":
        course = get_object_or_404(Courses, code=course_code)
        student = get_object_or_404(Student, user=request.user)
        if studentsReg.objects.filter(student_id=student, course_id=course).exists():
            messages.error(request, "You are already registered for this course.")
            return redirect('')  # Assuming 'home' is a valid URL name for the homepage
        num_registered_students = studentsReg.objects.filter(course_id=course).count()
        if num_registered_students >= course.capacity:
            messages.error(request, "The course capacity is full. You cannot register for this course.")
            return redirect('')
        prerequisites = Prerequisties.objects.filter(course=course)
        for prereq in prerequisites:
            if not studentsReg.objects.filter(student_id=student, course_id=prereq.course_prerequisite).exists():
                messages.error(request, f"You must complete {prereq.course_prerequisite.name} before registering for this course.")
                return redirect('')  # Redirect to homepage
        existing_registrations = studentsReg.objects.filter(student_id=student)
        for registration in existing_registrations:
            existing_course = registration.course_id
            if existing_course.schedule_id:
                if course.schedule_id and has_time_conflict(existing_course.schedule_id, course.schedule_id):
                    messages.error(request, f"Schedule conflict with {existing_course.name}.")
                    return redirect('')  # Redirect to homepage
        # Register for the course
        registration = studentsReg(student_id=student, course_id=course)
        registration.save()
        messages.success(request, "You have successfully registered for the course.")
    return redirect('')  # Redirect to homepage after processing the form
def has_time_conflict(schedule1, schedule2):
    if schedule1.days != schedule2.days:
        return False
    if schedule1.start_time < schedule2.end_time and schedule2.start_time < schedule1.end_time:
        return True
    return False
@login_required(login_url='/login'  )
def mycourses(request):
    userl = request.user
    print(f'Logged-in user: {userl}')
    student = Student.objects.filter(user=userl).first()
    print(f'Student found: {student}')
    courses_with_schedules = []    
    if student:
        registrations = studentsReg.objects.filter(student_id=student).select_related('course_id__schedule_id')       
        print(f'Registrations found: {registrations.count()}')
        for registration in registrations:
            course = registration.course_id
            schedule = course.schedule_id
            courses_with_schedules.append({
                'course_name': course.name,
                'course_code': course.code,
                'schedule_days': schedule.days if schedule else 'No schedule',
                'start_time': schedule.start_time if schedule else 'N/A',
                'end_time': schedule.end_time if schedule else 'N/A',
                'room_no': schedule.room_no if schedule else 'N/A',
                'instractor': course.instractor if schedule else 'N/A',
                'description': course.description if schedule else 'N/A',
            })
            print(f'Registered Course: {course.name}, Code: {course.code}, Schedule: {schedule}')
    
    return render(request, 'my_courses.html', {'student': student, 'courses': courses_with_schedules})

@login_required(login_url='/login'  )
def sittings(request):
    userl = request.user
    print(f'Logged-in user: {userl}')
    student = Student.objects.filter(user=userl).first()
    print(f'Student found: {student}')
    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES, instance=student)
        if form.is_valid():
            form.save()
            return redirect('')  # Assuming you have a URL named 'students_list'
    else:
        form = StudentForm(instance=student)
    return render(request, 'sitting.html' ,{'student': student, 'form': form})

@login_required(login_url='login')
def course_detail(request, course_code):
    course = get_object_or_404(Courses, code=course_code)
    user = request.user
    student = Student.objects.filter(user=user).first()

    # Get students registered in the course
    registrations = studentsReg.objects.filter(course_id=course)
    registered_students = [{
        'fullname': reg.student_id.fullname,
        'email': reg.student_id.email
    } for reg in registrations]

    # Check if the current user (student) is registered for the course
    user_is_registered = any(reg.student_id == student for reg in registrations) if student else False

    # Get prerequisites for the course
    prerequisites = Prerequisties.objects.filter(course=course)

    context = {
        'course': course,
        'schedule': course.schedule_id,
        'student': student,
        'registered_students': registered_students,
        'num_registered_students': len(registered_students),
        'is_admin': user.is_staff,
        'user_is_registered': user_is_registered,  # boolean value indicating registration status
        'prerequisites': prerequisites  # list of prerequisites
    }

    return render(request, 'course.html', context)

@staff_member_required
@login_required(login_url='login')
def add_course(request):
    user = request.user
    print(f'Logged-in user: {user}')
    
    student = Student.objects.filter(user=user).first()
    if not request.user.is_staff:
        messages.error(request, "You do not have permission to add courses.")
        return redirect('home')

    if request.method == 'POST':
        course_form = CourseForm(request.POST)
        schedule_form = ScheduleForm(request.POST)
        print('test1')
        if course_form.is_valid() and schedule_form.is_valid():
            schedule = schedule_form.save(commit=False)
            conflicting_courses = Courses.objects.filter(
                schedule_id__days=schedule.days,
                schedule_id__start_time__lt=schedule.end_time,
                schedule_id__end_time__gt=schedule.start_time,
                schedule_id__room_no=schedule.room_no
            )
            if conflicting_courses.exists():
                schedule_form.add_error('room_no', 'This schedule conflicts with another course.')
                messages.error(request, "Failed to add the course due to schedule conflicts.")
            else:
                schedule.save()
                course = course_form.save(commit=False)
                course.schedule_id = schedule
                bright_color = "#{:06X}".format(random.randint(0x888888, 0xFFFFFF))
                course.color = bright_color
                course.save()
                prerequisites = course_form.cleaned_data['prerequisites']
                for prerequisite in prerequisites:
                    Prerequisties.objects.create(course=course, course_prerequisite=prerequisite)
                messages.success(request, "Course and schedule added successfully.")
                return redirect('')  # Update with the correct URL name
        else:
            messages.error(request, "Invalid form entries. Please correct the data.")
            print('test2')
    else:
        course_form = CourseForm()
        schedule_form = ScheduleForm()

    context = {
        'course_form': course_form,
        'schedule_form': schedule_form,
        'student': student
    }
    return render(request, 'addcourse.html', context)

@login_required
def notifications_list(request):
    userl = request.user
    print(f'Logged-in user: {userl}')
    student = Student.objects.filter(user=userl).first()
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'notifications.html', {'notifications': notifications,'student': student})

@login_required
def mark_as_read(request, notification_id):
    userl = request.user
    print(f'Logged-in user: {userl}')
    student = Student.objects.filter(user=userl).first()
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    return redirect('notifications')

@staff_member_required
@login_required
def add_notification(request):
    userl = request.user
    print(f'Logged-in user: {userl}')
    student = Student.objects.filter(user=userl).first()
    if request.method == 'POST':
        title = request.POST['title']
        message = request.POST['message']
        users = User.objects.all()
        for user in users:
            Notification.objects.create(title=title, message=message, user=user)
        return redirect('notifications')
    return render(request, 'notification.html',{'student': student})
@login_required
@staff_member_required(login_url='login')
def delete_course(request, course_code):
    course = get_object_or_404(Courses, code=course_code)
    if request.method == 'POST':
        course_name = course.name
        schedule_id = course.schedule_id  # Store the schedule ID to delete after course deletion
        course.delete()  # Delete the course
        if schedule_id:  # If the course had an associated schedule, delete it
            schedule_id.delete()
        messages.success(request, f"The course '{course_name}' and its schedule have been deleted successfully.")
        return redirect('')  # Adjust this to the name of the URL where you list courses
    return render(request, 'index.html', {'course': course})

@login_required
def unregister_course(request, course_code):
    course = get_object_or_404(Courses, code=course_code)
    student = get_object_or_404(Student, user=request.user)

    if request.method == 'POST':
        registration = studentsReg.objects.filter(student_id=student, course_id=course).first()
        if registration:
            registration.delete()
            messages.success(request, "You have been unregistered from the course.")
        else:
            messages.error(request, "You are not registered for this course.")
        return redirect('')
    return redirect('' )

