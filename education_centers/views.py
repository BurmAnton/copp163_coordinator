from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render

from .models import EducationCenter, Group
from .contracts import create_document

# Create your views here.
def index(request):
    center = EducationCenter.objects.filter(contact_person=request.user)
    if len(center) != 0:
        center = center[0].name
        return JsonResponse(center, safe=False)
    return JsonResponse(False, safe=False)


def ed_center_groups(request, ed_center):
    ed_center = get_object_or_404(EducationCenter, id=ed_center)
    groups = Group.objects.filter(
        workshop__education_center=ed_center
    )
    create_document(ed_center, groups)
    return JsonResponse(False, safe=False)


