from django.shortcuts import render
from django.http import HttpResponse


# Create your views here.


def index(request):
    context = {
        'title': 'Расшифровка СМС',
    }
    return render(request, 'parser_sms/index.html', context=context)
