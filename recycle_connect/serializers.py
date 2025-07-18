from rest_framework import serializers
from .models import Material, RecyclingCenter
from django.contrib.auth.models import User
from .models import PostReaction

class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = ['id', 'name', 'description', 'image']


class RecyclingCenterSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecyclingCenter
        fields = ['name', 'address', 'latitude', 'longitude']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username']



class PostReactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostReaction
        fields = ['post', 'user', 'reaction']
