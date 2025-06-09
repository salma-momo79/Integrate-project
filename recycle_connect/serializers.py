from rest_framework import serializers
from .models import Material, RecyclingCenter

class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = ['name', 'description']

class RecyclingCenterSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecyclingCenter
        fields = ['name', 'address', 'latitude', 'longitude']
