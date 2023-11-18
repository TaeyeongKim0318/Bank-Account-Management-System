from io import StringIO, BytesIO
import base64
from PIL import Image
from PIL import ImageChops
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

import math, operator
from functools import reduce
import re
import os

def rmsdiff(im1, im2, im1_id, im2_id):
    # 이미지 두개를 비교하여 각 픽셀별로 얼마나 다른지 히스토그램으로 표현
    h = ImageChops.difference(im1, im2).histogram()
    
    # print('키패드에서 추출한 사진 순', end = ': ')
    # print(im1_id)
    # print('저장된 사진 숫자', end = ': ')
    # print(im2_id)
    # print()
    # result = math.sqrt(reduce(operator.add, map(lambda h, i: h * (i ** 2), h, range(256))) / (float(im1.size[0]) * im1.size[1]))
    # print(result)
    # return math.sqrt(reduce(operator.add, map(lambda h, i: h * (i ** 2), h, range(256))) / (float(im1.size[0]) * im1.size[1]))
    return math.sqrt(reduce(operator.add, map(lambda h, i: h * (i ** 2), h, range(256))) / (float(im1.size[0]) * im1.size[1]))


def _get_keypad_num_list(img):
    # 57x57 box
    # 미리 저장된 이미지를 불러온다.
    # 사이즈:57x57px
    # 경로(path):현재 파이썬 파일의 절대 경로 + assets
    box_5th = Image.open(os.path.join(CURRENT_PACKAGE_DIR, 'assets', '5.png'))
    # box_5th.show()
    box_7th = Image.open(os.path.join(CURRENT_PACKAGE_DIR, 'assets', '7.png'))
    # box_7th.show()
    box_8th = Image.open(os.path.join(CURRENT_PACKAGE_DIR, 'assets', '8.png'))
    # box_8th.show()
    box_9th = Image.open(os.path.join(CURRENT_PACKAGE_DIR, 'assets', '9.png'))
    # box_9th.show()
    box_0th = Image.open(os.path.join(CURRENT_PACKAGE_DIR, 'assets', '0.png'))
    # box_0th.show()

    # 딕셔너리에 각 버튼 이미지 저
    box_dict = {
        5: box_5th,
        7: box_7th,
        8: box_8th,
        9: box_9th,
        0: box_0th,
    }

    # 캡처했던 KB 마우스 입력기 이미지 좌표에 맞게 자르기
    # 해당 좌표값은 chrom devtool에서 확인 가능
    crop_5th = img.crop(box=(74, 99, 131, 156))
    # crop_5th.show()
    
    crop_7th = img.crop(box=(16, 157, 73, 214))
    # crop_7th.show()
    
    crop_8th = img.crop(box=(74, 157, 131, 214))
    # crop_8th.show()
    
    crop_9th = img.crop(box=(132, 157, 189, 214))
    # crop_9th.show()
    
    crop_0th = img.crop(box=(74, 215, 131, 272))
    # crop_0th.show()

    # 리스트에 자른 이미지 저장
    crop_list = [crop_5th, crop_7th, crop_8th, crop_9th, crop_0th]

    keypad_num_list = []

    #  
    # 참고: enumerate를 사용하여 리스트를 반복문으로 사용 할때 인덱스도 같이 사용할 수 있게 해줌
    for idx, crop in enumerate(crop_list):
        for key, box in box_dict.items():
            try:
                diff = rmsdiff(crop, box, idx, key)
                if diff < 62:
                    # 참고: key 자료형이 int이기 때문에 [key]로 생성
                    keypad_num_list += [key]
            except Exception as e:
                print(e)
    return keypad_num_list

########################################################################################################################



# 파이썬 파일의 절대 경로를 CURRENT_PACKAGE_DIR에 저장
CURRENT_PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_keypad_img():
    area_hash_list = []
    
    # 정규 표현식, 정규 표현식을 컴파일, 정규 표현식의 의미 문자열에 ''안에 들어있는 값이 숫자 혹은 문자를 반환한다.
    area_pattern = re.compile("'(\w+)'")
    
    # try ~ except 문 오류 처리문
    try:
        # 크롬 옵션 추가 headless 등 여러 속성 추가 가능
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('headless')
        # 드라이버 설치 현재 PC와 동일한 드라이버 자동 설치
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        
    except Exception as e:
        print("크롷 드라이버 설치 및 로드 중 오류가 발생했습니다.")
        print(e)
        print()
    
    
    # 크롬 사이즈 설정
    driver.set_window_size('1920', '1080')
    
    # 10초의 암묵적 대기 설정, 찾으려는 속성이 로드 될때까지 10초간 대기, 영구적용됨
    driver.implicitly_wait(10)
    # 해당 URL 브라우저에 띄우기
    driver.get('https://obank.kbstar.com/quics?page=C025255&cc=b028364:b028702&QSL=F')
    
    # 이름이 JSESSIONID인 쿠키를 가져온다. api 전송에 필요한 정보
    try:
        JSESSIONID = driver.get_cookie('JSESSIONID').get('value')
    except Exception as e:
        print('쿠키 JSESSIONID를 찾을 수 없습니다.')
        print(e)
        print()
        
    # 이름이 QSID인 쿠키를 가져온다. api 전송에 필요한 정보
    try:
        QSID = driver.get_cookie('QSID').get('value')
    except Exception as e:
        print('쿠키 QSID를 찾을 수 없습니다.')
        print(e)
    
    # KEYPAD_USEYN의 value 값을 가져온다. api 전송에 필요한 정보
    KEYPAD_USEYN = driver.find_element(By.CSS_SELECTOR, 'input[id*="KEYPAD_USEYN"]')
    
    # KB 마우스 입력기 css_selector 값 가져오기
    quics_img = driver.find_element(By.CSS_SELECTOR, 'img[src*="quics"]')
    
    # KB 마우스 입력기 각 버튼의 속성 값 list로 가져오기
    area_list = driver.find_elements(By.CSS_SELECTOR, 'map > area')
    
    
    # 각 버튼의 onmousedown, 즉 버튼을 눌렀을 때 작동하는 함수 가져오기
    for area in area_list:
        re_matched = area_pattern.findall(area.get_attribute('onmousedown'))
        # onmousedown에 값이 있을 경우 area_hash_list 에 저장
        if re_matched:
            area_hash_list.append(re_matched[0])
    
    # KB 마우스 입력기의 src값 추출
    img_url = quics_img.get_attribute('src')
    
    # KB 마우스 입력기의 usemap값 추출 후 #divKeypad를 제거
    keymap = quics_img.get_attribute('usemap').replace('#divKeypad', '')
    
    # 추출한 KB 마우스 입력기 src값을 이용하여 이미지를 브라우저에 띄운다
    driver.get(img_url)
    
    # 브라우저를 캡처 후 이미지 열어 screenshot 변수에 저장
    screenshot = Image.open(BytesIO(driver.get_screenshot_as_png()))
    
    # 이미지를 KB 마우스 입력기 사이즈에 맞게 잘라내기
    # real = screenshot.crop(box=(0, 0, 205, 336))
    real = screenshot.crop(box=(857.5, 372, 1062.5, 708))
    # real.show()
    
    # KB 마우스 입력기에서 랜덤으로 설정된 5, 7, 8, 9, 0의 순서 정렬
    # return type : list
    num_sequence = _get_keypad_num_list(real)
    
    # KB 마우스 입력기의 0 ~ 9 순서대로 정렬받기 위한 리스트
    PW_DIGITS = {}
    
    # 미리 저장한 onmousedown 값으로 1, 2, 3, 4, 6 값 정렬
    PW_DIGITS['1'] = area_hash_list[0]
    PW_DIGITS['2'] = area_hash_list[1]
    PW_DIGITS['3'] = area_hash_list[2]
    PW_DIGITS['4'] = area_hash_list[3]
    PW_DIGITS['6'] = area_hash_list[5]
    
    # 5, 6, 7, 8, 9 값 정렬
    for idx, num in enumerate(num_sequence):
        if idx == 0:
            PW_DIGITS[str(num)] = area_hash_list[4]
        elif idx == 1:
            PW_DIGITS[str(num)] = area_hash_list[6]
        elif idx == 2:
            PW_DIGITS[str(num)] = area_hash_list[7]
        elif idx == 3:
            PW_DIGITS[str(num)] = area_hash_list[8]
        elif idx == 4:
            PW_DIGITS[str(num)] = area_hash_list[9]
    
    return {
        'JSESSIONID': JSESSIONID,
        'QSID': QSID,
        'KEYMAP': keymap,
        'PW_DIGITS': PW_DIGITS,
        'KEYPAD_USEYN': KEYPAD_USEYN
    }





if __name__ == '__main__':
    print(get_keypad_img())
