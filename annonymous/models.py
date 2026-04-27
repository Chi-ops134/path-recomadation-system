from django.db import models
from django.contrib.auth.models import User


# ─────────────────────────────────────────────
#  Student Profile
# ─────────────────────────────────────────────
class StudentProfile(models.Model):
    LEVEL_CHOICES = [
        ('beginner',     'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced',     'Advanced'),
    ]

    user             = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    full_name        = models.CharField(max_length=100)
    bio              = models.TextField(blank=True)
    profile_picture  = models.ImageField(upload_to='profiles/', blank=True, null=True)
    skills           = models.TextField(help_text="Comma separated. e.g: Python, SQL")
    interests        = models.TextField(help_text="Comma separated. e.g: ML, Web Dev")
    learning_goals   = models.TextField()
    experience_level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='beginner')
    created_at       = models.DateTimeField(auto_now_add=True)
    updated_at       = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.full_name} — {self.experience_level}"

    def skills_list(self):
        return [s.strip() for s in self.skills.split(',') if s.strip()]

    def interests_list(self):
        return [i.strip() for i in self.interests.split(',') if i.strip()]


# ─────────────────────────────────────────────
#  Course (catalog of available courses)
# ─────────────────────────────────────────────
class Course(models.Model):
    LEVEL_CHOICES = [
        ('beginner',     'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced',     'Advanced'),
    ]

    title               = models.CharField(max_length=200)
    description         = models.TextField()
    topics              = models.TextField(help_text="Comma separated topics")
    level               = models.CharField(max_length=20, choices=LEVEL_CHOICES)
    duration_weeks      = models.IntegerField(default=4)
    learning_objectives = models.TextField()
    prerequisites       = models.TextField(blank=True)
    resource_url        = models.URLField(blank=True)

    def __str__(self):
        return f"{self.title} ({self.level})"

    def topics_list(self):
        return [t.strip() for t in self.topics.split(',') if t.strip()]


# ─────────────────────────────────────────────
#  Learning Path (AI Generated Roadmap)
# ─────────────────────────────────────────────
class LearningPath(models.Model):
    student          = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='paths')
    title            = models.CharField(max_length=200)
    goal             = models.TextField()               # what student typed
    roadmap_json     = models.JSONField()               # AI generated JSON
    youtube_json     = models.JSONField(default=list)   # YouTube videos JSON
    created_at       = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.full_name} — {self.title}"

    class Meta:
        ordering = ['-created_at']
