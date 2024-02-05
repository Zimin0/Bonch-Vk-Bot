from django.contrib import admin

from .models import Team, TeamInvites


@admin.register(Team)
class TeamAdminSite(admin.ModelAdmin):
    readonly_fields = ('allow_chang', 'user_team_info', 'study_team')
    list_display = (
        "name",
        "captain",
        "game",
    )
    list_filter = ('game', 'archived',)
    filter_horizontal = ("players",)
    search_fields = ('name',)
    fieldsets = (
        ('Стандартная информация', {
            'fields': ('name', 'game', 'players_count')
        }),
        ('Состав', {
            'fields': ('captain', 'players',)
        }),
        ('Дополнительная информация', {
            'fields': ('allow_chang', 'user_team_info',
                       'study_team', 'archived')
        })
    )


@admin.register(TeamInvites)
class TeamAdminSite(admin.ModelAdmin):
    list_display = (
        "team",
        "user",
        "date",
        "type"
    )
    autocomplete_fields = ("team", "user",)
