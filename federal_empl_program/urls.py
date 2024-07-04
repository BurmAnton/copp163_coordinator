from django.urls import path

from . import views

urlpatterns = [
    path('',views.index, name='index'),
    #Import
    path('import/atlas/', views.import_atlas_app, name='import_atlas_app'),
    path('import/flow/', views.import_flow, name='import_flow'),
    path('import/profstandarts/', views.import_profstandarts, name='import_profstandarts'),
    #Auth
    path('login/', views.login, name="login"),
    path('logout/', views.logout, name="logout"),
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
    path('quota/dashboard/', views.quota_dashboard, name="quota_dashboard"),
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
    #IRPO
    path('irpo/programs/<int:ed_center_id>', views.irpo_programs, name="irpo_programs"),
    path('irpo/programs/constractor/<int:program_id>', views.program_constractor, name="program_constractor")
]
