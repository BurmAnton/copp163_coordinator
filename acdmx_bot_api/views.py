from django.shortcuts import render

from rest_framework import viewsets
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from acdmx_bot_api.serializers import DiscordSeverSerializer, EducationTrackSerializer, GuildMemberSerializer
from acdmx_bot_api.models import DiscordSever, EducationTrack, GuildMember

class DiscordSeverViewSet(viewsets.ModelViewSet):
   queryset = DiscordSever.objects.all()
   serializer_class = DiscordSeverSerializer

@api_view(['GET', 'POST'])
def servers_list(request, format=None):
    if request.method == 'GET':
        snippets = DiscordSever.objects.all()
        serializer = DiscordSeverSerializer(snippets, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = DiscordSeverSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def server_details(request, pk, format=None):
    try:
        server = DiscordSever.objects.get(pk=pk)
    except DiscordSever.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = DiscordSeverSerializer(server)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = DiscordSeverSerializer(server, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        server.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class EducationTrackViewSet(viewsets.ModelViewSet):
   queryset = EducationTrack.objects.all()
   serializer_class = EducationTrackSerializer

@api_view(['GET'])
def tracks_list(request, format=None):
    if request.method == 'GET':
        snippets = EducationTrack.objects.all()
        serializer = EducationTrackSerializer(snippets, many=True)
        return Response(serializer.data)

@api_view(['GET'])
def track_details(request, pk, format=None):
    try:
        server = EducationTrack.objects.get(pk=pk)
    except EducationTrack.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = EducationTrackSerializer(server)
        return Response(serializer.data)


class GuildMemberViewSet(viewsets.ModelViewSet):
   queryset = GuildMember.objects.all()
   serializer_class = GuildMemberSerializer
