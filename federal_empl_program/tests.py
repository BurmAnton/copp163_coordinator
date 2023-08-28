import datetime
import math
from django.test import TestCase, Client
from django.contrib import auth

from datetime import date
from citizens.models import Citizen
from education_centers.models import EducationProgram, EducationCenter,\
                                     Competence, Employee
from users.models import User
from .models import EdCenterQuotaRequest, Indicator, CitizenApplication,\
                    ProgramQuotaRequest, EducationCenterProjectYear,\
                    EdCenterIndicator, ProjectPosition, Grant, Application,\
                    EdCenterEmployeePosition, QuotaRequest, ProjectYear,\
                    CitizenCategory

# Models tests
class FedEmplModelsTest(TestCase):
    def setUp(self):
        self.year = date.today().year
        self.req_num = 1
        self.name ='ГБПОУ "Образовательный центр с. Камышла"'
        self.s_name = 'ГБПОУ "ОЦ с. Камышла"'
        self.pr_name = 'Сварщик'
        self.pr_type = 'DPOPK'
        self.i_name = 'Тестовый показатель'
        self.p_name = 'Тестовая позиция'
        self.c_name = 'Тестовая категория'
        self.g_name = 'Тестовый грант'
        
        self.project_year = ProjectYear.objects.create(year=self.year)
        self.ed_center = EducationCenter.objects.create(
            name=self.name, short_name=self.s_name)
        self.center_project_year = EducationCenterProjectYear.objects.create(
            ed_center=self.ed_center,
            project_year=self.project_year
        )
        self.quota_req = QuotaRequest.objects.create(
            project_year=self.project_year, request_number=self.req_num)
        self.ed_quota_req = EdCenterQuotaRequest.objects.create(
            ed_center_year=self.center_project_year,
            request_number=self.req_num, 
            request=self.quota_req
        )
        competence = Competence.objects.create(title='Сварщик')
        self.program = EducationProgram.objects.create(
        program_name=self.pr_name, competence=competence, duration=72,
            program_type=self.pr_type)
        self.pr_quota_req = ProgramQuotaRequest.objects.create(
            ed_center_request=self.ed_quota_req, 
            program=self.program,
        )
        self.indicator = Indicator.objects.create(
            project_year=self.project_year, name=self.i_name
        )
        self.e_indicator = EdCenterIndicator.objects.create(
            indicator=self.indicator, ed_center=self.ed_center
        )
        self.position = ProjectPosition.objects.create(
            project_year=self.project_year, position=self.p_name
        )
        self.employee = Employee.objects.create(
            organization=self.ed_center,first_name='t', last_name='t',
            position='t', first_name_r='t',last_name_r='t', position_r='t',
            phone='t', email='test@t.com',
        )
        self.ed_position = EdCenterEmployeePosition.objects.create(
            employee=self.employee, ed_center=self.ed_center,
            position=self.position
        )
        self.category = CitizenCategory.objects.create(
            short_name=self.c_name, project_year=self.project_year
        )
        self.grant = Grant.objects.create(
            project_year=self.project_year, grant_name=self.g_name
        )
        self.citizen = Citizen.objects.create()
        self.appl = Application.objects.create(
            project_year=self.project_year, applicant=self.citizen,
            education_program=self.program
        )
        self.c_appl = CitizenApplication.objects.create(
            first_name='first_name', last_name='last_name'
        )

    def test_project_year(self):
        self.assertTrue(isinstance(self.project_year, ProjectYear))
        self.assertEqual(self.project_year.__str__(), str(self.year))

    def test_center_project_year(self):
        c = self.center_project_year
        self.assertTrue(isinstance(c, EducationCenterProjectYear))
        self.assertEqual(c.__str__(),f'{self.ed_center} ({str(self.year)} г.)')
    
    def test_quota_request(self):
        q = self.quota_req
        self.assertTrue(isinstance(q, QuotaRequest))
        self.assertEqual(q.__str__(), f'Запрос №{self.req_num} (заполнение)')

    def test_ed_quota_request(self):
        q = self.ed_quota_req
        self.assertTrue(isinstance(q, EdCenterQuotaRequest))
        self.assertEqual(
            q.__str__(), f'Запрос {self.s_name} №{self.req_num} (заполнение)')

    def test_pr_quota_request(self):
        p = self.pr_quota_req
        self.assertTrue(isinstance(p, ProgramQuotaRequest))
        self.assertEqual(
            p.__str__(), 
            f'{self.program.program_name} ({self.ed_quota_req.ed_center_year})'
        )

    def test_indicator(self):
        self.assertTrue(isinstance(self.indicator, Indicator))
        self.assertEqual(self.indicator.__str__(), self.i_name)

    def test_ed_center_indicator(self):
        self.assertTrue(isinstance(self.e_indicator, EdCenterIndicator))
        self.assertEqual(
            self.e_indicator.__str__(), f'{self.indicator} ({self.ed_center})'
        )
    
    def test_project_position(self):
        self.assertTrue(isinstance(self.position, ProjectPosition))
        self.assertEqual(
            self.position.__str__(), f'{self.p_name} ({self.year} г.)'
        )

    def test_ed_center_employee_position(self):
        self.assertTrue(isinstance(self.ed_position, EdCenterEmployeePosition))
        self.assertEqual(
            self.ed_position.__str__(), f'{self.employee} ({self.position})'
        )
    
    def test_citizen_category(self):
        self.assertTrue(isinstance(self.category, CitizenCategory))
        self.assertEqual(self.category.__str__(), self.c_name)

    def test_grant(self):
        self.assertTrue(isinstance(self.grant, Grant))
        self.assertEqual(
            self.grant.__str__(), f'{self.g_name} ({self.year} г.)'
        )

    def test_application(self):
        self.assertTrue(isinstance(self.appl, Application))
        self.assertEqual(
            self.appl.__str__(),
            f"{self.citizen} ({self.appl.get_appl_status_display()})" 
        )
        self.assertEqual(self.appl.get_ed_price(), math.ceil(23000 * 0.7))
        self.assertEqual(self.appl.get_empl_price(), 0)
        self.assertEqual(self.appl.get_full_price(), math.ceil(23000 * 0.7))
        self.appl.is_working = True
        self.appl.save()
        self.assertEqual(self.appl.get_empl_price(), math.ceil(23000 * 0.3))
        self.assertEqual(self.appl.get_full_price(), 23000)
    
    def test_citizen_application(self):
        self.assertTrue(isinstance(self.c_appl, CitizenApplication))
        self.assertEqual(
            self.c_appl.__str__(),
            f'{self.c_appl.last_name} {self.c_appl.first_name}'
        )
        self.c_appl.middle_name = 'middle_name'
        self.c_appl.save()
        self.assertEqual(
            self.c_appl.__str__(),
            f'{self.c_appl.last_name} {self.c_appl.first_name} {self.c_appl.middle_name}'
        )


# Views tests
class FedEmplViewsTest(TestCase):
    def setUp(self):
        user = User.objects.create_user(
            email='testuser@test.com', password='12345', is_staff=True)
        self.client = Client()
        self.project_year = ProjectYear.objects.create(year=date.today().year)
        self.name ='ГБПОУ "Образовательный центр с. Камышла"'
        self.ed_center = EducationCenter.objects.create(
            name=self.name, contact_person=user, short_name="ОЦК")
        
    def test_index(self):
        response = self.client.get("/")
        self.assertRedirects( response, '/login/?next=/', status_code=302,
                              target_status_code=200)
        
        self.client.login(username='testuser@test.com', password='12345')
        response = self.client.get("/")
        self.assertRedirects(response, '/login/', 
                             status_code=302, target_status_code=302)

    def test_import_express(self):
        self.client.login(username='testuser@test.com', password='12345') 
        response = self.client.get("/import/express/")
        self.assertEqual(response.status_code, 200)

    def test_logout(self):
        self.client.login(username='testuser@test.com', password='12345')
        response = self.client.get("/logout/")
        self.assertRedirects(response, '/login/', 
                             status_code=302, target_status_code=200)
        self.assertFalse(auth.get_user(self.client).is_authenticated)

        response = self.client.get("/logout/")
        self.assertRedirects(response, '/login/?next=/logout/', status_code=302)

    def test_login(self):
        self.assertFalse(auth.get_user(self.client).is_authenticated)
        
        response = self.client.get("/login/")
        self.assertEqual(response.status_code, 200)

        #Login
        #Incorrect
        response = self.client.post("/login/", {
            "email": "testuser@test.com",
            "password": "IncorrectPass"
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["message"], 'Неверный логин и/или пароль.')
        self.assertFalse(auth.get_user(self.client).is_authenticated)
        
        #Correct
        response = self.client.post("/login/", {
            "email": "testuser@test.com",
            "password": "12345"
        })
        self.assertRedirects(
            response,
            f'/admin/',
            status_code=302,
            target_status_code=200
        )
        
        user = auth.get_user(self.client)
        self.assertTrue(auth.get_user(self.client).is_authenticated)
        
        #If user is ed_center
        user.role = 'CO'
        user.save()
        response = self.client.get("/login/")

        self.assertRedirects(
            response,
            f'/education_centers/{self.ed_center.id}/application',
            status_code=302,
            target_status_code=200
        )
        
    def test_citizen_application(self):
        response = self.client.get("/application/citizen/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["is_register"], False)

        response = self.client.post("/application/citizen/", {
            "last_name": "Бурмацкий",
            "first_name":"Антон",
            "middle_name": "",
            "email": "test@test.com",
            "phone": "+79277900805",
            "birthday": "1998-11-25",
            "education_type": "SPVO",
            "employment_status": "MPL",
            "competence": "Компетенция",
            "practice_time": "MRNG",
            "planned_employment": "CMPL",
            "consultation": [],
            "sex": ['male',]
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["is_register"], True)
