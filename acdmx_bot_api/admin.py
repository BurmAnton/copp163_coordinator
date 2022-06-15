from django.contrib import admin

from acdmx_bot_api.models import GuildMember, GuildRole, EducationTrack, DiscordSever, Assessment, Assignment, Task, Criterion

# Register your models here.
@admin.register(GuildMember)
class GuildMemberAdmin(admin.ModelAdmin):
    pass

@admin.register(GuildRole)
class GuildRoleAdmin(admin.ModelAdmin):
    pass

@admin.register(EducationTrack)
class EducationTrackAdmin(admin.ModelAdmin):
    pass

@admin.register(DiscordSever)
class DiscordSeverAdmin(admin.ModelAdmin):
    pass

@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    pass

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    pass

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    pass

@admin.register(Criterion)
class CriterionAdmin(admin.ModelAdmin):
    pass