from django.test import TestCase, Client
from datetime import timedelta, date

from vocational_guidance.models import VocGuidTest, TimeSlot
from education_centers.models import EducationCenter

# Create your tests here.
class VocationGuidanceTestCase(TestCase):

    def setUp(self):
        education_center = EducationCenter.objects.create(name="TestEducationCenter")
        test = VocGuidTest.objects.create(
            name="test",
            education_center=education_center,
        )
        slot1 = TimeSlot.objects.create(
            date=date.today() + timedelta(days=7),
            slot="MRN",
            test=test
        )
        slot2 = TimeSlot.objects.create(
            date=date.today(),
            slot="EVN",
            test=test
        )
        slot3 = TimeSlot.objects.create(
            date=date.today() + timedelta(days=8),
            slot="MID",
            test=test
        )

    def test_tests_list(self):
        c = Client()
        response = c.get("/flights/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["tests"].count(), 1)
    
