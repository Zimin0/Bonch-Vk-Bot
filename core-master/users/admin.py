from django.contrib import admin

from .models import (UserEducation, EducationalType, GameAccount,
                     Location, Notification, Platform, User, UserNotification,
                     UserRestriction, UserRole, UserVerificationRequest,
                     FederalDistricts, Institute)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'first_name', 'last_name', 'date_next_verification', 'verified'
    )
    list_filter = ('date_next_verification',)
    filter_horizontal = ("game_subscription",)
    search_fields = ('first_name', 'last_name', 'vk_id',)
    autocomplete_fields = ('educational_institution',)


@admin.register(UserEducation)
class UserEducationAdmin(admin.ModelAdmin):
    list_display = (
        'location', 'type', 'institute',
    )
    search_fields = ('location__name', 'type__name', 'institute__name',)
    list_filter = ('location', 'type', 'institute',)
    autocomplete_fields = ('institute', 'location',)


@admin.register(Location)
class InstituteAdmin(admin.ModelAdmin):
    search_fields = ('name',)


@admin.register(Institute)
class InstituteAdmin(admin.ModelAdmin):
    search_fields = ('name',)


admin.site.register(EducationalType)
admin.site.register(UserRestriction)
admin.site.register(UserRole)
admin.site.register(Platform)


@admin.register(GameAccount)
class GameAccountAdmin(admin.ModelAdmin):
    list_display = (
        'nick_name', 'user', 'platform'
    )
    list_filter = ('platform', )
    search_fields = ('user__first_name', 'user__last_name', 'nick_name', )


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        'text', 'type', 'system'
    )
    # exclude = ('endpoints', 'attachments', 'system')
    list_filter = ('system',)

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return super().has_change_permission(request, obj=obj)
        if obj:
            return not obj.system


@admin.register(UserNotification)
class UserNotificationAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'status', 'delivery_date', 'notification',
    )
    search_fields = ('id',)


class LocationAdmin(admin.StackedInline):
    model = Location


class FederalDistrictsAdmin(admin.ModelAdmin):
    model = FederalDistricts
    inlines = [LocationAdmin]


admin.site.register(FederalDistricts, FederalDistrictsAdmin)


@admin.register(UserVerificationRequest)
class UserVerificationRequestAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'archived'
    )
    list_filter = ('archived',)
