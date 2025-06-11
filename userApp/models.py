from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

class UserResponse(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    age = models.IntegerField()
    gender = models.CharField(max_length=10)
    cgpa = models.DecimalField(max_digits=3, decimal_places=2)
    semester_credit_load = models.IntegerField()
    sleep_quality = models.CharField(max_length=10)
    physical_activity = models.CharField(max_length=10)
    diet_quality = models.CharField(max_length=10)
    social_support = models.CharField(max_length=10)
    relationship_status = models.CharField(max_length=10)
    financial_stress = models.IntegerField()
    substance_use = models.CharField(max_length=10, blank=True, null=True)
    counseling_service_use = models.CharField(max_length=10, blank=True, null=True)
    family_history = models.CharField(max_length=10, blank=True, null=True)
    chronic_illness = models.CharField(max_length=10, blank=True, null=True)
    extracurricular_involvement = models.CharField(max_length=10, blank=True, null=True)
    residence_type = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return f"Response #{self.id}"

class Prediction(models.Model):
    user_response = models.ForeignKey(UserResponse, on_delete=models.CASCADE)
    stress_level = models.DecimalField(max_digits=3, decimal_places=2)
    depression_score = models.DecimalField(max_digits=3, decimal_places=2)
    anxiety_score = models.DecimalField(max_digits=3, decimal_places=2)
    predict_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Prediction for {self.user_response}"
    

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(
        upload_to='profile_pics',
        default='profile_pics/default-avatar.png'
    )
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f'{self.user.username} Profile'

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
    