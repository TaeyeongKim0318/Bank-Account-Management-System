import requests
from bs4 import BeautifulSoup as bs
import datetime
from dateutil import parser
import os
import json
import math
import time

from image_checker import get_keypad_img

def get_transactions(bank_num, birthday, password, SDate, EDate):
    print("계좌번호 : ", bank_num)
    print("계좌 비밀번호 : ", birthday)
    print("생년월일 : ", password)
    print("조회 시작일 : ", SDate)
    print("조회 종료일 : ", EDate)
    # KB 마우스 입력기 관련 정보 및 쿠키 정보 가져오기
    VIRTUAL_KEYPAD_INFO = get_keypad_img()
    
    # get_keypad_img()에서 받아온 데이터 변수에 저장
    PW_DIGITS = VIRTUAL_KEYPAD_INFO['PW_DIGITS']
    KEYMAP = VIRTUAL_KEYPAD_INFO['KEYMAP']
    JSESSIONID = VIRTUAL_KEYPAD_INFO['JSESSIONID']
    QSID = VIRTUAL_KEYPAD_INFO['QSID']
    KEYPAD_USEYN = VIRTUAL_KEYPAD_INFO['KEYPAD_USEYN']
    
    # 입력 받은 개인 정보 자료형 변환
    bank_num = str(bank_num)
    birthday = str(birthday)
    password = str(password)
    
    # 입력 받은 비밀번호, get_keypad_img()에서 크롤링한 onmousedown과 mapping
    hexed_pw = ''
    for p in password:
        hexed_pw += PW_DIGITS[str(p)]

    # 오늘 년, 월, 일 변수에 저장
    start_year = SDate.strftime('%Y')
    # print('start_year')
    # print(start_year)
    start_month = SDate.strftime('%m')
    # print('start_month')
    # print(start_month)
    start_day = SDate.strftime('%d')
    # print('start_day')
    # print(start_day)
    start_all = SDate.strftime('%Y%m%d')
    # print('start_all')
    # print(start_all)
    # print()
    end_year = EDate.strftime('%Y')
    # print('end_year')
    # print(end_year)
    end_month = EDate.strftime('%m')
    # print('end_month')
    # print(end_month)
    end_day = EDate.strftime('%d')
    # print('end_day')
    # print(end_day)
    end_all = EDate.strftime('%Y%m%d')
    # print('end_all')
    # print(end_all)

    # api로 보낼 데이터 저장
    cookies = {
        '_KB_N_TIKER': 'N',
        'JSESSIONID': JSESSIONID,
        'QSID': QSID,
        'delfino.recentModule': 'G3',
    }
    headers = {
        'Pragma': 'no-cache',
        'Origin': 'https://obank.kbstar.com',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'ko-KR,ko;q=0.8,en-US;q=0.6,en;q=0.4,la;q=0.2,da;q=0.2',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.79 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded;  charset=UTF-8',
        'Accept': 'text/html, */*; q=0.01',
        'Cache-Control': 'no-cache',
        'X-Requested-With': 'XMLHttpRequest',
        'Connection': 'keep-alive',
        'Referer': 'https://obank.kbstar.com/quics?page=C025255&cc=b028364:b028702&QSL=F',
        'DNT': '1',
    }

    params = (
        ('chgCompId', 'b028770'),
        ('baseCompId', 'b028702'),
        ('page', 'C025255'),
        ('cc', 'b028702:b028770'),
    )

    data = [
        ('KEYPAD_TYPE_{}'.format(KEYMAP), '3'),
        ('KEYPAD_HASH_{}'.format(KEYMAP), hexed_pw),
        ('KEYPAD_USEYN_{}'.format(KEYMAP), KEYPAD_USEYN),
        ('KEYPAD_INPUT_{}'.format(KEYMAP), '\uBE44\uBC00\uBC88\uD638'),
        ('signed_msg', ''),
        ('\uC694\uCCAD\uD0A4', ''),
        ('\uACC4\uC88C\uBC88\uD638', bank_num),
        ('\uC870\uD68C\uC2DC\uC791\uC77C\uC790', start_all),
        ('\uC870\uD68C\uC885\uB8CC\uC77C', end_all),
        ('\uACE0\uAC1D\uC2DD\uBCC4\uBC88\uD638', ''),
        ('\uBE60\uB978\uC870\uD68C', 'Y'),
        ('\uC870\uD68C\uACC4\uC88C', bank_num),
        ('\uBE44\uBC00\uBC88\uD638', password),
        ('USEYN_CHECK_NAME_{}'.format(KEYMAP), 'Y'),
        ('\uAC80\uC0C9\uAD6C\uBD84', '2'),
        ('\uC8FC\uBBFC\uC0AC\uC5C5\uC790\uBC88\uD638', birthday),
        ('\uC870\uD68C\uC2DC\uC791\uB144', start_year),
        ('\uC870\uD68C\uC2DC\uC791\uC6D4', start_month),
        ('\uC870\uD68C\uC2DC\uC791\uC77C', start_day),
        ('\uC870\uD68C\uB05D\uB144', end_year),
        ('\uC870\uD68C\uB05D\uC6D4', end_month),
        ('\uC870\uD68C\uB05D\uC77C', end_day),
        ('\uC870\uD68C\uAD6C\uBD84', '2'),
        ('\uC751\uB2F5\uBC29\uBC95', '2'),
    ]

    # 위에서 저장한 데이터를 api를 이용하여 해당 URL에 전송
    r = requests.post('https://obank.kbstar.com/quics', headers=headers, params=params, cookies=cookies, data=data)

    # beautifulsoup를 이용하여 조회된 거래내역 페이지 크롤링
    soup = bs(r.text, 'html.parser')

    # 크롤링한 페이지 중 테이블 body의 행(tr) 데이터 transactions에 저장
    transactions = soup.select('#pop_contents > table.tType01 > tbody > tr')

    transaction_list = []

    for idx, value in enumerate(transactions):
        # 저장되어 있는 행 데이터 중 셀(td)데이터 tds에 저장
        tds = value.select('td')
        if not idx % 2:
            _date = tds[0].text
            _date = _date[:10] + ' ' + _date[10:]
            date = parser.parse(_date)  # 날짜: datetime
            amount = -int(tds[3].text.replace(',', '')) or int(tds[4].text.replace(',', ''))  # 입금 / 출금액: int
            balance = int(tds[5].text.replace(',', ''))  # 잔고: int
            detail = dict(date=date, amount=amount, balance=balance)
        else:
            transaction_by = tds[0].text.strip()  # 거래자(입금자 등): str
            tmp = dict(transaction_by=transaction_by)
            transaction_list.append({**detail, **tmp})

    print("결과값 : ", transaction_list)
    return transaction_list

if __name__ == '__main__':
    bank_num = input('Input your Bank Acc(only digits): ')
    birthday = input('Input your birthday(ex: 941024): ')
    password = input('Input your pw(4 digits): ')
    
    SYear = int(input('When is the start year?(ex: 2023): '))
    SMonth = int(input('When is the start month?(ex: 11): '))
    SDay = int(input('When is the start day?(ex: 16): '))

    EYear = int(input('When is the end year?(ex: 2023): '))
    EMonth = int(input('When is the end month?(ex: 11): '))
    EDay = int(input('When is the end day?(ex: 16): '))
    
    # SDate = datetime.date(input('When is the start date?(ex: 20220301)'))
    start = time.time()
    SDate = datetime.date(SYear, SMonth, SDay)
    EDate = datetime.date(EYear, EMonth, EDay)

    print("계좌번호 : ", bank_num)
    print("계좌 비밀번호 : ", birthday)
    print("생년월일 : ", password)
    print("조회 시작일 : ", SDate)
    print("조회 종료일 : ", EDate)

    trs = get_transactions(bank_num, birthday, password, SDate, EDate)
    print("결과값 데이터 타입 : ", type(trs))
    print("결과 값 : ", trs)
    end = time.time()
    print(f"{end - start:.5f} sec")

