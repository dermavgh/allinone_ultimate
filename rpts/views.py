from django.shortcuts import render
from django.views.generic import View
from login_app.models import made_context
import login_app.models
from .rptsmodule import *
from login_app.views import session


# Create your views here.
class rpts_report(View):
    def get(self, request):
        context = made_context()
        return render(request, 'rpts/rpts_form.html', context)

    def post(self, request):
        form = request.POST
        start = form.get('start')
        end = form.get('end')
        usercookie = login_app.models.do_not_delete.objects.get(name='usercookie').content
        csrf = login_app.models.do_not_delete.objects.get(name='csrf').content
        write_rtps(usercookie, session, csrf, start, end)
        return render(request, 'rpts/rpts_form.html', {'success': True})