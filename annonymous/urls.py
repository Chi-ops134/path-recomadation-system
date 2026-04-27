from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# REST API router
router = DefaultRouter()
router.register(r'api/students', views.StudentProfileViewSet)
router.register(r'api/courses',  views.CourseViewSet)
router.register(r'api/paths',    views.LearningPathViewSet)

urlpatterns = [

    # ── Auth ──────────────────────────────────
    path('',          views.login_view,    name='home'),
    path('register/', views.register_view, name='register'),
    path('login/',    views.login_view,    name='login'),
    path('logout/',   views.logout_view,   name='logout'),

    # ── Dashboard ─────────────────────────────
    path('dashboard/', views.dashboard_view, name='dashboard'),

    # ── Profile CRUD ──────────────────────────
    path('profile/',         views.profile_view,        name='profile'),
    path('profile/update/',  views.profile_update_view, name='profile-update'),
    path('profile/delete/',  views.profile_delete_view, name='profile-delete'),

    # ── AI Generate + Roadmap ─────────────────
    path('generate/',        views.generate_view,       name='generate'),
    path('roadmap/<int:pk>/',views.roadmap_view,         name='roadmap'),

    # ── History ───────────────────────────────
    path('history/',                    views.history_view,        name='history'),
    path('history/delete/<int:pk>/',    views.history_delete_view, name='history-delete'),

    # ── REST API ──────────────────────────────
    path('', include(router.urls)),
    path('api/generate/', views.GeneratePathAPIView.as_view(), name='api-generate'),
]
