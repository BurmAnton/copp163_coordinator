from django.shortcuts import render

from rest_framework import viewsets
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from acdmx_bot_api.serializers import DiscordServerSerializer, EducationTrackSerializer, GuildRoleSerializer, GuildMemberSerializer, TaskSerializer, CriterionSerializer, AssignmentSerializer, AssessmentSerializer
from acdmx_bot_api.models import DiscordSever, EducationTrack, GuildMember, GuildRole, Task, Criterion, Assignment, Assessment


@api_view(['GET', 'POST'])
def servers_list(request, format=None):
    if request.method == 'GET':
        servers = DiscordSever.objects.all()
        serializer = DiscordServerSerializer(servers, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = DiscordServerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def server_details(request, server_id, format=None):
    try:
        server = DiscordSever.objects.get(server_id=server_id)
    except DiscordSever.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = DiscordServerSerializer(server)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = DiscordServerSerializer(server, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        server.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
def tracks_list(request, format=None):
    if request.method == 'GET':
        snippets = EducationTrack.objects.all()
        serializer = EducationTrackSerializer(snippets, many=True)
        return Response(serializer.data)

@api_view(['GET'])
def track_details(request, track_id, format=None):
    try:
        track = EducationTrack.objects.get(id=track_id)
    except EducationTrack.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = EducationTrackSerializer(track)
        return Response(serializer.data)

@api_view(['GET', 'POST'])
def roles_list(request, format=None):
    if request.method == 'GET':
        roles = GuildRole.objects.all()
        user_id = request.query_params.get('user_id')
        if user_id is not None:
            try:
                user = GuildMember.objects.get(user_id=user_id)
                roles = roles.filter(name=user.server_role)
            except:
                pass
        serializer = GuildRoleSerializer(roles, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = GuildRoleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def role_details(request, role_id, format=None):
    try:
        role = GuildRole.objects.get(role_id=role_id)
    except GuildRole.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = GuildRoleSerializer(role)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = GuildRoleSerializer(role, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        role.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET', 'POST'])
def members_list(request, format=None):
    if request.method == 'GET':
        members = GuildMember.objects.all()
        server_role = request.query_params.get('server_role')
        if server_role is not None:
            members = members.filter(server_role__role_id=server_role)
        member_status = request.query_params.get('status')
        if member_status is not None:
            members = members.filter(status=member_status)
        serializer = GuildMemberSerializer(members, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = GuildMemberSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def member_details(request, user_id, format=None):
    try:
        member = GuildMember.objects.get(user_id=user_id)
    except GuildMember.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = GuildMemberSerializer(member)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = GuildMemberSerializer(member, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        member.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET', 'POST'])
def task_list(request, format=None):
    if request.method == 'GET':
        tasks = Task.objects.all()
        track = request.query_params.get('name')
        if track is not None:
            tasks = tasks.filter(track__id=track)
        number = request.query_params.get('number')
        if number is not None:
            tasks = tasks.filter(number=number)
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def task_details(request, task_id, format=None):
    try:
        task = Task.objects.get(id=task_id)
    except Task.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = TaskSerializer(task)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = TaskSerializer(task, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET', 'POST'])
def criteria_list(request, format=None):
    if request.method == 'GET':
        criteria = Criterion.objects.all()
        serializer = CriterionSerializer(criteria, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = CriterionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'POST'])
def assignments_list(request, format=None):
    if request.method == 'GET':
        assignments = Assignment.objects.all()
        task = request.query_params.get('task')
        if task is not None:
            assignments = assignments.filter(task=task)
        executor = request.query_params.get('executor')
        if executor is not None:
            assignments = assignments.filter(executor__user_id=executor)
        is_done = request.query_params.get('is_done')
        if is_done is not None:
            assignments = assignments.filter(is_done=is_done)
        is_delivered = request.query_params.get('is_delivered')
        if is_delivered is not None:
            assignments = assignments.filter(is_delivered=is_delivered)
        is_started = request.query_params.get('is_started')
        if is_started is not None:
            assignments = assignments.exclude(start_date=None)
        serializer = AssignmentSerializer(assignments, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = AssignmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def assignment_details(request, assignment_id, format=None):
    try:
        member = Assignment.objects.get(id=assignment_id)
    except Assignment.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = AssignmentSerializer(member)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = AssignmentSerializer(member, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        member.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET', 'POST'])
def assessment_list(request, format=None):
    if request.method == 'GET':
        members = Assessment.objects.all()
        serializer = AssessmentSerializer(members, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = AssessmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)