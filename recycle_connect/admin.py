from django.contrib import admin
from django.utils.html import format_html
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin

from .models import (
    Material, RecyclingCenter, RecyclingProof,
    VolunteerOpportunity, VolunteerSignup,
    ForumPost, Comment, Poll, PollOption, Vote, Suggestion
)

# Material Admin
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('name', 'image_tag')

    def image_tag(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="60" height="60" />', obj.image.url)
        return "-"
    image_tag.short_description = 'Image'

admin.site.register(Material, MaterialAdmin)
admin.site.register(RecyclingCenter)


# Recycling Proof Admin
@admin.register(RecyclingProof)
class RecyclingProofAdmin(admin.ModelAdmin):
    list_display = ['id', 'get_user', 'verified', 'image_tag']

    def get_user(self, obj):
        return obj.challenge.user
    get_user.short_description = 'User'

    def image_tag(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 60px; height: auto;" />', obj.image.url)
        return "No Image"
    image_tag.short_description = 'Proof Image'


# Volunteer Opportunity Admin
@admin.register(VolunteerOpportunity)
class VolunteerOpportunityAdmin(admin.ModelAdmin):
    list_display = ('title', 'location', 'date', 'max_volunteers')
    list_filter = ('date', 'location')
    search_fields = ('title', 'location', 'description')
    date_hierarchy = 'date'


# Volunteer Signup Admin
@admin.register(VolunteerSignup)
class VolunteerSignupAdmin(admin.ModelAdmin):
    list_display = ('user', 'opportunity', 'hours_completed', 'certified')
    list_filter = ('certified', 'opportunity')
    search_fields = ('user__username', 'opportunity__title')
    list_editable = ('hours_completed', 'certified')


# Custom User Admin
class CustomUserAdmin(DefaultUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'date_joined', 'last_login')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('date_joined', 'last_login')

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


# Forum Post Admin
@admin.register(ForumPost)
class ForumPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'is_approved', 'created_at')
    list_filter = ('is_approved',)
    actions = ['approve_selected']

    def approve_selected(self, request, queryset):
        queryset.update(is_approved=True)
    approve_selected.short_description = "Approve selected forum posts"


# Comment Admin
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'user', 'created_at')
    search_fields = ('post__title', 'user__username', 'content')
    list_filter = ('created_at',)


# PollOption inline for PollAdmin
class PollOptionInline(admin.TabularInline):
    model = PollOption
    extra = 3


# Poll Admin with inline PollOption editing
@admin.register(Poll)
class PollAdmin(admin.ModelAdmin):
    list_display = ('question', 'created_at')
    inlines = [PollOptionInline]


# PollOption Admin
@admin.register(PollOption)
class PollOptionAdmin(admin.ModelAdmin):
    list_display = ('poll', 'text')


# Vote Admin
@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ('option', 'user')


# Suggestion Admin
@admin.register(Suggestion)
class SuggestionAdmin(admin.ModelAdmin):
    list_display = ('post', 'user', 'text')
    filter_horizontal = ('votes',)

from django.contrib import admin
from .models import Event, EventRegistration

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'location')
    list_filter = ('date',)
    search_fields = ('title', 'location')

@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = ('user', 'event', 'name', 'email', 'registered_at')
    list_filter = ('event', 'registered_at')
    search_fields = ('user__username', 'name', 'email')
    ordering = ('-registered_at',)
