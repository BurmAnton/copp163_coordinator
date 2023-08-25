from django.test import TestCase
from django.urls import reverse

from citizens.models import Citizen, DisabilityType, Municipality, School
from education_centers.forms import ImportDataForm

# models test
class MunicipalityTest(TestCase):

    def create_municipality(self, name="Тольяттинский"):
        return Municipality.objects.create(name=name)
    
    def test_municipality_creation(self):
        m = self.create_municipality()
        self.assertTrue(isinstance(m, Municipality))
        self.assertEqual(m.__str__(), m.name)


class SchoolTest(TestCase):

    def create_school(self, name="Школа №46", ter_admin='TADM'):
        return School.objects.create(
            name=name, territorial_administration=ter_admin
        )
    
    def test_municipality_creation(self):
        sch = self.create_school()
        self.assertTrue(isinstance(sch, School))
        self.assertEqual(
            sch.__str__(), 
            f"{sch.name} ({sch.get_territorial_administration_display()})"
        )


class DisabilityTypeTest(TestCase):

    def create_disability_type(self, name="Нарушения слуха"):
        return DisabilityType.objects.create(name=name)
    
    def test_disability_type_creation(self):
        dsb_t = self.create_disability_type()
        self.assertTrue(isinstance(dsb_t, DisabilityType))
        self.assertEqual(dsb_t.__str__(), dsb_t.name)


class CitizenTest(TestCase):

    def create_citizen(self, last_name="Иванов", first_name="Иван",
    middle_name=None):
        return Citizen.objects.create(
            last_name=last_name,
            first_name=first_name,
            middle_name=middle_name
        )
    
    def test_citizen_creation(self):
        ctzn = self.create_citizen(middle_name="Иванович")
        self.assertTrue(isinstance(ctzn, Citizen))
        self.assertEqual(
            ctzn.__str__(), 
            f'{ctzn.last_name} {ctzn.first_name} {ctzn.middle_name}'
        )
    
    def test_citizen_wo_middle_name_creation(self):
        ctzn = self.create_citizen()
        self.assertTrue(isinstance(ctzn, Citizen))
        self.assertEqual(
            ctzn.__str__(), 
            f'{ctzn.last_name} {ctzn.first_name}'
        )

# views test
class ViewsTest(TestCase):

    def test_import_schools_view(self):
        url = reverse("import_schools")
        resp = self.client.get(url)

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context['message'], None)
    