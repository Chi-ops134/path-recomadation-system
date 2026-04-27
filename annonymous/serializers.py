from rest_framework import serializers
from .models import StudentProfile, Course, LearningPath


class StudentProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model  = StudentProfile
        fields = ['id', 'username', 'full_name', 'skills', 'interests',
                  'learning_goals', 'experience_level', 'created_at']


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Course
        fields = '__all__'


class LearningPathSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)

    class Meta:
        model  = LearningPath
        fields = ['id', 'student_name', 'title', 'goal',
                  'roadmap_json', 'youtube_json', 'created_at']
