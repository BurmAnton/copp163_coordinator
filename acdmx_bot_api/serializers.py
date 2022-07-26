from email.policy import default
from enum import unique
from typing_extensions import Required
from requests import request
from rest_framework import serializers
from django.db.models import Max

from acdmx_bot_api.models import DiscordSever, EducationTrack, GuildRole, GuildMember, Task, Criterion, Assignment, Assessment

class DiscordServerSerializer(serializers.Serializer):
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
        slug_field='role_id',
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
    track = serializers.SlugRelatedField(
        many=False,
        read_only=False,
        slug_field='id',
        queryset=EducationTrack.objects.all(),
        required=False
        
    )

    def create(self, validated_data):
        return GuildRole.objects.create(**validated_data)
    
    def update(self, instance, validate_data):
        instance.role_id = validate_data.get('role_id', instance.role_id)
        instance.name = validate_data.get('name', instance.name)
        instance.server = validate_data.get('server', instance.server)
        instance.track = validate_data.get('track', instance.track)
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
        slug_field='role_id',
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


class CriterionSerializer(serializers.Serializer):
    name = serializers.CharField(required=False, allow_blank=True, max_length=200)

    def create(self, validated_data):
        name = validated_data.get('name')
        criteria = Criterion.objects.filter(name=name)
        if len(criteria) > 0:
            return criteria[0]
        return Criterion.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        
        instance.save()
        return instance


class TaskSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)

    track = serializers.SlugRelatedField(
        many=False,
        read_only=False,
        slug_field='id',
        queryset=EducationTrack.objects.all()
    )
    number = serializers.IntegerField(required=False)
    description = serializers.CharField(required=True, allow_blank=False)
    days_required = serializers.IntegerField(required=True)
    criteria = serializers.SlugRelatedField(
        many=True,
        read_only=False,
        slug_field='name',
        queryset=Criterion.objects.all()
    )

    def create(self, validated_data):
        track = validated_data.get('track')
        tracks = Task.objects.filter(track=track).aggregate(Max('number'))
        if tracks['number__max'] is not None:
            number = tracks['number__max'] + 1
        else:
            number = 1
        description = validated_data.get('description')
        days_required = validated_data.get('days_required')
        task = Task.objects.create(
            track=track,
            number=number,
            description=description,
            days_required=days_required
        )
        criteria = validated_data.get('criteria')
        task.criteria.add(*criteria)
        task.save()
        return task
    
    def update(self, instance, validate_data):
        instance.days_required = validate_data.get('days_required', instance.days_required)
        instance.description = validate_data.get('description', instance.description)
        instance.number = validate_data.get('number', instance.number)
        instance.track = validate_data.get('track', instance.track)
        instance.criteria = validate_data.get('criteria', instance.track)
        
        instance.save()
        return instance


class AssignmentSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    task = serializers.SlugRelatedField(
        many=False,
        read_only=False,
        slug_field='id',
        queryset=Task.objects.all(),
        required=False
    )

    executor = serializers.SlugRelatedField(
        many=False,
        read_only=False,
        slug_field='user_id',
        queryset=GuildMember.objects.all(),
        required=False
    )
    start_date = serializers.DateTimeField(required=False)
    deadline = serializers.DateTimeField(required=False)
    delivery_day = serializers.DateTimeField(required=False, allow_null=True)
    is_done = serializers.BooleanField(required=False)
    is_delivered = serializers.BooleanField(required=False)
    message_id = serializers.IntegerField(required=False, allow_null=True)
    assignment_text = serializers.CharField(required=False, allow_blank=True, max_length=10000)
    teacher_comment = serializers.CharField(required=False, allow_blank=True, max_length=10000)

    def create(self, validated_data):
        return Assignment.objects.create(**validated_data)
    
    def update(self, instance, validate_data):
        instance.task = validate_data.get('task', instance.task)
        instance.executor = validate_data.get('executor', instance.executor)
        instance.start_date = validate_data.get('start_date', instance.start_date)
        instance.deadline = validate_data.get('deadline', instance.deadline)
        instance.delivery_day = validate_data.get('delivery_day', instance.delivery_day)
        instance.is_done = validate_data.get('is_done', instance.is_done)
        instance.is_delivered = validate_data.get('is_delivered', instance.is_delivered)
        instance.message_id = validate_data.get('message_id', instance.message_id)
        instance.assignment_text = validate_data.get('assignment_text', instance.assignment_text)
        instance.teacher_comment = validate_data.get('teacher_comment', instance.teacher_comment)

        instance.save()
        return instance


class AssessmentSerializer(serializers.Serializer):
    assignment = serializers.SlugRelatedField(
        many=False,
        read_only=False,
        slug_field='id',
        queryset=Assignment.objects.all()
    )
    criterion = serializers.SlugRelatedField(
        many=False,
        read_only=False,
        slug_field='name',
        queryset=Criterion.objects.all()
    )
    is_met = serializers.BooleanField(required=False)

    def create(self, validated_data):
        return Assessment.objects.create(**validated_data)
    
    def update(self, instance, validate_data):
        instance.assignment = validate_data.get('task', instance.assignment)
        instance.criterion = validate_data.get('executor', instance.criterion)
        instance.is_met = validate_data.get('is_met', instance.is_met)
        
        instance.save()
        return instance