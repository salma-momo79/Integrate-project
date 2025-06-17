from django.contrib import admin
from .models import Material, RecyclingCenter
from .models import RecyclingProof
from django.utils.html import format_html

admin.site.register(Material)
admin.site.register(RecyclingCenter)


@admin.register(RecyclingProof)
class RecyclingProofAdmin(admin.ModelAdmin):
    list_display = ['id', 'get_user', 'verified', 'image_tag']

    def get_user(self, obj):
        return obj.challenge.user  # Assuming UserChallenge has a 'user' field
    get_user.short_description = 'User'

    def image_tag(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 60px; height: auto;" />', obj.image.url)
        return "No Image"
    image_tag.short_description = 'Proof Image'
