from email.policy import default
from requests import request
from rest_framework import serializers
from django.db.models import Max

from acdmx_bot_api.models import DiscordSever, EducationTrack, GuildRole, GuildMember, Task, Criterion

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
    track_role = serializers.SlugRelatedField(
        many=False,
        read_only=False,
        slug_field='name',
        queryset=GuildRole.objects.all()
    )


class GuildRoleSerializer(serializers.Serializer):
    role_id = serializers.CharField(required=True, allow_blank=False, max_length=200)
    name = serializers.CharField(required=True, allow_blank=False, max_length=200)
    server = serializers.SlugRelatedField(
        many=False,
        read_only=False,
        slug_field='server_id',
        queryset=DiscordSever.objects.all()
    )

    def create(self, validated_data):
        return GuildRole.objects.create(**validated_data)
    
    def update(self, instance, validate_data):
        instance.role_id = validate_data.get('role_id', instance.role_id)
        instance.name = validate_data.get('name', instance.name)
        instance.server = validate_data.get('server', instance.server)
        
        instance.save()
        return instance


class GuildMemberSerializer(serializers.Serializer):
    user_id = serializers.CharField(required=True, allow_blank=False, max_length=200)
    
    first_name = serializers.CharField(required=True, allow_blank=False, max_length=50)
    middle_name = serializers.CharField(required=False, allow_blank=True, max_length=50)
    last_name = serializers.CharField(required=True, allow_blank=False, max_length=50)
    email =serializers.EmailField(required=True, allow_blank=False)
    
    status =serializers.CharField(allow_blank=True, max_length=3, default='ST')
    server = serializers.SlugRelatedField(
        many=False,
        read_only=False,
        slug_field='server_id',
        queryset=DiscordSever.objects.all()
    )
    server_role = serializers.SlugRelatedField(
        many=False,
        read_only=False,
        slug_field='name',
        queryset=GuildRole.objects.all()
    )
    
    def create(self, validated_data):
        return GuildMember.objects.create(**validated_data)
    
    def update(self, instance, validate_data):
        instance.user_id = validate_data.get('user_id', instance.user_id)
        instance.first_name = validate_data.get('first_name', instance.first_name)
        instance.middle_name = validate_data.get('middle_name', instance.middle_name)
        instance.last_name = validate_data.get('last_name', instance.last_name)
        instance.email = validate_data.get('email', instance.email)
        instance.status = validate_data.get('status', instance.status)
        instance.server = validate_data.get('status', instance.server)
        instance.server_role = validate_data.get('server_role', instance.server_roles)
        
        instance.save()
        return instance


class TaskSerializer(serializers.Serializer):
    track = serializers.SlugRelatedField(
        many=False,
        read_only=False,
        slug_field='name',
        queryset=EducationTrack.objects.all()
    )
    number = serializers.IntegerField(required=False)
    description = serializers.CharField(required=True, allow_blank=False)
    days_required = serializers.IntegerField(required=True)

    def create(self, validated_data):
        tracks = Task.objects.filter().aggregate(Max('number'))
        if tracks['number__max'] is not None:
            number = tracks['number__max'] + 1
        else:
            number = 1
        return Task.objects.create(**validated_data, number=number)
    
    def update(self, instance, validate_data):
        instance.days_required = validate_data.get('days_required', instance.days_required)
        instance.description = validate_data.get('description', instance.description)
        instance.number = validate_data.get('number', instance.number)
        instance.track = validate_data.get('track', instance.track)
        
        instance.save()
        return instance