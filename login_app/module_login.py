from bs4 import BeautifulSoup
import requests
import re
from datetime import datetime
import pygsheets
import lxml.html
import lxml.html.clean

# session = requests.session()
#要建立資料庫的內容
# 1.登入相關資訊
# ID, PW, cookie(不斷更新),
# 2.病人相關資訊
# 姓名, 生日, 性別, 病歷號, 日期, VS, 標題, 組織來源1, 術前診斷1, 術式1, 組織來源2, 術前診斷2, 術式2

def logoutweb9(session):
    url_logout = 'https://web9.vghtpe.gov.tw/Signon/ibm_security_logout?logoutExitPage=/'

    header_logout = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36',
    }

    payload_logout = {
        'logoutExitPage': '/'
    }

    session.get(url_logout, headers=header_logout, params = payload_logout)




#~~~~~~~~~~~~~~~~~~~~login function 程式碼~~~~~~~~~~~~~~~~~~~~
#嘗試登入web9,
# 1. 登入成功: (True, usercookie)
# 2. 登入失敗: (False)
# return login_success, usercookie


def loginweb9(ID, PW, session):
    print(ID, PW)
    try:
        ##擷取登入前homepage cookie(JSESSIONIDsso)

        url_homepage = 'https://web9.vghtpe.gov.tw/Signon/login.jsp'
        header_homepage = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36',
        }

        r_homepage = session.get(url_homepage, headers=header_homepage)
        cookieJar = requests.cookies.RequestsCookieJar()
        for cookie in r_homepage.cookies:  # 登入前的JSESSIONIDsso
            cookieJar.set(cookie.name, cookie.value, domain=cookie.domain)
        print(cookieJar)



        # 登入web9 並擷取 JSESSIONIDsso(登入後), LtpaToken2

        url_homepage_login = 'https://web9.vghtpe.gov.tw/Signon/lockaccount'
        header_homepage_login = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36',
        }
        payload_homepage_login = {
            'j_username': ID,
            'j_password': PW,
            'Submit': '確認登入',
            'j_pin': '',
            'j_pin2': '',
            'ipaddr': 'N'
        }

        r_homepage_login = session.post(url_homepage_login, params=payload_homepage_login, headers=header_homepage_login, cookies = cookieJar, allow_redirects=False)
        for cookie in r_homepage_login.cookies:  # 登入後的JSESSIONIDsso + LtpaToken2
            cookieJar.set(cookie.name, cookie.value, domain=cookie.domain)
        print(cookieJar)


        ## 獲得 JSESSIONIDdoc
        url_get_doc = 'https://web9.vghtpe.gov.tw/emr/qemr/qemr.cfm?action=findPatient&srnId=DRWEBAPP&seqNo=009'
        header_get_doc = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36',
        }
        payload_get_doc = {
            'action': 'findPatient',
            'srnId': 'DRWEBAPP',
            'seqNo': '009'}

        r_get_doc = session.get(url_get_doc, params=payload_get_doc, headers=header_get_doc, cookies = cookieJar, allow_redirects=False)
        for cookie in r_get_doc.cookies:  # 登入後的JSESSIONIDsso + LtpaToken2 + JSESSIONIDdoc
            cookieJar.set(cookie.name, cookie.value, domain=cookie.domain)
        print(cookieJar)

        usercookie = ''
        for cookie in cookieJar:
            usercookie += (cookie.name + '=' + cookie.value + '; ')
        print('-------login_usercookie-----------------------')
        print(usercookie)
        print('----------------------------------------------')

        ## 以上為登入步驟，並成功獲得JSESSIONIDdoc, JSESSIONIDsso, LtpaToken2, 若要使用其他功能，可能要嘗試獲得更多cookie

        return True, usercookie


    except KeyError: # 登入失敗
        return False


def loginrpts(usercookie, session, ID, PW):

    url_login = 'https://eip.vghtpe.gov.tw/login.php'
    r_login = session.get(url_login)

    cookieJar = requests.cookies.RequestsCookieJar()
    for cookie in r_login.cookies: #取得OAKS_SESS4(未登入)
        cookieJar.set(cookie.name, cookie.value, domain=cookie.domain)

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
    r_login_action = session.post(url_login_action, data=payload_login_action, headers=header_login_action,cookies=cookieJar)
    for cookie in r_login_action.cookies: #取得APP_USER_LOGIN_PERSISTENT_DESK + OAKS_SESS4(登入)
        cookieJar.set(cookie.name, cookie.value, domain=cookie.domain)

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
    for cookie in r_token.cookies: #取得PUBLIC_APP_USER_SSO_TOKEN
        cookieJar.set(cookie.name, cookie.value, domain=cookie.domain)

    url_rpts = 'https://web9.vghtpe.gov.tw/RPTWEB/'
    header_rpts = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36',
        'Host': 'web9.vghtpe.gov.tw',
        'Referer': 'https://eip.vghtpe.gov.tw/',
    }
    r_rpts = session.get(url_rpts, headers=header_rpts, cookies=cookieJar, allow_redirects=False)
    for cookie in r_rpts.cookies: #取得JSESSIONIDw9
        cookieJar.set(cookie.name, cookie.value, domain=cookie.domain)
    print(cookieJar)

    # 取得csrf
    url_get_csrf = 'https://web9.vghtpe.gov.tw/RPTWEB/Rpts/Index?node=5'
    header_get_csrf = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36',
    }
    payload_get_csrf = {'node': '5'}

    r_get_csrf = session.get(url_get_csrf, params=payload_get_csrf, headers=header_get_csrf, cookies=cookieJar)
    soup = BeautifulSoup(r_get_csrf.text, features="lxml")
    csrf = soup.find("meta", {"name": "_csrf"})['content']
    cookieJar.set('SIGNONID', ID)
    usercookie_add = ''
    for cookie in cookieJar:
        usercookie_add += (cookie.name + '=' + cookie.value + '; ')
    usercookie = usercookie + "; " + usercookie_add
    print('-------rpts_usercookie-----------------------')
    print(usercookie)
    print('---------------------------------------------')

    return usercookie, csrf, cookieJar

#================================================================
def test():
    print("hahaha")
