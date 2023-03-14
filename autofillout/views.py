from django.shortcuts import render
from django.views.generic import View
from autofillout.models import Saved_str, Saved_list, Saved_boo,  savetolist, savetostring, savetoboo, made_context, delete_everything
from .module0628 import *
import login_app.models
from login_app.views import session
import requests
import lxml
from datetime import datetime
import pygsheets


class chartno(View):
    def get(self, request):
        context = made_context()
        return render(request, 'autofillout/chartno.html', context)

    def post(self, request):
        form = request.POST
        usercookie = login_app.models.do_not_delete.objects.get(name="usercookie").content
        delete_everything()
        savetostring('usercookie', usercookie)
        chartno= form.get("chartno")
        savetostring("chartno", chartno)
        csrf = login_app.models.do_not_delete.objects.get(name='csrf').content
        rptslist = findREQ(usercookie, session, csrf, chartno)
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        print(rptslist)
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        if len(rptslist)>0:
            REQ1 = rptslist[0]
            savetostring('REQ1', REQ1)
            try:
                REQ2 = rptslist[1]
                savetostring('REQ2', REQ2)
            except:
                pass
        else:
            REQ1 = "無"
            savetostring('REQ1', REQ1)
            REQ2 = "無"
            savetostring('REQ2', REQ2)

        output = lookup_opd(chartno, usercookie, session)
        # output = [True, [['2022/06/11','09:15','hahaha','DERM', 'ICD-9', 'href'], ['2022/06/12', '08:11', 'nonono','DERM','ICD-9', 'href'], ['2022/06/18', '13:44', 'tototo','DERM', 'ICD-9', 'href']],'usercookie123',["西瓜", '2025/06/01', 'M']]
        # output = [False, True]
        # output = [False, False, ["東瓜", '2020/06/01', 'M']]
        if output[0] == False:
            if output[1] == True:
                return render(request, 'autofillout/chartno.html', {"Error": True})
            else:
                patient_info_list = output[2]
                name = patient_info_list[0]
                savetostring("name", name)
                birth = patient_info_list[1]
                savetostring("birth", birth)
                gender = patient_info_list[2]
                savetostring("gender", gender)

                return render(request, 'autofillout/before_getcall.html')
        else:
            opd_list_derm_latest = output[1]
            savetolist("opd_list_derm_latest", opd_list_derm_latest)
            usercookie = output[2]
            savetostring("usercookie", usercookie)
            patient_info_list = output[3]
            name = patient_info_list[0]
            savetostring("name", name)
            birth = patient_info_list[1]
            savetostring("birth", birth)
            gender = patient_info_list[2]
            savetostring("gender", gender)

            table=[]
            for i in range(len(opd_list_derm_latest)):
                lst =[]
                lst.append(i)
                lst.append(opd_list_derm_latest[i][0])
                lst.append(opd_list_derm_latest[i][2])
                lst.append(opd_list_derm_latest[i][3])
                table.append(lst)

            context = made_context()
            context["table"] = table
            context['opd'] = True
            return render(request, 'autofillout/table.html', context)

class selectopd(View):
    def get(self, request):
        context = made_context()
        return render(request, 'autofillout/table.html', context)

    def post(self, request):
        form = request.POST
        select_num = form.get("opdnumber")

        if select_num == "N" or select_num =="n":
            return render(request, 'autofillout/before_getcall.html')
        else:
            if "+" in select_num or form.get("MoreThenOne") == "True":
                double = True
                select_num = select_num.replace("+", "")
            else:
                double = False
            savetoboo('double', double)
            usercookie = Saved_str.objects.get(name="usercookie").content
            chartno = Saved_str.objects.get(name='chartno').content
            opd_list_derm_latest = Saved_list.objects.get(name='opd_list_derm_latest').content
            opd_derm_selected_list = opd_list_derm_latest[int(select_num)]
            savetolist("opd_derm_selected_list", opd_derm_selected_list)
            patho_date = opd_derm_selected_list[0]
            VS = opd_derm_selected_list[2]
            savetostring('patho_date', patho_date)
            savetostring('VS', VS)
        output = getopd_detail(double, usercookie, chartno, opd_derm_selected_list, session)
        # output = [True, [['surgical pathology level IV', '0000000000000000000head', '0000000000000000egg'], ['surgical pathology level IV', '0000000000000000000tail', '0000000000000000apple']], double]
        print('-------------------')
        print(output)
        print('-------------------')
        if output[0] == False:
            op_list1 = ["其他",'', '']
            savetolist('op_list1',  op_list1)
            if double == True:
                op_list2 = ["其他", '', '']
                savetolist('op_list2', op_list2)
            context = made_context()
            return render(request, 'autofillout/opinfo.html', context)
        else:
            op_sheet_list= output[1]
            op_list1 = []
            op_list2 = []
            double = output[-1]
            savetoboo('double', double)
            if double == True:
                op_list1 = op_sheet_list[0]
                savetolist('op_list1', op_list1)
                tissue_origin_1 = op_list1[1][19:]
                savetostring('tissue_origin_1',tissue_origin_1)
                impression_1 = op_list1[2][16:]
                savetostring('impression_1',impression_1)
                op_list2 = op_sheet_list[1]
                savetolist('op_list2', op_list2)
                tissue_origin_2 = op_list2[1][19:]
                savetostring('tissue_origin_2',tissue_origin_2)
                impression_2 = op_list2[2][16:]
                savetostring('impression_2',impression_2)
            else:
                op_list1 = op_sheet_list[0]
                savetolist('op_list1', op_list1)
                tissue_origin_1 = op_list1[1][19:]
                savetostring('tissue_origin_1',tissue_origin_1)
                impression_1 = op_list1[2][16:]
                savetostring('impression_1',impression_1)
            savetoboo('double',  double)
            savetostring('TEL', "")
            #REQ1 = '測試用1'
            #REQ2 = '測試用2'
            # savetostring('REQ1', REQ1)
            # savetostring('REQ2', REQ2)
            context = made_context()
            return render(request, 'autofillout/opinfo.html', context)

class opsheetinfo(View):
    def get(self, request):
        context = made_context()
        return render(request, 'autofillout/opinfo.html', context)
    def post(self, request):
        double = Saved_boo.objects.get(name="double").content
        form = request.POST
        op1 = form.get('op1')
        if double == True:
            op2 = form.get('op2')
        if op1 == 'True':
            op_list1 = Saved_list.objects.get(name = 'op_list1').content
            tissue_origin_1 = form.get('tissue_origin_1')
            savetostring('tissue_origin_1', tissue_origin_1)
            impression_1 = form.get('impression_1')
            savetostring('impression_1', impression_1)
            op_list1[1] = tissue_origin_1
            op_list1[2] = impression_1
            savetolist('op_list1', op_list1)
            REQ1 = form.get('REQ1')
            savetostring('REQ1', REQ1)
            if double == True and op2 == 'True':
                    op_list2 = Saved_list.objects.get(name='op_list2').content
                    tissue_origin_2 = form.get('tissue_origin_2')
                    savetostring('tissue_origin_2', tissue_origin_2)
                    impression_2 = form.get('impression_2')
                    savetostring('impression_2', impression_2)
                    op_list2[1] = tissue_origin_2
                    op_list2[2] = impression_2
                    savetolist('op_list2', op_list2)
                    REQ2 = form.get('REQ2')
                    savetostring('REQ2', REQ2)
            else:
                double = False
                savetoboo('double', double)
        elif double == True and op2 == 'True':
            op_list1 = Saved_list.objects.get(name='op_list2').content
            tissue_origin_1 = form.get('tissue_origin_2')
            savetostring('tissue_origin_1', tissue_origin_1)
            impression_1 = form.get('impression_2')
            savetostring('impression_1', impression_1)
            op_list1[1] = tissue_origin_1
            op_list1[2] = impression_1
            savetolist('op_list1', op_list1)
            double = False
            savetoboo('double', double)
        else:
            context = made_context()
            context['op_error'] = True
            return render(request, 'autofillout/opinfo.html', context)
        TEL = form.get('TEL')
        savetostring('TEL', TEL)
        if double == True:
            double_str = '兩張'
        else:
            double_str = '一張'
        context = made_context()
        context['double_str'] = double_str
        return render(request, 'autofillout/opinfo_recheck.html', context)

class opmethod(View):
    def get(self, request):
        context = made_context()
        return render(request, 'autofillout/opmethod.html', context)
    def post(self, request):
        form = request.POST
        double = Saved_boo.objects.get(name="double").content
        ID = login_app.models.do_not_delete.objects.get(name='ID').content
        chartno = Saved_str.objects.get(name='chartno').content
        VS= Saved_str.objects.get(name='VS').content[:-8]
        name = Saved_str.objects.get(name='name').content
        birth = Saved_str.objects.get(name='birth').content
        gender= Saved_str.objects.get(name='gender').content
        TEL = Saved_str.objects.get(name='TEL').content
        optype_1 = form.get("optype_1").upper()
        op_list1 = Saved_list.objects.get(name="op_list1").content
        # op_list1[1] = op_list1[1][19:]
        # op_list1[2] = op_list1[2][16:]
        op_list1.append(optype_1)
        op_sheet_list = [op_list1]
        if double == True:
            optype_2 = form.get("optype_2").upper()
            op_list2 = Saved_list.objects.get(name="op_list2").content
            # op_list2[1] = op_list2[1][19:]
            # op_list2[2] = op_list2[2][16:]
            op_list2.append(optype_2)
            op_sheet_list = [op_list1, op_list2]
        savetolist('op_sheet_list', op_sheet_list)
        google1 = form.get('google1')
        if google1 == "True":
            savetoboo('google1', True)
        else:
            savetoboo('google1', False)
        if double == True:
            google2 = form.get('google2')
            if google2 == "True":
                savetoboo('google2', True)
            else:
                savetoboo('google2', False)
        token = login_s(session, chartno, ID)[1]
        cookie_login = login_s(session, chartno, ID)[0]

        print('==================================')
        print('開始填表單')
        stop = False
        z=0
        result_list =[]
        while stop == False and z < 2:
            payload_op_common = OPType_get_common(token, ID, chartno, z, op_sheet_list, VS)[0]
            date = OPType_get_common(token, ID, chartno, z, op_sheet_list, VS)[2]
            time = OPType_get_common(token, ID, chartno, z, op_sheet_list, VS)[3]
            OPType_list = OPType_get_common(token, ID, chartno, z, op_sheet_list, VS)[1]
            payload_op = OPType_get_N(chartno, payload_op_common, OPType_list)
            login_s(session, chartno, ID)
            OPType_get_common(token, ID, chartno, z, op_sheet_list, VS)
            OPType_get_N(chartno, payload_op_common, OPType_list)
            postn(cookie_login, chartno, payload_op, session)
            payload_op = OPType_get_A(chartno, payload_op_common, OPType_list)
            OPType_get_A(chartno, payload_op_common, OPType_list)
            posta(cookie_login, chartno, payload_op, session)
            result = suytcheck(chartno, cookie_login, ID, date, time, session)
            print(result)
            result_list.append(result)

            z = z + 1
            if double == False:
                stop = True

        google1 = form.get('google1')
        if google1 == "True":
            savetoboo('google1', True)
        else:
            savetoboo('google1', False)
        if double == True:
            google2 = form.get('google2')
            if google2 == "True":
                savetoboo('google2', True)
            else:
                savetoboo('google2', False)


        if Saved_boo.objects.get(name='google1').content == False:
            savetostring("google_no1", '無')
        else:
            tissue_origin_1 = Saved_str.objects.get(name = "tissue_origin_1").content
            impression_1 = Saved_str.objects.get(name = "impression_1").content
            REQ1 = Saved_str.objects.get(name = "REQ1").content
            output1 = toGoogle(name, birth, gender, chartno, tissue_origin_1, impression_1, TEL, ID, REQ1)
            if output1 == False:
                savetostring("google_no1", "錯誤")
            else:
                savetostring("google_no1", output1)
        if double == True:
            if Saved_boo.objects.get(name='google2').content == False:
                savetostring("google_no2", '無')
            else:
                tissue_origin_2 = Saved_str.objects.get(name="tissue_origin_2").content
                impression_2 = Saved_str.objects.get(name="impression_2").content
                REQ2 = Saved_str.objects.get(name="REQ2").content
                output2 = toGoogle(name, birth, gender, chartno, tissue_origin_2, impression_2, TEL, ID, REQ2)
                if output2 == False:
                    savetostring("google_no2", "錯誤")
                else:
                    savetostring("google_no2", output2)
        final_result =[]
        for i in result_list:
            if i == True:
                final_result.append('完成ε٩(๑> ₃ <)۶з')
            else:
                final_result.append('失敗( ｰ̀дｰ́ )')

        context = made_context()
        context['final_result'] = final_result
        return render(request, 'autofillout/results.html', context)

class getcall_content(View):
    def post(self, request):
        chartno = Saved_str.objects.get(name = "chartno").content
        usercookie = Saved_str.objects.get(name = "usercookie").content
        output = getcall(chartno, usercookie, session)
        # output = [True, 'content1', 'content2', 'content2', 'content2']
        if output[0] == False:
            return render(request, 'before_getcall.html', {"Error": True})
        else:
            call_content= output[1]
            num = 0
            for i in call_content:
                call_content[num] = str(i).replace('<td style="text-align:left;color: #AA0000;font-size: 12px">', '<td style="padding-bottom: 0.5%; padding-top: 0.5%;">')
                call_content[num] = call_content[num].replace('\xa0','').replace('\u3000', '')
                num+=1
            # savetolist('call_content', call_content)
            print('wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww')
            print(call_content)
            # call_content=['<td>ouput1</td', '<td>ouput2</td', '<td>ouput3</td', '<td>ouput4</td']
            savetolist('call_content', call_content)
            context= made_context()
            # context['call_content'] = call_content
            VS = call_content[3][60:63]
            savetostring('VS', VS)
            return render(request, 'autofillout/call.html', context)


class call(View):
    def get(self, request):
        context = made_context()
        return render(request, 'autofillout/call.html', context)
    def post(self, request):
        form = request.POST
        if form.get("MoreThenOne") == "True":
            double = True
        else:
            double = False
        savetoboo('double', double)
        tissue_origin_1 = form.get('tissue_origin_1')
        savetostring('tissue_origin_1', tissue_origin_1)
        impression_1 = form.get('impression_1')
        savetostring('impression_1', impression_1)
        op_list1 = ['surgical pathology level IV', tissue_origin_1, impression_1]
        savetolist('op_list1', op_list1)
        if double == True:
            tissue_origin_2 = form.get('tissue_origin_2')
            savetostring('tissue_origin_2', tissue_origin_2)
            impression_2 = form.get('impression_2')
            savetostring('impression_2', impression_2)
            op_list2 = ['surgical pathology level IV', tissue_origin_2, impression_2]
            savetolist('op_list2', op_list2)
        REQ1 = "無"
        savetostring('REQ1', REQ1)
        REQ2 = "無"
        savetostring('REQ2', REQ2)
        TEL = form.get('TEL')
        savetostring('TEL', TEL)
        VS = Saved_str.objects.get(name='VS').content
        savetostring("VS", VS)
        if double == True:
            double_str = '兩張'
        else:
            double_str = '一張'
        context = made_context()
        context['double_str'] = double_str
        return render(request, 'autofillout/callinfo_recheck.html', context)
