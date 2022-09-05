from django.contrib import admin

from acdmx_bot_api.models import GuildMember, GuildRole, EducationTrack, DiscordSever, Assessment, Assignment, Task, Criterion

from easy_select2 import select2_modelform
# Register your models here.
#@admin.register(GuildMember)
class GuildMemberAdmin(admin.ModelAdmin):
    pass

#@admin.register(GuildRole)
class GuildRoleAdmin(admin.ModelAdmin):
    pass

#@admin.register(EducationTrack)
class EducationTrackAdmin(admin.ModelAdmin):
    pass

#@admin.register(DiscordSever)
class DiscordSeverAdmin(admin.ModelAdmin):
    pass

#@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    pass

AssessmentForm = select2_modelform(Assessment, attrs={'width': '400px'})

class AssessmentInLine(admin.TabularInline):
    model = Assessment
    form = AssessmentForm
    fields = ['criterion', 'is_met']
    def get_extra(self, request, obj=None, **kwargs):
        extra = 0
        if obj:
            return extra
        return extra

#@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    inlines = [AssessmentInLine,]

#@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    pass

#@admin.register(Criterion)
class CriterionAdmin(admin.ModelAdmin):
    pass