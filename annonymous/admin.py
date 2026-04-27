from django.contrib import admin

# Register your models here.
from .models import StudentProfile, Course, LearningPath

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display  = ['full_name', 'experience_level', 'created_at']
    search_fields = ['full_name']
    list_filter   = ['experience_level']

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display  = ['title', 'level', 'duration_weeks']
    list_filter   = ['level']

@admin.register(LearningPath)
class LearningPathAdmin(admin.ModelAdmin):
    list_display  = ['student', 'title', 'created_at']
    list_filter   = ['created_at']
