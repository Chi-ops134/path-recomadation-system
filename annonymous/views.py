from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from .models import StudentProfile, Course, LearningPath
from .forms import RegisterForm, ProfileUpdateForm, GeneratePathForm
from .serializers import StudentProfileSerializer, CourseSerializer, LearningPathSerializer
from .services import generate_full_path


# ══════════════════════════════════════════════════════════
#  AUTH VIEWS
# ══════════════════════════════════════════════════════════

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome, {user.profile.full_name}! 🎉 Your journey starts now.")
            return redirect('dashboard')
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


# ══════════════════════════════════════════════════════════
#  DASHBOARD
# ══════════════════════════════════════════════════════════

@login_required
def dashboard_view(request):
    profile      = get_object_or_404(StudentProfile, user=request.user)
    recent_paths = LearningPath.objects.filter(student=profile)[:3]
    total_paths  = LearningPath.objects.filter(student=profile).count()
    return render(request, 'dashboard.html', {
        'profile':      profile,
        'recent_paths': recent_paths,
        'total_paths':  total_paths,
    })


# ══════════════════════════════════════════════════════════
#  PROFILE VIEWS (CRUD)
# ══════════════════════════════════════════════════════════

@login_required
def profile_view(request):
    profile = get_object_or_404(StudentProfile, user=request.user)
    return render(request, 'profile.html', {'profile': profile})


@login_required
def profile_update_view(request):
    profile = get_object_or_404(StudentProfile, user=request.user)
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully! ✅")
            return redirect('profile')
        else:
            messages.error(request, "Please fix the errors.")
    else:
        form = ProfileUpdateForm(instance=profile)
    return render(request, 'profile_update.html', {'form': form, 'profile': profile})


@login_required
def profile_delete_view(request):
    if request.method == 'POST':
        user = request.user
        logout(request)
        user.delete()
        messages.success(request, "Your account has been deleted.")
        return redirect('register')
    return render(request, 'profile_delete.html')


# ══════════════════════════════════════════════════════════
#  GENERATE PATH + ROADMAP
# ══════════════════════════════════════════════════════════

@login_required
def generate_view(request):
    profile = get_object_or_404(StudentProfile, user=request.user)
    if request.method == 'POST':
        form = GeneratePathForm(request.POST)
        if form.is_valid():
            goal = form.cleaned_data['goal']
            try:
                roadmap, youtube_videos = generate_full_path(profile, goal)
                # Save to DB
                path = LearningPath.objects.create(
                    student      = profile,
                    title        = roadmap.get('title', 'My Learning Path'),
                    goal         = goal,
                    roadmap_json = roadmap,
                    youtube_json = youtube_videos,
                )
                messages.success(request, "Your AI roadmap is ready! 🚀")
                return redirect('roadmap', pk=path.id)
            except Exception as e:
                messages.error(request, f"AI generation failed: {str(e)}")
    else:
        form = GeneratePathForm()
    return render(request, 'generate.html', {'form': form, 'profile': profile})


@login_required
def roadmap_view(request, pk):
    profile = get_object_or_404(StudentProfile, user=request.user)
    path    = get_object_or_404(LearningPath, pk=pk, student=profile)
    roadmap = path.roadmap_json
    youtube = path.youtube_json  # dict: {week_range: [videos]}
    return render(request, 'roadmap.html', {
        'path':    path,
        'roadmap': roadmap,
        'youtube': youtube,
    })


# ══════════════════════════════════════════════════════════
#  PATH HISTORY
# ══════════════════════════════════════════════════════════

@login_required
def history_view(request):
    profile = get_object_or_404(StudentProfile, user=request.user)
    paths   = LearningPath.objects.filter(student=profile)
    return render(request, 'history.html', {'paths': paths, 'profile': profile})


@login_required
def history_delete_view(request, pk):
    profile = get_object_or_404(StudentProfile, user=request.user)
    path    = get_object_or_404(LearningPath, pk=pk, student=profile)
    if request.method == 'POST':
        path.delete()
        messages.success(request, "Path deleted.")
    return redirect('history')


# ══════════════════════════════════════════════════════════
#  REST API VIEWSETS
# ══════════════════════════════════════════════════════════

class StudentProfileViewSet(viewsets.ModelViewSet):
    queryset           = StudentProfile.objects.all()
    serializer_class   = StudentProfileSerializer


class CourseViewSet(viewsets.ModelViewSet):
    queryset           = Course.objects.all()
    serializer_class   = CourseSerializer


class LearningPathViewSet(viewsets.ModelViewSet):
    queryset           = LearningPath.objects.all()
    serializer_class   = LearningPathSerializer


class GeneratePathAPIView(APIView):
    """API endpoint to generate learning path — for mobile/external use."""
    def post(self, request):
        student_id = request.data.get('student_id')
        goal       = request.data.get('goal')
        if not student_id or not goal:
            return Response({'error': 'student_id and goal required'}, status=400)
        try:
            profile         = StudentProfile.objects.get(id=student_id)
            roadmap, videos = generate_full_path(profile, goal)
            path            = LearningPath.objects.create(
                student      = profile,
                title        = roadmap.get('title', 'My Learning Path'),
                goal         = goal,
                roadmap_json = roadmap,
                youtube_json = videos,
            )
            return Response({'path_id': path.id, 'roadmap': roadmap}, status=200)
        except StudentProfile.DoesNotExist:
            return Response({'error': 'Student not found'}, status=404)
        except Exception as e:
            return Response({'error': str(e)}, status=500)
