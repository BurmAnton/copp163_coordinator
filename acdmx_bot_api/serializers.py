from rest_framework import serializers

from acdmx_bot_api.models import DiscordSever, EducationTrack, GuildMember 

class DiscordSeverSerializer(serializers.Serializer):
    server_id = serializers.CharField(required=True, allow_blank=False, max_length=200)
    name = serializers.CharField(required=False, allow_blank=True, max_length=200)

    def create(self, validated_data):
        return DiscordSever.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        instance.server_id = validated_data.get('server_id', instance.server_id)
        instance.name = validated_data.get('name', instance.name)
        instance.save()
        return instance

class EducationTrackSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(required=True, allow_blank=False, max_length=200)
    server = serializers.StringRelatedField(many=False)


class GuildMemberSerializer(serializers.ModelSerializer):
   class Meta:
       model = GuildMember
       fields = (
           'user_id', 
           'education_track', 
           'role', 
           'first_name', 
           'middle_name', 
           'last_name', 
           'email'
        )