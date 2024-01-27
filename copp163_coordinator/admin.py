from django.contrib import admin

class MyAdminSite(admin.AdminSite):
    site_header = 'Центр опережающей профессиональной подготовки (Самарской области)'
    site_title = 'ЦОПП СО'

    def get_app_list(self, request):

        ordering = {
            "федеральная программа «содействие занятости»": 1,
            "база граждан": 2,
            "обучение":3,
            "билет в будущее": 4,
            "регионы": 5,
            "пользователи и права": 6,
            'field_history': 7,
            'пользователи и группы': 8,
        }
        app_dict = self._build_app_dict(request)
        app_list = sorted(app_dict.values(), key=lambda x: ordering[x['name'].lower()])

        # Sort the models alphabetically within each app.
        for app in app_list:
            app['models'].sort(key=lambda x: x['name'])

        return app_list