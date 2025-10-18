# In accounts/models.py
from django.db import models
from django.conf import settings
from django.urls import reverse

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    # You can store a Font Awesome class for the icon
    icon_class = models.CharField(max_length=50, default='fa-solid fa-shield-halved')

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Categories"

class Challenge(models.Model):
    class Difficulty(models.TextChoices):
        BEGINNER = 'beginner', 'Beginner'
        INTERMEDIATE = 'intermediate', 'Intermediate'
        ADVANCED = 'advanced', 'Advanced'
        EXPERT = 'expert', 'Expert'

    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='challenges')
    title = models.CharField(max_length=200)
    description = models.TextField()
    points = models.IntegerField()
    difficulty = models.CharField(max_length=20, choices=Difficulty.choices, default=Difficulty.BEGINNER)
    
    # To track completions (Many-to-Many with the User model)
    completed_by = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='completed_challenges', blank=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        # Creates a URL for each specific challenge
        # NOTE: You will need to create this 'challenge_detail' URL later
        return reverse('challenge_detail', args=[str(self.id)])