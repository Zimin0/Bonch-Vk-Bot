import copy

from django.db import models
from django.contrib import admin
from django.contrib.admin import widgets

from .models import Match, Round, Tournament, TournamentEvent, \
    TournamentNotification, CsgoRound, CsgoMap, CsgoPeakStage


@admin.register(Tournament)
class TournamentAdminSite(admin.ModelAdmin):
    list_display = (
        "name",
        "game",
    )
    filter_horizontal = ("location_limit", "federal_districts_limit",
                         "registered_teams", "confirmed_teams", "referee")
    autocomplete_fields = ('winner',)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "winner":
            tournament_id = request.path.split('/')[4]
            if tournament_id.isdigit():
                tournament = Tournament.objects.filter(
                    id=tournament_id).first()
                kwargs["queryset"] = tournament.confirmed_teams
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class RoundInline(admin.TabularInline):
    model = Round
    readonly_fields = [
        "number",
        "match"
    ]
    exclude = ('date_created',)
    extra = 0
    can_delete = False

    # filter_horizontal = ("teams", )

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.choices:
            return self.formfield_for_choice_field(db_field, request, **kwargs)

        # ForeignKey or ManyToManyFields
        if isinstance(db_field, (models.ForeignKey, models.ManyToManyField)):
            if db_field.__class__ in self.formfield_overrides:
                kwargs = {**self.formfield_overrides[db_field.__class__],
                          **kwargs}

            # Get the correct formfield.
            if isinstance(db_field, models.ForeignKey):
                formfield = self.formfield_for_foreignkey(db_field, request,
                                                          **kwargs)
            elif isinstance(db_field, models.ManyToManyField):
                formfield = self.formfield_for_manytomany(db_field, request,
                                                          **kwargs)

            if formfield and db_field.name not in self.raw_id_fields:
                related_modeladmin = self.admin_site._registry.get(
                    db_field.remote_field.model)
                wrapper_kwargs = {}
                if related_modeladmin:
                    wrapper_kwargs.update(
                        can_add_related=related_modeladmin.has_add_permission(
                            request),
                        can_change_related=related_modeladmin.has_change_permission(
                            request),
                        can_delete_related=related_modeladmin.has_delete_permission(
                            request),
                        can_view_related=related_modeladmin.has_view_permission(
                            request),
                    )
                formfield.widget = widgets.RelatedFieldWidgetWrapper(
                    formfield.widget, db_field.remote_field, self.admin_site,
                    **wrapper_kwargs
                )
            if db_field.name == 'teams' and 'object_id' in kwargs:
                tournament_match = Match.objects.get(
                    id=request.resolver_match.kwargs['object_id']
                )
                formfield._queryset = \
                    tournament_match.tournament.confirmed_teams.filter()
            if db_field.name == 'winner' and 'object_id' in kwargs:
                tournament_match = Match.objects.get(
                    id=request.resolver_match.kwargs['object_id']
                )
                tournament_round = tournament_match.rounds_match.all()
                if tournament_round:
                    formfield._queryset = \
                        tournament_round[0].teams.filter()
                else:
                    formfield._queryset = Round.objects.filter(id=0)

            return formfield

        for klass in db_field.__class__.mro():
            if klass in self.formfield_overrides:
                kwargs = {**copy.deepcopy(self.formfield_overrides[klass]),
                          **kwargs}
                return db_field.formfield(**kwargs)

        return db_field.formfield(**kwargs)


class CsgoRoundInline(RoundInline):
    model = CsgoRound


@admin.register(Match)
class MatchAdminSite(admin.ModelAdmin):
    list_display = (
        "admin_name",
        "number",
        "referee",
        "teams",
        "winner_name",
        "type",
    )
    autocomplete_fields = ('referee',)
    inlines = [
        RoundInline, CsgoRoundInline
    ]
    list_filter = ('tournament', 'archived')
    search_fields = ('id',)
    exclude = ('archived',)

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return super().has_change_permission(request, obj=obj)
        if obj:
            return not obj.archived


@admin.register(TournamentNotification)
class TournamentNotificationAdminSite(admin.ModelAdmin):
    list_display = (
        "text",
        "users_status",
        "tournament",
        "users_status"
    )


@admin.register(Round)
class RoundAdminSite(admin.ModelAdmin):
    list_display = (
        "match",
        "team_names",
        "winner",
    )
    filter_horizontal = ("teams",)


@admin.register(CsgoRound)
class RoundAdminSite(admin.ModelAdmin):
    list_display = (
        "match",
        "team_names",
        "winner",
    )
    filter_horizontal = ("teams",)


@admin.register(CsgoMap)
class CsgoMapsAdminSite(admin.ModelAdmin):
    pass

@admin.register(CsgoPeakStage)
class CsgoPeakStageAdminSite(admin.ModelAdmin):
    list_display = (
        "match",
        "selected",
        "team",
        "map"
    )


@admin.register(TournamentEvent)
class TournamentEventAdminSite(admin.ModelAdmin):
    list_display = (
        "tournament",
        "type",
        "time_start",
        "time_end",
    )
    list_filter = ('tournament', 'time_start',)
