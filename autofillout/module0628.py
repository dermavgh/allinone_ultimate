from bs4 import BeautifulSoup
import requests
import re
from datetime import datetime
import pygsheets
import lxml.html
import lxml.html.clean



#~~~~~~~~~~~~~~~~~~~~lookup_opd function 程式碼開始~~~~~~~~~~~~~~~~~~~~
def lookup_opd(ChartNo, usercookie, session):
    # 把會開單人的姓名輸入到doctor裡

    '''
    doctor = ['張雲亭', '吳貞宜', '陳志強', '陳長齡', '李定達', '李政源', '何翊芯', '王文正', '王翔思', '紀兆祥', '位宇勳', '馬聖翔', '丁彙矩', '周佑儒', '汪立心',
              '李嘉倫']
    '''
    doctor = []
    f = open('doctorlist.txt', encoding='UTF-8')
    for line in f.readlines():
        doctor.append(line.strip("\n"))
    f.close
    print(doctor)

    # 開啟查詢功能
    url_lookup = 'https://web9.vghtpe.gov.tw/emr/qemr/qemr.cfm?action=findEmr&histno=' + ChartNo

    header_lookup = {
        'Cookie': usercookie,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'
    }

    payload_lookup = {
        'action': 'findEmr',
        'histno': ChartNo
    }

    lookup = session.post(url_lookup, params=payload_lookup, headers=header_lookup)
    cookies = session.cookies.get_dict()

    ##確認病歷號是否輸入錯誤
    soup_lookup = BeautifulSoup(lookup.text, "lxml")
    print('這裡在測試')
    # print(soup_lookup)

    try:
        lookupinfo = soup_lookup.title.string  # 載入回報的title, 若病歷號輸入錯誤, 應為Error.jsp
    except:
        lookupinfo = soup_lookup.body.string






    if lookupinfo == 'Error.jsp' or lookupinfo == None:  # 病歷號錯誤, 直接停止
        wrongid = True
        return False, wrongid


    else:  # 病歷號正確, 嘗試獲取病人基本資訊
        ## 獲取病人姓名
        soup = BeautifulSoup(lookup.text, "lxml")
        name = soup.select('title')  # 獲取下來的list只有一項, 下面直接帶name[0]
        for i in name:  # 建立好要給google的資料
            patient_info_list_raw = []
            patient_info_list = []
            patient = i.text.replace('\r', '').replace('\n', '').replace('\u3000', ',').replace('-', '').replace(
                '電子病歷查詢系統', '').split(',')
            patient_info_list_raw.append(patient)
            name = patient_info_list_raw[0][0]
            birthday = patient_info_list_raw[0][2][-9:-1][0:4] + '/' + patient_info_list_raw[0][2][-9:-1][4:6] + '/' + patient_info_list_raw[0][2][-9:-1][6:8]
            gender = patient_info_list_raw[0][3].replace('男性', 'M').replace('女性', 'F')
            patient_info_list.append(name)
            patient_info_list.append(birthday)
            patient_info_list.append(gender)


        # 獲得門診資訊
        # ~~~~~~~~~~~~~~~~~~~~~~getopd function 程式碼開始~~~~~~~~~~~~~~~~~~~~~~~~
        def getopd(ChartNo, usercookie, session):

            url_get_opd = 'https://web9.vghtpe.gov.tw/emr/qemr/qemr.cfm?action=findOpd&histno=' + ChartNo

            header_get_opd = {
                'Cookie': usercookie,
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'
            }

            payload_get_opd = {
                'action': 'findOpd',
                'histno': ChartNo
            }

            opd_info = session.get(url_get_opd, params=payload_get_opd, headers=header_get_opd)
            soup = BeautifulSoup(opd_info.text, "lxml")
            td = soup.select('tbody#list td')  # 獲得病人所有的門診資訊

            ##整理門診資訊
            opd_list = []  # 初始門診資訊
            opd_list_new = []  # 整理成每次門診為一個list:[日期, 時間, 主治醫師, 科別, 診斷碼]
            opd_list_href = []  # 整理所有門診的href連結
            opd_list_derm = []  # 擷取所有皮膚科門診紀錄list:[日期, 時間, 主治醫師, 科別, 診斷碼, href]
            opd_list_derm_latest = []  # 擷取病人最近皮膚科門診紀錄list:[[日期, 時間, 主治醫師, 科別, 診斷碼, href],[2],[3],......]
            for i in td:
                a = i.text.replace(' ', '').replace('(', '').replace(')', '')  # 刪除門診資訊中的垃圾文字
                opd_list.append(a)  # 寫入初始門診資訊list內
            for i in range(0, len(opd_list), 5):
                opd_list_new.append(opd_list[i:i + 5])  # 寫入opd_list_new, 整理成每次門診為一個list:[日期, 時間, 主治醫師, 科別, 診斷碼]
            td1 = soup.find_all('a', href=True)  # 獲得所有門診資訊的href
            for a in td1:
                opd_list_href.append(a['href'])  # href整理成list

            if opd_list_new[0][0] == '無門診資料':  #完全沒有門診資料
                 wrongid = False
                 return False, wrongid, patient_info_list


            x = 0
            y = 0
            while x < len(opd_list_new):
                for i in doctor:
                    if i in opd_list_new[x][2]:  # 判斷是否為皮膚科的門診(用開單者名字[在doctor list中]當判斷標準),
                        opd_list_derm.append(opd_list_new[x])  # 若是則把該筆門診資料加入opd_list_derm
                        opd_list_derm[y].append(opd_list_href[x])  # 將該次門診href寫入opd_list_derm
                        y = y + 1
                x = x + 1

            if len(opd_list_derm) != 0:  # 有皮膚科門診紀錄者會到這裡
                for i in opd_list_derm[:5]:
                    opd_list_derm_latest.append(i)
            if len(opd_list_derm) == 0:
                return False, False


            return True, opd_list_derm_latest

        # ~~~~~~~~~~~~~~~~~~~~~~getopd function 程式碼結束~~~~~~~~~~~~~~~~~~~~~~~~


        if getopd(ChartNo, usercookie, session)[0] == False and getopd(ChartNo, usercookie, session)[1] == False:  # 完全沒有門診資料 or 有門診但沒皮膚科門診
            return False, False, patient_info_list


        else:
            lookup_opd = getopd(ChartNo, usercookie, session)[1]  # 就是opd_list_derm_latest
            lookup_success = getopd(ChartNo, usercookie, session)[0]  # 就是True

            return lookup_success, lookup_opd, usercookie, patient_info_list
#~~~~~~~~~~~~~~~~~~~~lookup_opd function 程式碼結束~~~~~~~~~~~~~~~~~~~~


#~~~~~~~~~~~~~~~~~~~~~~~~~getcall function 程式碼開始~~~~~~~~~~~~~~~~~~~
#查詢病人會診紀錄
# 1. 會診O, 皮膚O: 返回會診內容(True, outputlist[0], outputlist[1], outputlist[2], outputlist[3])
# 2. 會診O, 皮膚X: [False]
# 3. 會診X, 皮膚X: [False]
def getcall(ChartNo, usercookie, session):
    url_get_call = 'https://web9.vghtpe.gov.tw/emr/qemr/qemr.cfm?action=findCps&histno=' + ChartNo

    header_get_call = {
        'Cookie': usercookie,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'}
    payload_get_call = {
        'action': 'findCps',
        'histno': ChartNo
    }

    call_raw_list = []
    call_list = [] #病人所有會診紀錄
    call_href_list = []
    call_derm_list = [] #病人所有皮膚科會診紀錄

    call_info = session.get(url_get_call, params=payload_get_call, headers=header_get_call)
    soup = BeautifulSoup(call_info.text)
    call_detail = soup.select('tr td')  # 獲得所有會診資料
    call_detail_href = soup.find_all('a', href=True)  # 獲得每次會診資料的href

    for i in call_detail_href:
        call_href_list.append(i['href'])  # 將href做成list

    for i in call_detail:
        call_raw_list.append(i.text)

    # if len(call_raw_list) == 0: #完全沒有會診資料
    #     return False

    for i in range(0, len(call_raw_list), 7):
        call_list.append(call_raw_list[i:i + 7])  # 將每次會診資料做成list: 會診日期,病房床號,所屬科別,會診科別,會診醫師一,會診醫師二,會診醫師三

    print('==========================')
    print(call_list)

    if call_list[0][0] != '[無資料!!]':  # 有會診資料,找看看是否有皮膚科會診
        # 選出會診皮膚科並串聯href
        x = 0
        y = 0
        for i in call_list:
            if i[3] == 'DERM-DERM':
                call_derm_list.append(call_list[x])
                call_derm_list[y].append(call_href_list[x])
                y = y + 1
            x = x + 1
        if len(call_derm_list) != 0:  # 有抓到皮膚科會診資料,製作下一步payload所需資料
            caseno = call_derm_list[0][7].split('&')[2][7:]
            oseq = call_derm_list[0][7].split('&')[3][5:]
        if len(call_derm_list) == 0:  # 有會診但沒有皮膚科會診會跑來這裡
            print('\n\n！！！查無皮膚科會診資料！！！\n\n')
            print('\n\n！！！這位病人跟皮膚科沒有關係(╬ Ò ‸ Ó)！！！\n\n')
            lookup_call = False
            return [lookup_call]

    if call_list[0][0] == '[無資料!!]':  # 病人完全沒有會診資料
        print('\n\n！！！查無會診資料！！！\n\n')
        print('\n\n！！！這位病人跟皮膚科沒有關係(╬ Ò ‸ Ó)！！！\n\n')
        lookup_call =  False
        return [lookup_call]

    # 獲取最近一次皮膚科會診內容
    url_get_call_latest = 'https://web9.vghtpe.gov.tw' + call_derm_list[0][7]  # 0表示最新一次

    header_get_call_latest = {
        'Cookie': usercookie,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'
    }

    payload_get_call_latest = {
        'action': 'findCps',
        'histno': ChartNo,
        'caseno': caseno,
        'oseq': oseq}

    call_latest = session.get(url_get_call_latest, params=payload_get_call_latest, headers=header_get_call_latest)
    # call_latest = lxml.html.fromstring(call_latest.text)
    # cleaner = lxml.html.clean.Cleaner(style =True )
    # call_latest = cleaner.clean_html(call_latest)

    soup = BeautifulSoup(call_latest.text)
    # soup.replace(u'\xa0', ' ')
    # soup.prettify(formatter=lambda s: s.replace('&nbsp', ' '))

    # for breaks in soup.findAll('&nbsp'):  # 設法刪掉原始碼中的br
    #     breaks.replaceWith(" ")

    call_latest_content = soup.select('tr td')
    # print('===================')
    # print(call_latest_content)
    # print('===================')

    # call_latest_content = soup.select('tr td')  # 獲得會診內容

    outputlist = []
    for i in call_latest_content:
        outputlist.append(i.text)

    outputlist[0] = call_latest_content     # outputlist[0].replace('####', '')
    outputlist[1] = ''#outputlist[1].replace('####', '')
    outputlist[2] = ''#outputlist[2].replace('####', '\n')
    outputlist[3] = ''#outputlist[3].replace('####', '')
    # for i in outputlist:  # 顯示出會診內容
    #     print(i)
    #     print('======')


    return True, outputlist[0], outputlist[1], outputlist[2], outputlist[3]

# ~~~~~~~~~~~~~~~~~~~~~~~~~getcall function 程式碼結束~~~~~~~~~~~~~~~~~~~


# ~~~~~~~~~~~~~~~~~~~~~~~getopd_detail function 程式碼開始~~~~~~~~~~~~~~~~~~~~~~~~~~
# 1. 使用者指定某次皮膚科門診
#     a. 要輸入一張病理單 Double = False: (True, op_sheet_list, double)
#     b. 要輸入兩張病理單 Double = True: (True, op_sheet_list, double)
def getopd_detail(double, usercookie, ChartNo, opd_derm_selected_list, session):
    # select_num = input('請選取門診時間 \n(若要同時帶入兩張病理單，請在數字後面加上+)').upper()

     # 嘗試取得選定門診內的內容

    url_get_opsheet = 'https://web9.vghtpe.gov.tw/' + opd_derm_selected_list[5]

    header_get_opd = {
        'Cookie': usercookie,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'
    }

    ### headers 可以用之前的header_get_opd就好
    payload_get_opsheet = {
        'action': 'findOpd',
        'histno': ChartNo,
        'dt': opd_derm_selected_list[0],
        'dept': opd_derm_selected_list[5].split('&')[3][5:],
        'doc': opd_derm_selected_list[5].split('&')[4][4:],
        'deptnm': opd_derm_selected_list[5].split('&')[5][7:]
    }
    opsheet = session.get(url_get_opsheet, params=payload_get_opsheet, headers=header_get_opd)
    soup1 = BeautifulSoup(opsheet.text)  # 獲得該次門診內的內容


    # 開始整理獲得的門診內容
    op_sheet_list_raw = []  # [標題, 組織來源, 術前診斷]
    op_sheet_list = []


    for i in soup1.select('td.left pre')[2]:  # 0是門診S, 1是門診O, 2是門診P

        op_sheet_list_raw.append(i.text.replace('\r\n', '').replace('  ', '').replace('【H.E STAIN IV-SKIN NON-CYST/TAG】：', 'HE Stain IV-Skin Non-Cyst/Tag').replace('【SMALL SURGICAL SPECIMEN-LEVEL 4】', 'Small Surgical Specimen- Level 4').replace('【H.E STAIN III-SKIN CYST/TAG】', 'HE. Stain III- Skin Cyst/Tag').replace('【SURGICAL PATHOLOGY LEVEL III】', 'Surgical Pathology Level III').replace('：', ''))
        #.replace('【H.E STAIN IV-SKIN NON-CYST/TAG】', 'H.E STAIN IV-SKIN NON-CYST/TAG').erplace('【H.E STAIN III-SKIN CYST/TAG】', 'H.E STAIN III-SKIN CYST/TAG').replace('【SURGICAL PATHOLOGY LEVEL III】','SURGICAL PATHOLOGY LEVEL III').replace('【SMALL SURGICAL SPECIMEN-LEVEL 4】','SMALL SURGICAL SPECIMEN-LEVEL 4' ).replace('【','').replace('】','').replace('：', ':'))

    for i in range(op_sheet_list_raw.count('')):
        op_sheet_list_raw.remove('')

    if len(op_sheet_list_raw) ==0:
        op_sheet_list_raw.append(' ')

    if 'HE Stain IV-Skin Non-Cyst/Tag' not in op_sheet_list_raw[0] and 'Small Surgical Specimen- Level 4' not in op_sheet_list_raw[0] and 'HE. Stain III- Skin Cyst/Tag' not in op_sheet_list_raw[0] and 'Surgical Pathology Level III' not in op_sheet_list_raw[0]:
        return False, double #使用者要的double

    list1 = op_sheet_list_raw[:3]
    op_sheet_list.append(list1)
    if len (op_sheet_list_raw)  >= 8 and ('HE Stain IV-Skin Non-Cyst/Tag' in op_sheet_list_raw[4] or 'Small Surgical Specimen- Level 4' in op_sheet_list_raw[4] or 'HE. Stain III- Skin Cyst/Tag' in op_sheet_list_raw[4] or 'Surgical Pathology Level III' in op_sheet_list_raw[4]): #表示有兩張病理單被抓到
        list2 = op_sheet_list_raw[4:7]
        op_sheet_list.append(list2)
        double = True #真double
    else:
        double =False #真double


    return True, op_sheet_list, double
# ~~~~~~~~~~~~~~~~~~~~~~~getopd_detail function 程式碼結束~~~~~~~~~~~~~~~~~~~~~~~~~~

# ~~~~~~~~~~~~~~~~~~~~自動手術資訊 function 程式碼開始~~~~~~~~~~~~~~~~~~~~~~~~~~~
# # 從門診資訊中自動帶入手術資訊
# # 1.要兩張病理單double=True: (True, for_post_list :[[標題1, 組織來源1, 臨床診斷1], [標題2, 組織來源2, 臨床診斷2]])
# # 2.要一張病理單double=False: (True, for_post_list :[[標題, 組織來源, 臨床診斷])
#
# def makepatho(double, op_sheet_list):
#     for_post_list = []
#     x = 1
#     while x <= 5:  # 設定x可以決定要製造幾個病理單, x=1 第一張, x=5 第二張, x=9, 第三張........
#         tissue_origin = op_sheet_list[x][20:].strip()
#         impression = op_sheet_list[x + 1][17:].strip()
#         for_post_list.append([tissue_origin,impression])
#         if double == True: #double = True 要擷取兩張病理單
#             x = x+4
#         else: #double = False 要擷取1張病理單
#             return True, for_post_list
#
#         return True, for_post_list
# ~~~~~~~~~~~~~~~~~~~~自動手術資訊 function 程式碼結束~~~~~~~~~~~~~~~~~~~~~~~~~~~


# #~~~~~~~~~~~~~~~~~~~~修改資料 function 程式碼開始~~~~~~~~~~~~~~~~~~~~~~
# #使用者是否修改資料會在前端處理好，送過來的資料一律修改, 輸出: html_detail_list_new, op_sheet_list
# def modifydata(html_detail_list, html_op_sheet_list, TEL):
#         html_detail_list[html_detail_list.index(['tissue_origin'])]= tissue_origin1
#         html_detail_list[html_detail_list.index(['impression'])]= impression1
#         html_detail_list_new = html_detail_list
#
#         op_sheet_list_new = []
#
#         return html_detail_list_new
# # ~~~~~~~~~~~~~~~~~~~~修改資料 function 程式碼結束~~~~~~~~~~~~~~~~~~~~~~

# ~~~~~~~~~~~~~~~~~~~~手動手術資訊 function 程式碼開始~~~~~~~~~~~~~~~~~~~~~~~~~~~
# def makepatho_m(double, op_sheet_list):
# ~~~~~~~~~~~~~~~~~~~~手動手術資訊 function 程式碼結束~~~~~~~~~~~~~~~~~~~~~~~~~~~`


#~~~~~~~~~~~~~~~~~~~~~~~~登入SUYT表單 function程式碼開始~~~~~~~~~~~~~~~~~~~~
# 登入SUYT表單系統
# 登入成功: (cookie_login, token)
# 登入失敗: 還沒寫

def login_s(session, ChartNo, ID):

    ##表單填寫系統
    url_homepage = 'http://10.97.249.35:8080/webnur/comm/login.jsp'

    header_homepage = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        'Connection': 'keep-alive',
        'Host': '10.97.249.35:8080',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36',
    }

    ##先獲取表單填寫系統登入前JSESSIONID(要放在登入cookie裡)
    r = session.get(url_homepage, headers=header_homepage)
    cookies = session.cookies.get_dict()
    cookie_login = 'JSESSIONID=' + cookies['JSESSIONID']

    ##登入表單填寫系統
    url_login = 'http://10.97.249.35:8080/webnur/comm/login.do;jsessionid=' + cookies['JSESSIONID']

    payload_login = {
        'LOGIN': '1',
        'autologin': 'true',
        'accession_no': ChartNo,
        'sheet_no': 'VT81-1',
        'print': '',
        'typerid': 'null',
        'starttime': 'null',
        'endtime': 'null',
        'image': 'null',
        'viewall': 'null',
        'topage': '',
        'printversion': '',
        'pre_accession_no': '',
        'userid': ID,
        'password': 'cirtnexe0845',  # 每個人的密碼都是一樣的, 這是資訊室設定的密碼, 可從登入表單填寫系統的開發者模式中獲取
        'language': 'zh_TW'
    }

    header_login = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Host': '10.97.249.35:8080',
        'Referer': 'http://10.97.249.35:8080/webnur/comm/login.jsp?sheet_no=VT81-1&userid=' + ID + '&accession_no=' + ChartNo,
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36',
    }

    # 登入後JSESSIONID會更新，所以要獲取登入後的JSESSIONID
    r1 = session.post(url_login, headers=header_login, data=payload_login)

    cookies1 = session.cookies.get_dict()
    cookie_logged = "'JSESSIONID=" + cookies1['JSESSIONID'] + "'"

    # 要填寫表單需要額外token, 這裡獲取org.apache.struts.taglib.html.TOKEN
    url_token = 'http://10.97.249.35:8080/webnur/NUR/NUR1A001.do?pageid=NUR1A001&accession_no=' + ChartNo + '&series_no=1&sheet_no=VT81-1&view='

    payload_token = {
        'pageid': 'NUR1N001',
        'accession_no': ChartNo,
        'series_no': '1',
        'sheet_no': 'VT81-1'}

    header_token = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Content-Length': '3943',
        'cookie': cookie_login,
        'Host': '10.97.249.35:8080',
        'Referer': 'http://10.97.249.35:8080/webnur/comm/login.jsp?sheet_no=VT81-1&userid=' + ID + '&accession_no=' + ChartNo,
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36',
    }

    r2 = session.post(url_token, headers=header_token, data=payload_token)

    soup = BeautifulSoup(r2.text, 'html.parser')
    tags = soup.find_all('input')
    for tag in tags:
        if tag.get('name') == 'org.apache.struts.taglib.html.TOKEN':
            token = tag.get('value')

    return cookie_login, token
#~~~~~~~~~~~~~~~~~~~~~~~~登入SUYT表單 function程式碼結束~~~~~~~~~~~~~~~~~~~~~~~



###要開始post SUYT囉
#html_detail_list:[[病歷號, 姓名, 日期, VS, 標題, 組織來源, 術前診斷], [~~~]]
#op_sheet_list=[[組織, 診斷, 術式], [組織, 診斷, 術式]]


# op_sheet_list= [[title1, tissue1, impres1, 'ABC'], [title2, tissue2, impress2, 'DEF']]





#~~~~~~~~~~~~~~~~~~~~~~~~製造通用SUYT表單 function程式碼開始~~~~~~~~~~~~~~~~~~~
#製造postn, posta 共用的payload： (payload_op_common(是一個dictionary), OPType_list)

def OPType_get_common(token, ID, ChartNo, z, op_sheet_list, VS):
    # user = {'DOC4721E': '周佑儒', 'DOC4722F': '丁彙矩', 'DOC4724H': '汪立心', 'DOC4725J': '李嘉倫'}  # !!!!!!!這個字典應該要想辦法放在通用地方

    user = {}
    f = open('userlist.txt', encoding='UTF-8')
    for line in f.readlines():
        s = line.strip("\n").split(' ')
        user[s[0]] = s[1]
    f.close

    time = str(datetime.now().time())
    date = datetime.now().strftime("%Y/%m/%d")


    OPType_list = [] ##要向getn(), geta()告知手術要用的術式, 要return出來

    OPType_raw = op_sheet_list[z][3]
    OPType = OPType_raw.upper()
    for i in OPType:
        OPType_list.append(i)

    ##兩種方法共用的payload_op部分
    payload_op_common = {
        'org.apache.struts.taglib.html.TOKEN': token,
        'SAVE': 'undefined',
        'orgid': '06',
        'issave': 'false',
        'isprint': 'false',
        'mccid': '1',
        'mciname': '皮膚部procedure note',
        'layer_1': '',
        'layer_1_Id': '',
        'series_no': '1',
        'sheet_no': 'VT81-1',
        'version': '1',
        'isview': '0',
        'iso': '',
        'doc': '',
        'indate': '',
        'typeuserid': ID,
        'typer': user[ID],
        'showYear': '0',
        'doctoruserid': ID,
        'reportyear': date,
        'reporthour': time[0:2],
        'reportmin': time[3:5],
        'phrase': '1',
        'room': '',
        'patno': '',
        'patname': '',
        'sex': '',
        'birthday': '',
        'age': '',
        'vistingstaff': '',
        'txt_107979': '',
        'hidtxt_107979': '107979',
        'txt_107980': ChartNo,
        'hidtxt_107980': '107980',
        'txt_107981': '',
        'hidtxt_107981': '107981',
        'txt_107982': '',
        'hidtxt_107982': '107982',
        'txt_107983': '',
        'hidtxt_107983': '107983',
        'txt_107984': '',
        'hidtxt_107984': '107984',
        'txt_107990': date,
        'hidtxt_107990': '107990',
        'txt_107993': 'nil',
        'hidtxt_107993': '107993',
        'txt_107995': 'nil',
        'hidtxt_107995': '107995',
        'hidcheck_108428': '',
        'hiduncheck_108428': '',
        'hidcheckB_108428': '',
        'hiduncheckB_108428': '',
        'hidcheckC_108428': '',
        'hiduncheckC_108428': '',
        'txt_108429': '',
        'hidtxt_108429': '108429',
        'sel_107998': '---',
        'sel_108431': '---',
        'sel_108432': '---',
        'txt_108433': op_sheet_list[z][1], #手術位置
        'hidtxt_108433': '108433',
        '19745': '108124',
        'hidrdo_108124': 'A. Betadine + ALCOHOL',
        'hidunrdo_108124': '',
        'hidrdoB_108124': '',
        'hidunrdoB_108124': '',
        'hidrdoC_108124': '',
        'hidunrdoC_108124': '',
        'hidrdo_108125': 'B. Betadine',
        'hidunrdo_108125': '',
        'hidrdoB_108125': '',
        'hidunrdoB_108125': '',
        'hidrdoC_108125': '',
        'hidunrdoC_108125': '',
        '19746': '108126',
        'hidrdo_108126': 'A. 2％ lidocaine + epinephrine',
        'hidunrdo_108126': '',
        'hidrdoB_108126': '',
        'hidunrdoB_108126': '',
        'hidrdoC_108126': '',
        'hidunrdoC_108126': '',
        'hidrdo_108127': 'B. 2％ lidocaine',
        'hidunrdo_108127': '',
        'hidrdoB_108127': '',
        'hidunrdoB_108127': '',
        'hidrdoC_108127': '',
        'hidunrdoC_108127': '',
        'hidcheck_108011': 'A.切除整個病灶（Excisional biopsy）',
        'hiduncheck_108011': '',
        'hidcheckB_108011': '',
        'hiduncheckB_108011': '',
        'hidcheckC_108011': '',
        'hiduncheckC_108011': '',
        'hidcheck_108012': 'B.切除部分病灶（Incisional biopsy）',
        'hiduncheck_108012': '',
        'hidcheckB_108012': '',
        'hiduncheckB_108012': '',
        'hidcheckC_108012': '',
        'hiduncheckC_108012': '',
        'hidcheck_113299': 'C.Shave biopsy',
        'hiduncheck_113299': '',
        'hidcheckB_113299': '',
        'hiduncheckB_113299': '',
        'hidcheckC_113299': '',
        'hiduncheckC_113299': '',
        'hidcheck_113300': 'D.Punch biopsy',
        'hiduncheck_113300': '',
        'hidcheckB_113300': '',
        'hiduncheckB_113300': '',
        'hidcheckC_113300': '',
        'hiduncheckC_113300': '',
        'hidcheck_108014': 'E.全指甲移除 (Total nail extraction)',
        'hiduncheck_108014': '',
        'hidcheckB_108014': '',
        'hiduncheckB_108014': '',
        'hidcheckC_108014': '',
        'hiduncheckC_108014': '',
        'hidcheck_108015': 'F.部分指甲移除 (Partial nail extraction)',
        'hiduncheck_108015': '',
        'hidcheckB_108015': '',
        'hiduncheckB_108015': '',
        'hidcheckC_108015': '',
        'hiduncheckC_108015': '',
        'hidcheck_108016': 'G.指甲矯正 (Nail bracing)',
        'hiduncheck_108016': '',
        'hidcheckB_108016': '',
        'hiduncheckB_108016': '',
        'hidcheckC_108016': '',
        'hiduncheckC_108016': '',
        'hidcheck_113302': 'H.電氣燒灼 (Electrocauterization)',
        'hiduncheck_113302': '',
        'hidcheckB_113302': '',
        'hiduncheckB_113302': '',
        'hidcheckC_113302': '',
        'hiduncheckC_113302': '',
        'hidcheck_113303': 'I.TCA化學燒灼 (TCA chemical cauterization)',
        'hiduncheck_113303': '',
        'hidcheckB_113303': '',
        'hiduncheckB_113303': '',
        'hidcheckC_113303': '',
        'hiduncheckC_113303': '',
        'hidcheck_113304': 'J.冷凍治療 (Cryotherapy)',
        'hiduncheck_113304': '',
        'hidcheckB_113304': '',
        'hiduncheckB_113304': '',
        'hidcheckC_113304': '',
        'hiduncheckC_113304': '',
        '19751': '108128',
        'hidrdo_108128': '平順',
        'hidunrdo_108128': '',
        'hidrdoB_108128': '',
        'hidunrdoB_108128': '',
        'hidrdoC_108128': '',
        'hidunrdoC_108128': '',
        'hidrdo_108129': '有併發症：',
        'hidunrdo_108129': '',
        'hidrdoB_108129': '',
        'hidunrdoB_108129': '',
        'hidrdoC_108129': '',
        'hidunrdoC_108129': '',
        'txt_108026': '',
        'hidtxt_108026': '108026',
        'txt_108028': VS,   # 主治醫師
        'hidtxt_108028': '108028',
        'txt_108029': user[ID], # 開刀者
        'hidtxt_108029': '108029',
        'returnmessage': ''
        }
    return payload_op_common, OPType_list, date, time
#~~~~~~~~~~~~~~~~~~~~~~~~製造通用SUYT表單 function程式碼結束~~~~~~~~~~~~~~~~~~~



#~~~~~~~~~~~~~~~~~~~~~~~~製造postn專屬payload function程式碼開始~~~~~~~~~~~~~~~~~~~
#將共用payload, 特屬npayload結合, 準備給postn使用: payload_op(是一個dictionart)

def OPType_get_N(ChartNo, payload_op_common, OPType_list):

    payload_opn_unique = {
        'pageid': 'NUR1N001',
        'accession_no': ChartNo,
        'series_no': '1',
        'viewid': '',
        'viewcount': '7',
        'cut': '',
        'starttime': '',
        'endtime': '',
        'onlyview': '',
        'haschange': '0',
    }

    OPdict = {
        'A': '108011',
        'B': '108012',
        'C': '113299',
        'D': '113300',
        'E': '108014',
        'F': '108015',
        'G': '108016',
        'H': '113302',
        'I': '113303',
        'J': '113304'}

    # 將共用字典及獨特字典融合
    payload_op = {}
    payload_op.update(payload_op_common)
    payload_op.update(payload_opn_unique)

    # 將所要術式編碼進paylod中
    for key in OPType_list:
        newkey = 'chk_' + OPdict[key]
        payload_op[newkey] = OPdict[key]



    return payload_op

#~~~~~~~~~~~~~~~~~~~~~~~~製造postn專屬payload  function程式碼結束~~~~~~~~~~~~~~~~~~~


#~~~~~~~~~~~~~~~~~~~~~~~~執行postn表單 function程式碼開始~~~~~~~~~~~~~~~~~~~
# 無論成功或失敗不會返還任何東西

def postn(cookie_login, ChartNo, payload_op, session):
    url_formN = 'http://10.97.249.35:8080/webnur/NUR/NUR1N001.do'

    headers_op = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-TW,zh;q=0.9',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Cookie': cookie_login,
        'Host': '10.97.249.35:8080',
        'Origin': 'http://10.97.249.35:8080',
        'Referer': 'http://10.97.249.35:8080/webnur/NUR/NUR1A001.do?pageid=NUR1A001&accession_no=' + ChartNo + '&series_no=1&sheet_no=VT81-1&view=',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.115 Safari/537.36'
    }

    session.post(url_formN, headers=headers_op, data=payload_op)

#~~~~~~~~~~~~~~~~~~~~~~~~執行postn表單 function程式碼結束~~~~~~~~~~~~~~~~~~~


#~~~~~~~~~~~~~~~~~~~~~~~~製造posta專屬payload function程式碼開始~~~~~~~~~~~~~~~~~~~
#將共用payload, 特屬a payload結合, 準備給posta使用: payload_op(是一個dictionart)

def OPType_get_A(ChartNo, payload_op_common, OPType_list):

    print('a開始')
    print('=============================')
    payload_opa_unique = {
        'pageid': 'NUR1A001',
        'accession_no': ChartNo,
        'view': '',
        'hasoldaccession': 'false',
        'oldaccession_no': '',
        'versiondate': '',
        'haschange': 'false',
        'historytype': '0',
    }

    OPdict = {
        'A': '108011',
        'B': '108012',
        'C': '113299',
        'D': '113300',
        'E': '108014',
        'F': '108015',
        'G': '108016',
        'H': '113302',
        'I': '113303',
        'J': '113304'}

    # 將共用字典及獨特字典融合
    payload_op = {}
    payload_op.update(payload_op_common)
    payload_op.update(payload_opa_unique)

    # 將所要術式編碼進paylod中
    for key in OPType_list:
        newkey = 'chk_' + OPdict[key]
        payload_op[newkey] = OPdict[key]

    return payload_op

#~~~~~~~~~~~~~~~~~~~~~~~~製造postn專屬payload  function程式碼結束~~~~~~~~~~~~~~~~~~~


# ~~~~~~~~~~~~~~~~~~~~~~~~執行posta表單 function程式碼開始~~~~~~~~~~~~~~~~~~~
# 無論成功或失敗不會返還任何東西

def posta(cookie_login, ChartNo, payload_op, session):

    print('a1開始')
    print('=============================')
    
    url_formA = 'http://10.97.249.35:8080/webnur/NUR/NUR1A001.do'

    headers_op = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-TW,zh;q=0.9',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Cookie': cookie_login,
        'Host': '10.97.249.35:8080',
        'Origin': 'http://10.97.249.35:8080',
        'Referer': 'http://10.97.249.35:8080/webnur/NUR/NUR1A001.do?pageid=NUR1A001&accession_no=' + ChartNo + '&series_no=1&sheet_no=VT81-1&view=',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.115 Safari/537.36'
    }

    session.post(url_formA, headers=headers_op, data=payload_op)

    # ~~~~~~~~~~~~~~~~~~~~~~~~執行postn表單 function程式碼結束~~~~~~~~~~~~~~~~~~~


def suytcheck(ChartNo, cookie_login, ID, date, time, session):
    # 檢查是否寫入SUYT成功
    url_quiry = 'http://10.97.249.35:8080/webnur/NUR/NUR1N001.do?pageid=NUR1N001&accession_no='+ ChartNo + '&series_no=1&sheet_no=VT81-1'

    payload_quiry = {
    'accession_no': ChartNo,
    'series_no': '1',
    'sheet_no': 'VT81-1'}

    header_quiry = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Content-Length': '3943',
    'cookie': cookie_login,
    'Host': '10.97.249.35:8080',
    'Referer': 'http://10.97.249.35:8080/webnur/comm/login.jsp?sheet_no=VT81-1&userid='+ID+'&accession_no='+ ChartNo,
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36',
    }

    r= session.get(url_quiry, headers = header_quiry, data = payload_quiry)
    soup = BeautifulSoup(r.text, 'html.parser')
    sheets = soup.select('select#selVersion option')
    sheets_list= []
    for i in sheets:
        sheets_list.append(i.text)

    print(sheets_list[-1], date, time[0:2], time[3:5])

    if date in sheets_list[-1] and time[0:2] in sheets_list[-1] and time[3:5] in sheets_list[-1]:
        return True
    else:
        return False

# ~~~~~~~~~~~~~~~~~~~~~~~~執行posta表單 function程式碼結束~~~~~~~~~~~~~~~~~~~



# ~~~~~~~~~~~~~~~~將資料寫入goole表單 程式碼開始~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 寫入後return該筆病理號

def toGoogle(name, birthday, gender, ChartNo, tissue_origin, impression, TEL, ID, REQ):
    # user = {'DOC4721E': '周佑儒', 'DOC4722F': '丁彙矩', 'DOC4724H': '汪立心', 'DOC4725J': '李嘉倫'}

    user = {}
    f = open('userlist.txt', encoding='UTF-8')
    for line in f.readlines():
        s = line.strip("\n").split(' ')
        user[s[0]] = s[1]
    f.close


    gc = pygsheets.authorize(service_file='./credentials.json')
    sht = gc.open_by_url(
        'https://docs.google.com/spreadsheets/d/1yIgn12m_AJ8cx2qZCLoOg6JjHdk7lQNNU4KkgpIxvw0/edit#gid=0')
    wks = sht.worksheet_by_title('工作表1')


    date = datetime.now().strftime("%Y/%m/%d")

    
    ##寫入google表單
    ##電話小知識 037苗栗 049南投 089台東 082金門 0836連江
    if '037' == TEL[:3] or '089' == TEL[:3] or '082' == TEL[:3] or '049' == TEL[:3]:
        TEL = str(TEL[:3]) + '-' + str(TEL[3:])
    elif '0836' == TEL[:4]:
        TEL = str(TEL[:4]) + '-' + str(TEL[4:])
    elif '09' == TEL[:2]:
        TEL = str(TEL[:4]) + '-' + str(TEL[4:])
    else:
        TEL = str(TEL[:2]) + '-' + str(TEL[2:])

    togoogle = []

    print('拽取最後一行開始')
    last_row = len(wks.get_col(2, include_tailing_empty=False))
    #####下面的資料要從哪裡取得要再改～～～～######

    print('拽取最後一行結束')
    
    togoogle.append([last_row, name, birthday, gender, ChartNo, tissue_origin, impression, '', date, TEL, user[ID], REQ])

    print('填寫表單中')
    wks.update_row(last_row + 1, togoogle)
    print('填寫表單成功')
    # print(last_row)
    #
    # print(wks.find('丁彙矩', cols=(1, 2))[-1].row)
    # print(type(wks.find('丁彙矩', cols=(1, 2))[-1].row))
    try:
        print('比對資料中')
        a =  wks.find(name)[-1].row
        print('比對資料完成')
        if a != last_row +1:
            return False
        else:
            pathono = a-1
            return pathono
    except:
        return False


    # ~~~~~~~~~~~~~~~~將資料寫入goole表單 程式碼結束~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    operate_times = operate_times + 1
# ~~~~~~~~~~~~~~~~將資料寫入goole表單 程式碼結束~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~



#======find REQ============================================================
def findREQ(usercookie, session, csrf, ChartNo):
    url_patient = 'https://web9.vghtpe.gov.tw/RPTWEB/json/WorkList'


    header_patient = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36',
            'Cookie': usercookie,
            'Referer': 'https://web9.vghtpe.gov.tw/RPTWEB/Rpts/Index?node=5',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'X-Requested-With': 'XMLHttpRequest',
            'Host': 'web9.vghtpe.gov.tw',
            'Origin': 'https://web9.vghtpe.gov.tw'
        }

    payload_patient = {
            '_csrf': csrf,
            'SearchMethod': 'histno',
            'Search': ChartNo,
            'button': '',
            'DateScope': '-7',
            'ORBGNDTM_S': '2022/06/24',
            'ORBGNDTM_E': '2022/07/01',
            'ORENTRY': 'ALL',
            'DEPT': '',
            'SPECITEM': 'DEFAULT',
            'PathMethod': 'S'}

    r = session.post(url_patient, params=payload_patient, headers=header_patient)
    rr = r.json()  # 用json方式讀取回傳的資料

    detail = []
    for x in range(len(rr['WorkListCVOList'])):
        if rr['WorkListCVOList'][x]['ORDSCODE'] == '991DEA02' or rr['WorkListCVOList'][x]['ORDSCODE'] == '991DE002':
            patinet_info = rr['WorkListCVOList'][x]  # 整理json dictionary取出之後需要的資
            REQNO = patinet_info['ORDSTATVO']['ORREQNO']
            ORSTATUS = patinet_info['ORDERVO']['ORSTATUS']
            if ORSTATUS == "31" or ORSTATUS == "62":
                detail.append(REQNO)

    return detail
