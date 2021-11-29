from django.test import TestCase, Client
from datetime import timedelta, date


from citizens.models import Citizen, School, SchoolClass
from vocational_guidance.models import BiletDistribution, VocGuidTest, TimeSlot
from education_centers.models import EducationCenter
from users.models import User

# Create your tests here.
class VocationGuidanceTestCase(TestCase):

    def setUp(self):
        education_center = EducationCenter.objects.create(name="TestEducationCenter")
        test = VocGuidTest.objects.create(
            name="test",
            education_center=education_center,
            thematic_env="HLTH"
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

        school = School.objects.create(
            name = "Тестовая школа №1",
        )
        quota = BiletDistribution.objects.create(
            school=school,
            quota=0
        )
        school_class = SchoolClass.objects.create(
            school=school,
            grade_number=6,
            grade_letter="А"
        )
        teacher = User.objects.create(
            email='teacher@user.com',
        )
        teacher.set_password('password')
        teacher.coordinated_schools.add(school)
        teacher.save()

        user = User.objects.create(email='student@user.com')
        user.set_password('password')
        user.save()
        student = Citizen.objects.create(
            email='student@user.com',
            birthday = '1998-11-25',
            school=school,
            school_class=school_class
        )

    def test_login(self):
        c = Client()
        response = c.get("/bilet/login/")
        
        self.assertTrue(response.status_code, 200)
    
    def test_registration(self):
        c = Client()

        response = c.get("/bilet/registration/")
        self.assertTrue(response.status_code, 200)

        response = c.get("/bilet/registration/child/")
        self.assertTrue(response.status_code, 200)

        response = c.get("/bilet/registration/parent/")
        self.assertTrue(response.status_code, 200)
    
    def test_student_profile(self):
        c = Client()
        response = c.get("/bilet/student/profile/1/")
        self.assertEqual(response.status_code, 302)

        user = User.objects.get(email='student@user.com')
        c.force_login(user, backend=None)

        student = Citizen.objects.get(email='student@user.com')
        response = c.get(f"/bilet/student/profile/{student.id}/", follow=True)
        self.assertEqual(response.status_code, 200)
    
    def test_school_profile(self):
        c = Client()
        school = School.objects.first()
        response = c.get(f"/bilet/school/profile/{school.id}/")
        self.assertEqual(response.status_code, 302)
        
        teacher = User.objects.get(coordinated_schools=school)
        c.force_login(teacher, backend=None)
        response = c.get(f"/bilet/school/profile/{school.id}/", follow=True)
        self.assertEqual(response.status_code, 200)

    def test_tests_list(self):
        c = Client()

        response = c.get("/bilet/tests/all/")
        test = VocGuidTest.objects.get(name="test")
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["tests"]["Здоровая среда"]), 1)
        self.assertEqual(response.context["tests"]["Здоровая среда"][0], test)

