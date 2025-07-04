from django.contrib import admin
from .models import Material, RecyclingCenter, RecyclingProof, VolunteerOpportunity, VolunteerSignup
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


@admin.register(VolunteerOpportunity)
class VolunteerOpportunityAdmin(admin.ModelAdmin):
    list_display = ('title', 'location', 'date', 'max_volunteers')
    list_filter = ('date', 'location')
    search_fields = ('title', 'location', 'description')
    date_hierarchy = 'date'


@admin.register(VolunteerSignup)
class VolunteerSignupAdmin(admin.ModelAdmin):
    list_display = ('user', 'opportunity', 'hours_completed', 'certified')
    list_filter = ('certified', 'opportunity')
    search_fields = ('user__username', 'opportunity__title')
    list_editable = ('hours_completed', 'certified')
