from django.shortcuts import render
from django.views.generic import View
from login_app.models import made_context
import login_app.models
from django.shortcuts import render
from django.views.generic import View
from .changeservice_module import *
from login_app.views import session
from changeservice.models import Saved_str, Saved_list, Saved_boo,  savetolist, savetostring, savetoboo, made_context, delete_everything

# Create your views here.

class change(View):
    def get(self, request):
        usercookie = login_app.models.do_not_delete.objects.get(name='usercookie').content
        cookieJar = parse_cookie_string(usercookie)
        patientlist = get_patient_list(session, cookieJar)
        savetolist("patientlist", patientlist)
        vs_list = []
        for key, value in VScode.items():
            vs_list.append(key +" "+ value)
        savetolist('vs_list', vs_list)
        context = made_context()
        return render(request, 'changeservice/changeservice_form.html', context)

    def post(self, request):
        usercookie = login_app.models.do_not_delete.objects.get(name='usercookie').content
        cookieJar = parse_cookie_string(usercookie)
        form = request.POST
        selected_list = form.getlist('patients')
        print(selected_list)

        vs_id_raw = form.get('vs-select')
        if vs_id_raw != "":
            vs_id = vs_id_raw[-5:-1]
            print(vs_id)
            success = change_doc(session, cookieJar, selected_list, vs_id)
            savetoboo("success", success)
        else:
            print("vs not chosen")
            savetoboo("success", False)

        patientlist = get_patient_list(session, cookieJar)
        savetolist("patientlist", patientlist)
        context = made_context()
        return render(request, 'changeservice/changeservice_form.html', context)