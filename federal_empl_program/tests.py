from django.test import TestCase, Client
from django.contrib import auth

from datetime import date
from education_centers.models import Competence, EducationCenter, EducationProgram

from users.models import User
from .models import EdCenterQuotaRequest, EducationCenterProjectYear, ProgramQuotaRequest, ProjectYear, QuotaRequest

# Models tests
class ProjectYearTest(TestCase):

    def create_project_year(self, year):
        return ProjectYear.objects.create(year=year)
    
    def test_project_year_creation(self):
        year = date.today().year
        p = self.create_project_year(year)
        self.assertTrue(isinstance(p, ProjectYear))
        self.assertEqual(p.__str__(), str(year))


class EducationCenterProjectYearTest(TestCase):

    def create_center_project_year(self, year, name):
        project_year = ProjectYear.objects.create(year=year)
        ed_center = EducationCenter.objects.create(name=name)
        return EducationCenterProjectYear.objects.create(
            ed_center=ed_center,
            project_year=project_year
        )
    
    def test_center_project_year_creation(self):
        year = date.today().year
        ed_center = 'ГБПОУ "Образовательный центр с. Камышла"'
        p = self.create_center_project_year(year, ed_center)
        self.assertTrue(isinstance(p, EducationCenterProjectYear))
        self.assertEqual(p.__str__(), f'{ed_center} ({year} г.)')


class QuotaRequestTest(TestCase):

    def create_quota_request(self, year, request_number):
        project_year = ProjectYear.objects.create(year=year)
        return QuotaRequest.objects.create(
            project_year=project_year, request_number=request_number)
    
    def test_quota_request_creation(self):
        year = date.today().year
        q = self.create_quota_request(year, 1)
        self.assertTrue(isinstance(q, QuotaRequest))
        self.assertEqual(q.__str__(), 'Запрос №1 (заполнение)')


class EdCenterQuotaRequestTest(TestCase):

    def create_ed_quota_request(self, year, request_number, name, short_name):
        project_year = ProjectYear.objects.create(year=year)
        ed_center = EducationCenter.objects.create(
            name=name, short_name=short_name)
        request = QuotaRequest.objects.create(
            project_year=project_year, request_number=request_number)
        ed_center_year = EducationCenterProjectYear.objects.create(
            ed_center=ed_center,
            project_year=project_year
        )
        return EdCenterQuotaRequest.objects.create(
            ed_center_year=ed_center_year, request_number=request_number, 
            request=request)
    
    def test_ed_quota_request_creation(self):
        year = date.today().year
        name = 'ГБПОУ "Образовательный центр с. Камышла"'
        short_name = 'ГБПОУ "ОЦ с. Камышла"'
        q = self.create_ed_quota_request(year, 1, name, short_name)
        self.assertTrue(isinstance(q, EdCenterQuotaRequest))
        self.assertEqual(q.__str__(), f'Запрос {short_name} №1 (заполнение)')


class ProgramQuotaRequestTest(TestCase):

    def create_pr_quota_request(self, program):
        year = date.today().year
        name = 'ГБПОУ "Образовательный центр с. Камышла"'
        short_name = 'ГБПОУ "ОЦ с. Камышла"'
        project_year = ProjectYear.objects.create(year=year)
        ed_center = EducationCenter.objects.create(
            name=name, short_name=short_name)
        ed_center_year = EducationCenterProjectYear.objects.create(
            ed_center=ed_center,
            project_year=project_year
        )
        request = QuotaRequest.objects.create(
            project_year=project_year, request_number=1)
        ed_center_request = EdCenterQuotaRequest.objects.create(
            ed_center_year=ed_center_year, request_number=1, request=request)       
        return ProgramQuotaRequest.objects.create(
            ed_center_request=ed_center_request, 
            program=program,
        )
    
    def test_pr_quota_request_creation(self):
        year = date.today().year
        program_name = 'Сварщик'
        program_type = 'DPOPK'
        competence = Competence.objects.create(title='Сварщик')
        program = EducationProgram.objects.create(
        program_name=program_name, competence=competence, duration=72,
            program_type=program_type)
        p = self.create_pr_quota_request(program)
        self.assertTrue(isinstance(p, ProgramQuotaRequest))
        self.assertEqual(
            p.__str__(), 
            f'{program.program_name} ({p.ed_center_request.ed_center_year})'
        )


# Views tests
class IndexTest(TestCase):
    def setUp(self):
        # Every test needs a client.
        self.client = Client()
    
    def test_view(self):
        # Issue a GET request.
        response = self.client.get("")

        # Check that the response is 200 OK.
        self.assertEqual(response.status_code, 302)


class ImportExpressTest(TestCase):
    def setUp(self):
        User.objects.create_user(email='testuser@test.com', password='12345')
        self.client = Client()
        
    def test_view(self):
        # Issue a GET request.
        self.client.login(username='testuser@test.com', password='12345') 
        response = self.client.get("/import/express/")

        # Check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)


class LogoutTest(TestCase):
    def setUp(self):
        User.objects.create_user(email='testuser@test.com', password='12345')
        self.client = Client()
        
    def test_view(self):
        self.client.login(username='testuser@test.com', password='12345')
        
        # Issue a GET request.
        response = self.client.get("/logout/")
        self.assertRedirects(response, '/login/', 
                             status_code=302, target_status_code=200)
        user = auth.get_user(self.client)
        self.assertFalse(user.is_authenticated)
        

