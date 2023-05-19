from bs4 import BeautifulSoup
import requests
import re
from datetime import datetime
import http.cookiejar
import urllib.parse

def parse_cookie_string(cookie_string):
    # Create a new CookieJar object
    cookiejar = http.cookiejar.CookieJar()

    # Parse the cookie string into a dictionary
    cookie_dict = urllib.parse.parse_qs(cookie_string, keep_blank_values=True)

    # Loop through the dictionary and add each cookie to the CookieJar
    for name, values in cookie_dict.items():
        for value in values:
            cookie = http.cookiejar.Cookie(
                version=0,
                name=name,
                value=value,
                port=None,
                port_specified=False,
                domain='',
                domain_specified=False,
                domain_initial_dot=False,
                path='/',
                path_specified=True,
                secure=False,
                expires=None,
                discard=False,
                comment=None,
                comment_url=None,
                rest=None
            )
            cookiejar.set_cookie(cookie)

    return cookiejar

VScode={
    '張雲亭' : 'DOC4720D',
    '吳貞宜' : 'DOC4714E',
    '陳志強' : 'DOC4772K',
    '陳長齡' : 'DOC4723G',
    '李定達' : 'DOC4741L',
    '李政源' : 'DOC4703A',
    '何翊芯' : 'DOC4789J'}


def find_VS_name(id_num):
    for key, value in VScode.items():
        numbers = re.findall('\d+', value)
        if numbers and numbers[0] == id_num:
            result = key
            break
    return result

def loginweb9(ID, PW, session):
    print(ID, PW)
    try:
        # 取得OAKS_SESS4(未登入)
        url_login = 'https://eip.vghtpe.gov.tw/login.php'
        r_login = session.get(url_login)
        cookieJar = requests.cookies.RequestsCookieJar()
        for cookie in r_login.cookies:
            cookieJar.set(cookie.name, cookie.value, domain=cookie.domain)

        # 取得APP_USER_LOGIN_PERSISTENT_DESK + OAKS_SESS4(登入)
        url_login_action = 'https://eip.vghtpe.gov.tw/login_action.php'
        payload_login_action = {
            'loginCheck': '1',
            'login_name': ID,
            'password': PW,
            'fromAjax': '1',
        }
        header_login_action = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36',
            'Host': 'eip.vghtpe.gov.tw',
            'Origin': 'https://eip.vghtpe.gov.tw',
            'Referer': 'https://eip.vghtpe.gov.tw/login.php',
        }
        r_login_action = session.post(url_login_action, data=payload_login_action, headers=header_login_action,
                                      cookies=cookieJar)
        for cookie in r_login_action.cookies:
            cookieJar.set(cookie.name, cookie.value, domain=cookie.domain)

        # 取得PUBLIC_APP_USER_SSO_TOKEN
        url_login_check = 'https://eip.vghtpe.gov.tw/login_check.php'
        header_login_check = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36',
            'Host': 'eip.vghtpe.gov.tw',
            'Referer': 'https://eip.vghtpe.gov.tw/login.php',
        }
        r_login_check = session.get(url_login_check, headers=header_login_check, cookies=cookieJar)
        index = (r_login_check.text).find('/')
        location = (r_login_check.text)[index:-10]
        fromcheck = location[26:]
        print(fromcheck)

        url_token = 'https://eip.vghtpe.gov.tw' + location
        header_token = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36',
            'Host': 'eip.vghtpe.gov.tw',
            'Referer': 'https://eip.vghtpe.gov.tw/login_check.php',
        }
        payload_token = {
            'fromcheck': fromcheck,
        }

        r_token = session.get(url_token, params=payload_token, headers=header_token, cookies=cookieJar,
                              allow_redirects=False)
        for cookie in r_token.cookies:
            cookieJar.set(cookie.name, cookie.value, domain=cookie.domain)

        # 取得JSESSIONIDw9
        url_rpts = 'https://web9.vghtpe.gov.tw/RPTWEB/'
        header_rpts = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36',
            'Host': 'web9.vghtpe.gov.tw',
            'Referer': 'https://eip.vghtpe.gov.tw/',
        }
        r_rpts = session.get(url_rpts, headers=header_rpts, cookies=cookieJar, allow_redirects=False)
        for cookie in r_rpts.cookies:
            cookieJar.set(cookie.name, cookie.value, domain=cookie.domain)
        print(cookieJar)


        # cookieJar.set('SIGNONID', ID)
        usercookie = ''
        for cookie in cookieJar:
            usercookie += (cookie.name + '=' + cookie.value + '; ')

        print('-------rpts_usercookie-----------------------')
        print(usercookie)
        print('---------------------------------------------')

        return cookieJar

    except KeyError: # 登入失敗
        return False

def get_patient_list(session, cookieJar):
    # 取得JSESSIONIDdoc
    url_drweb = "https://web9.vghtpe.gov.tw/emr/qemr/qemr.cfm"
    header_drweb = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36',
        'Host': 'eip.vghtpe.gov.tw',
        'Referer': 'https://eip.vghtpe.gov.tw/',
    }
    payload_drweb ={
        'action': 'findPatient',
        'srnId': 'DRWEBAPP',
        'seqno': '009',
    }
    r_drweb =  session.post(url_drweb, params = payload_drweb, headers=header_drweb, cookies=cookieJar)
    for cookie in r_drweb.cookies:
        cookieJar.set(cookie.name, cookie.value, domain=cookie.domain)
    print(cookieJar)

    # 搜尋醫師病人並加入patientlist
    search_list = []
    for value in VScode.values():
        numbers = re.findall('\d+', value)
        search_list.append(numbers[0])

    patientlist = []
    for drid in search_list:
        url_find_patient = 'https://web9.vghtpe.gov.tw/emr/qemr/qemr.cfm?action=findPatient'

        header_find_patient = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36',
            'Host': 'web9.vghtpe.gov.tw',
        }

        payload_find_patient = {
            'wd': '0',
            'histno': '',
            'pidno': '',
            'namec': '',
            'drid': drid,
            'er': '0',
            'bilqrta': '0',
            'bilqrtdt': '',
            'bildurdt': '0',
            'other': '0',
            'nametype': ''}

        r_find_patient = session.post(url_find_patient, params=payload_find_patient, headers=header_find_patient, cookies=cookieJar)
        soup = BeautifulSoup(r_find_patient.text, features="html.parser")
        patient = soup.select('tbody tr')
        if "無資料!!" not in patient[0].text:
            for row in patient:
                cells = row.find_all('td')
                entry = [cell.get_text(strip=True) for cell in cells]
                entry[0] = find_VS_name(drid)+drid
                histo = row.select('td a')[0].get('id').strip()
                entry[2] = histo
                patientlist.append(entry)



    print('====================以下為皮膚科住院病人====================')
    for p in patientlist:
        print(p)
    # Exmaple: [['主治: 吳貞宜4714', 'B077- 24', '50168', '黃隆一', '男', '19411026(81歲)'], ['主治: 吳貞宜4714', 'B077- 25', '6188314', '韓家進', '男', '19580425(64歲)']]
    print('==========================================================')

    return patientlist

def change_doc(session, cookieJar, selected_id, vs_id):
    # selected_id=[]
    # # vs_id = input('請輸入欲轉VS之燈號: ')
    # for patient in patientlist:
    #     selected_id.append(patient[2])

    for id in selected_id:
        url_lookup = 'https://web9.vghtpe.gov.tw/emr/qemr/qemr.cfm?action=findEmr&histno=' + id
        header_lookup = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36',
            'Host': 'web9.vghtpe.gov.tw',
        }
        cookieJar = cookieJar
        r_lookup = session.post(url_lookup, headers=header_lookup, cookies=cookieJar)
        soup = BeautifulSoup(r_lookup.text, features="html.parser")
        href = 'https://web9.vghtpe.gov.tw' + soup.select('tr td form')[2].get('action')


        url_order = href
        header_order = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36',
            'Host': 'web9.vghtpe.gov.tw',
        }
        r_order = session.post(url_order, headers=header_order, cookies=cookieJar)
        soup = BeautifulSoup(r_order.text, features="html.parser")
        tkvalue = soup.select('form input')[0].get('value')


        url_service = 'https://web9.vghtpe.gov.tw/VGHTRTE/TRTMNT/patientDiagnos.jsp'
        header_service = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36',
            'Host': 'web9.vghtpe.gov.tw',
        }
        payload_service = {
            'token': tkvalue
        }
        r_service = session.post(url_service, headers=header_service, cookies=cookieJar, params=payload_service)
        soup = BeautifulSoup(r_service.text, features="html.parser")
        DRRNA = soup.find('input', {'id': 'DRRNA'})['value']
        DRRID = soup.find('input', {'id': 'DRRID'})['value']
        print(DRRNA, DRRID)


        url_change = 'https://web9.vghtpe.gov.tw/VGHTRTE/edit/dr.do'
        header_change = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36',
            'Host': 'web9.vghtpe.gov.tw',
        }
        payload_change = {
            'DRVSID': VScode[find_VS_name(vs_id)],
            'DRVSNA': find_VS_name(vs_id),
            'DRVS2ID': "",
            'DRVS2NA': "",
            'DRRID': DRRID,
            'DRRNA': DRRNA,
            'DRIID': '',
            'DRINA': '',
            'DRCID': '',
            'DRCNA': '',
            'NPID': '',
            'NPNA': '',
            'onDRServiceFun':'0',
            'token': tkvalue}

        r_change = session.post(url_change, params=payload_change, headers=header_change, cookies=cookieJar)
        if "true" in BeautifulSoup(r_change.text, features="html.parser"):
            print("病歷號" + id + "修改成功!")
        else:
            print("病歷號" + id + "修改失敗QAQ")
    return True





def main():
    session = requests.session()
    # ID = input("帳號: ")
    # PW = input("密碼: ")
    ID = "doc4724h"
    PW = "qasw1234"
    cookieJar = loginweb9(ID, PW, session)
    patientlist = get_patient_list(session, cookieJar)
    change_doc(session, cookieJar, patientlist)



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
