from django.urls import path, re_path, include
from .views import *
from sms_parser import settings

urlpatterns = [
    # path('', index, name='home_page'),             # http://127.0.0.1:8000/
    path('', ListAddedSMS.as_view(), name='home_page'),    # http://127.0.0.1:8000/
#   path('parsed_sms/<int:sms_id>/', ShowParsedSMS.as_view(), name='parsed_sms'),  # http://127.0.0.1:8000/parsed_sms/№/
    path('parsed_sms/<int:metadata_id>/', ShowParsedSMS.as_view(), name='parsed_sms'),  # Формируем url с id от ParsedMetaData
    path('about/', about, name='about'),
    path('contact/', contact, name='contact'),
    path('login/', LoginUser.as_view(), name='login'),
    path('logout/', logout_user, name='logout'),
    path('register/', RegisterUser.as_view(), name='register'),
    path('process_sms/', AddSMS.as_view(), name='process_sms'),
]


if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
        path('__debug__/', include('debug_toolbar.urls'))
    ] + urlpatterns

