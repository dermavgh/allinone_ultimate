from django.shortcuts import render
from django.views.generic import View
from login_app.models import *
from .module_login import logoutweb9, loginweb9, loginrpts
import requests
import lxml

session = requests.session()
# Create your views here.
class login(View):
    def get(self, request):
        return render(request, 'login_app/login.html')

    def post(self, request):
        delete_everything()
        form = request.POST
        ID = form.get('ID').upper()
        savetodonotdelete('ID', ID)
        PW = form.get('PW')
        savetodonotdelete('PW', PW)
        # login_list = [True, ID + PW]
        login_list = loginweb9(ID, PW, session)
        context = made_context()
        if login_list == False:
            return render(request, 'login_app/login.html', {"Error": True})
        else:
            usercookie = login_list[1]
            savetodonotdelete("usercookie", usercookie)
            rptslist = loginrpts(usercookie, session, ID, PW)
            usercookie2 = rptslist[0]
            csrf = rptslist[1]
            cookieJar = rptslist[2]
            savetodonotdelete('usercookie', usercookie2)
            savetodonotdelete('csrf', csrf)
            savetodonotdelete('cookieJar', cookieJar)
            return render(request, 'login_app/intersection.html', context)

class logout(View):
    def get(self, request):
        return render(request, 'login_app/login.html')

    def post(self, request):
        form = request.POST
        out = form.get('out')
        if out =='True':
            logoutweb9(session)
        return render(request, 'login_app/login.html')

class intersection(View):
    def get(self, request):
        return render(request, 'login_app/intersection.html')
