from django.contrib import admin

from acdmx_bot_api.models import GuildMember, EducationTrack, DiscordSever

# Register your models here.
@admin.register(GuildMember)
class GuildMemberAdmin(admin.ModelAdmin):
    pass

@admin.register(EducationTrack)
class EducationTrackAdmin(admin.ModelAdmin):
    pass

@admin.register(DiscordSever)
class DiscordSeverAdmin(admin.ModelAdmin):
    pass