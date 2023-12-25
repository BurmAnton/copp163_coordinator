from django.urls import path

from . import views

urlpatterns = [
    path('',views.index, name='index'),
    #Import
    path('import/flow/', views.import_flow, name='import_flow'),
    #Auth
    path('login/', views.login, name="login"),
    path('logout/', views.logout, name="logout"),
    #Quotes
    path(
        'quota/<int:ed_center_id>/request', 
        views.quota_center_request, 
        name="quota_center_request"
    ),
    path('quota/request', views.quota_request, name="quota_request"),
    #Applications
    path(
        'application/citizen/', 
        views.citizen_application, 
        name="citizen_application"
    ),
    path('groups/list/<int:year>', views.groups_list, name="groups_list"),
    path('groups/<int:group_id>', views.group_view, name="group_view"),
    path('invoices/list/<int:year>', views.invoices_list, name="invoices_list"),
    path('invoices/<int:invoice_id>', views.invoice_view, name="invoice_view"),
    path(
        'dashboard/applications/<int:year>', 
        views.applications_dashboard, 
        name="applications_dashboard"
    ),
    path(
        'dashboard/applications/flow/<int:year>', 
        views.flow_appls_dashboard, 
        name="flow_appls_dashboard"
    ),
]
