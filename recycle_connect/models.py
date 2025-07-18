from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
import os

# def material_image_upload_path(instance, filename):
#     name, ext = os.path.splitext(filename)
#     safe_name = slugify(name) 
#     return f"materials/{safe_name}{ext.lower()}"
import os
import uuid
from django.utils.text import slugify

def material_image_upload_path(instance, filename):
    ext = os.path.splitext(filename)[1].lower()  
    material_slug = slugify(instance.name)       

    unique_id = uuid.uuid4().hex                  
    filename = f"{unique_id}{ext}"

    return f"materials/{material_slug}/{filename}"
import os
from django.db import models

class Material(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to=material_image_upload_path, blank=True, null=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        try:
            old = Material.objects.get(pk=self.pk)
        except Material.DoesNotExist:
            old = None

        super().save(*args, **kwargs) 

        if old and old.image and old.image != self.image:
            if os.path.isfile(old.image.path):
                os.remove(old.image.path)


class RecyclingCenter(models.Model):
    name = models.CharField(max_length=200)
    address = models.TextField()
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return self.name


class UserChallenge(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    progress = models.FloatField(default=0.0)
    joined_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s Challenge Progress"


class RecyclingProof(models.Model):
    challenge = models.ForeignKey(UserChallenge, related_name='proofs', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='proofs/')
    verified = models.BooleanField(default=False)


class Reward(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rewards')
    title = models.CharField(max_length=255)
    description = models.TextField()
    date_awarded = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.user.username}"


class VolunteerOpportunity(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=255)
    date = models.DateField()
    max_volunteers = models.PositiveIntegerField(default=20)
    image = models.ImageField(upload_to='opportunities/', null=True, blank=True)

    def __str__(self):
        return self.title


class VolunteerSignup(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    opportunity = models.ForeignKey(VolunteerOpportunity, on_delete=models.CASCADE, related_name='volunteersignup_set')
    hours_completed = models.PositiveIntegerField(default=0)
    certified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.opportunity.title}"


class ForumPost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class Comment(models.Model):
    post = models.ForeignKey(ForumPost, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)



class Poll(models.Model):
    question = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.question


class PollOption(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name='options')
    text = models.CharField(max_length=255)

    def __str__(self):
        return self.text


class Vote(models.Model):
    option = models.ForeignKey(PollOption, on_delete=models.CASCADE, related_name='votes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('option', 'user')


# Suggestion system 

class Suggestion(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    post = models.ForeignKey(ForumPost, on_delete=models.CASCADE, related_name='suggestions')
    text = models.TextField()
    votes = models.ManyToManyField(User, related_name='suggestion_votes', blank=True)

    def __str__(self):
        return f"Suggestion by {self.user.username} on {self.post.title}"

    class Meta:
        unique_together = ('post', 'user')


# Reactions 

class ReactionType(models.TextChoices):
    LIKE = 'like', 'Like'
    LOVE = 'love', 'Love'
    HAHA = 'haha', 'Haha'
    WOW = 'wow', 'Wow'
    SAD = 'sad', 'Sad'
    ANGRY = 'angry', 'Angry'


class PostReaction(models.Model):
    post = models.ForeignKey('ForumPost', on_delete=models.CASCADE, related_name='reactions')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reaction = models.CharField(max_length=10, choices=ReactionType.choices)

    class Meta:
        unique_together = ('post', 'user')

from django.db import models
from django.contrib.auth.models import User

class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    date = models.DateField()
    location = models.CharField(max_length=200)

    def __str__(self):
        return self.title

class EventRegistration(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    registered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'event')

    def __str__(self):
        return f"{self.name} - {self.event.title}"


class PickupReminder(models.Model):
    pickup_datetime = models.DateTimeField()
    phone = models.CharField(max_length=15, blank=True)
    email = models.EmailField(blank=True)
    reminder_time = models.DateTimeField()  
    created_at = models.DateTimeField(auto_now_add=True)

class Reminder(models.Model):
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    reminder_time = models.DateTimeField()
    message = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Reminder for {self.email or self.phone} at {self.reminder_time}"
