from django.contrib.admin.apps import AdminConfig

class MyAdminConfig(AdminConfig):
    default_site = 'copp163_coordinator.admin.MyAdminSite'