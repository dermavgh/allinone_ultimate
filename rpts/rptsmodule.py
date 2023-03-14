from datetime import *
import requests
from bs4 import BeautifulSoup
import pygsheets
import json


# session = requests.session()

def write_rtps(usercookie, session, csrf, start, end):
##查詢病人開單資料

    start = int(start) +1
    end = int(end) +2

    gc = pygsheets.authorize(service_file='./credentials.json')
    sht = gc.open_by_url(
        'https://docs.google.com/spreadsheets/d/1DqR1Lhlvk8rSBQG8Kx4VnPTHwScjZRAvIBOEgf7lMl8/')
    wks = sht.worksheet_by_title('2023切片本')

    dolist = []
    for i in range(start, end):
        row = wks.get_row(i, returnas='matrix', include_tailing_empty=False)
        dolist.append(row)

    print(dolist)
    date_0 = datetime.now().strftime("%Y/%m/%d")
    date_7 = (datetime.now()+timedelta(days=-7)).strftime("%Y/%m/%d")

    i = 0
    while i < len(dolist):
        while len(dolist[i]) < 12:
            dolist[i].append('')
        print(dolist)
        if dolist[i][11] != '無' and dolist[i][11] != '':

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
                'SearchMethod': 'reqno',
                'Search': dolist[i][11],
                'button': '',
                'DateScope': '-7',
                'ORBGNDTM_S': date_7,
                'ORBGNDTM_E': date_0,
                'ORENTRY': 'ALL',
                'DEPT': '',
                'SPECITEM': 'DEFAULT',
                'PathMethod': 'S'}

            r = session.post(url_patient, params=payload_patient, headers=header_patient)
            rr = r.json()  # 用json方式讀取回傳的資料

            detail = []
            # for x in range(len(rr['WorkListCVOList'])):
            #     if rr['WorkListCVOList'][x]['ORDSCODE'] == '991DEA02' or rr['WorkListCVOList'][x]['ORDSCODE'] == '991DE002':
            patinet_info = rr['WorkListCVOList'][0]  # 整理json dictionary取出之後需要的資
            ORHISTNO = patinet_info['ORDSTATVO']['ORHISTNO'].strip()
            ORDSEQCN = patinet_info['ORDSTATVO']['ORDSEQCN']
            ORDSEQNO = patinet_info['ORDSTATVO']['ORDSEQNO']
            REQNO = patinet_info['ORDSTATVO']['ORREQNO']
            ORENTRY = patinet_info['ORDERVO']['ORENTRY']
            PFKEY = patinet_info['ORDSCODE']
            ORSTATUS = patinet_info['ORDERVO']['ORSTATUS']
            detail.append([ORHISTNO, ORDSEQCN, ORDSEQNO, REQNO, ORENTRY, PFKEY, ORSTATUS])

            print(detail)


            # 啟動rtpweb病人資料編輯模式

            # if i == 0:
            #     o = 0
            # elif dolist[i][1] == dolist[i-1][1] and detail != []:
            #     o = 1
            # elif dolist[i][1] != dolist[i-1][1] and detail != []:
            #     o = 0
            # else:
            #     o = 2
            #
            # print('i=', i)
            # print('o=', o)



            if detail[0][6] == '31':
                url_do = 'https://web9.vghtpe.gov.tw/RPTWEB/json/ExecuteORDTicket'

                header_do = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36',
                    'Cookie': usercookie
                }

                payload_do = {
                    '_csrf': csrf,
                    'ORMM': '',
                    'ORHISTNO': detail[0][0],
                    'ORDSEQCN': detail[0][1],
                    'ORDSEQNO': detail[0][2],
                    'REQNO': detail[0][3],
                    'ORENTRY': detail[0][4],
                    'PFKEY': detail[0][5],
                    'CURRENT_STATUS':  '31',    #detail[o][6],
                    'EXECUTE_STATUS': '62',
                    'EXECUTE_DATE': date.today()
                }

                    # 30重送
                    # 31開立
                    # 34已排程
                    # 35已抽血
                    # 36已送檢
                    # 37已到站
                    # 38簽收
                    # 60已完成
                    # 61連續計價
                    # 62初步報告
                    # 64正式報告
                    # 66更正報告
                    # 68最後報告

                aa = session.post(url_do, params=payload_do, headers=header_do)


                # 發布報告

                url_post = 'https://web9.vghtpe.gov.tw/RPTWEB/Lab/Lab/Post/ajax'

                header_post = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36',
                    'Cookie': usercookie
                }

                payload_post = {
                    'LREQNO520180201001_RTTECHNI': '',
                    'LREQNO520180201001_RTOPER': '4723G',
                    'LREQNO520180201001_RTREAD': '4723G',
                    'LREQNO520180201001_RTSUPV': '4723G',
                    'LREQNO520180201001_OCGOBACK': '',
                    'LRTDERM120190115001_RTDPATH': '23-' + dolist[i][0],  # 病理號
                    'LRTDERM120190115001_RTDER03': dolist[i][6],  # 臨床診斷
                    'LRTDERM120190115001_RTDER01': dolist[i][5],  # 組織來源
                    'LRTDERM120190115001_RTDER02': dolist[i][8],  # 切片日期
                    'LRTDERM120190115001_RTDERA': 'Pending report.',  # 報告內容
                    'LRTDERM120190115001_RTDER24': date.today(),  # 報告日期
                    'HISTNO': detail[0][0],
                    'REQNO': detail[0][3],
                    'ORENTRY': detail[0][4],
                    'NEXTSTATUS': '62',
                    'RRFMORDER': '00',
                    '_csrf': csrf
                }

                a = session.post(url_post, params=payload_post, headers=header_post)

                print(a)

            i += 1
        else:
            i += 1




