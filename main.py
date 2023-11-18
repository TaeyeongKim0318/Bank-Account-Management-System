import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QAbstractItemView, QHeaderView, QTableWidgetItem, QVBoxLayout, QApplication
from PyQt5 import QtCore, QtGui

from dateutil import relativedelta
from PyQt5.QtCore import QDate
from crawler import get_transactions

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvas as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

# UI파일 연결
main_class = uic.loadUiType(".//UI//bank_main_ui.ui")[0]

# 화면을 띄우는데 사용하는 class 선언
class SubWindow(QMainWindow):
    def __init__(self, deal_data):
        super().__init__()
        self.ui = uic.loadUi(".//UI//sub_window_ui.ui", self)
        self.show()
        # UI를 생성하기 위한 setupUi 메서드 호출
        self.initUI(deal_data)
    
    def initUI(self, deal_data):
        try:
            # 행 갯수 설정
            self.data_table.setRowCount(len(deal_data))
            # 열 갯수 설정
            self.data_table.setColumnCount(4)
            # 헤더 이름 저장
            column_headers = ['거래일시', '입출금금액', '잔액', '의뢰인/수취인']
            # 헤더 이름 설정
            self.data_table.setHorizontalHeaderLabels(column_headers)
            # 테이블 수정 금지
            self.data_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
            # 열 자동 늘리기
            self.data_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            # 행 자동 늘리기
            self.data_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
            # 크롤링한 데이터 key값 리스트에 저장
            deal_data_key = ['date', 'amount', 'balance', 'transaction_by']
            # 그래프로 그리기 위해 필요한 데이터만 담을 리스트 선언
            plot_data_list = []
            # 테이블 생성
            for idx, val in enumerate(deal_data):
                for i, v in enumerate(deal_data_key):
                    if (i == 0):
                        # 첫번째 셀에 데이터 삽입
                        self.data_table.setItem(idx, i, QTableWidgetItem(val[v].strftime("%Y-%m-%d, %H:%M:%S")))
                    elif (i == 1):
                        # 두번째 셀에 데이터 삽입
                        self.data_table.setItem(idx, i, QTableWidgetItem(str(val[v])))
                        # 그래프용 데이터로 리스트에 저장
                        plot_data_list.append(val[v])
                    elif (i == 2):
                        # 세번째 셀에 데이터 삽입
                        self.data_table.setItem(idx, i, QTableWidgetItem(str(val[v])))
                        # 네번째 셀에 데이터 삽입
                    else:
                        self.data_table.setItem(idx, i, QTableWidgetItem(val[v]))
        except Exception as e:
            print(e)
            QMessageBox.about(self,'테이블 생성 애러','테이블 생성 중 오류가 발생했습니다.\
                              \n다시 시도해주세요.')
        
        try:
            # Figure 함수 생성(그래프를 그리기 위한 함수)
            self.fig = plt.Figure()
            # 인스턴스에 FigureCanvas의 인스턴스 생성(pyqt5 위젯 위에 그림을 그리기 위한 도구)
            canvas = FigureCanvas(self.fig)
            
            # 레이아웃 생성
            # QVBoxLayout 모든 위젯을 수직으로 정렬
            layout2 = QVBoxLayout(self.data_graph)
            # 레이아웃에 FigureCanvas 추가
            layout2.addWidget(canvas)
            
            # 그래프 컨트롤바 추가
            self.addToolBar(NavigationToolbar(canvas, self.data_graph))
            # 그래프 영역 이미지 추가
            self.plt = canvas.figure.subplots()
            self.plt.cla()
            
            # 그래프 높이 설정
            bar_height = list(range(len(deal_data)))
            # 막대그래프 이미지 추가
            self.plt.bar(bar_height, plot_data_list)
        except Exception as e:
            print(e)
            QMessageBox.about(self,'그래프 생성 애러','그래프 생성 중 오류가 발생했습니다.\
                              \n다시 시도해주세요.')
        
        try:
            miner_money = 0
            plus_money = 0
            for i in plot_data_list:
                if i<0:
                    miner_money += i
                else:
                    plus_money += i
                
            self.MMoney.setText(str(miner_money)+ '원')
            self.PMoney.setText(str(plus_money)+ '원')
            self.TMoney.setText(str(sum(plot_data_list))+ '원')
        except Exception as e:
            print(e)
            QMessageBox.about(self,'입출금액 산출 애러','입출금액 산출 중 오류가 발생했습니다.\
                              \n다시 시도해주세요.')
                    

# 화면을 띄우는데 사용하는 class 선언
class MainWindow(QMainWindow, main_class):
    def __init__(self):
        # 기반 클래스 초기화
        super().__init__()
        # UI를 생성하기 위한 setupUi 메서드 호출
        self.setupUi(self)
        
        self.initUI()
        # inf_input 버튼이 클릭 되었을 때 btnClick이라는 함수 실행
        self.inf_input.clicked.connect(self.btnClick)
        self.one_day.clicked.connect(self.RadioBtnclick)
        self.one_month.clicked.connect(self.RadioBtnclick)
        self.three_month.clicked.connect(self.RadioBtnclick)
        self.six_month.clicked.connect(self.RadioBtnclick)
        
    def initUI(self):
        # 최초 화면에서 시작일 종료일 설정(당일로 설정)
        self.start_date.setDate(QDate.currentDate())
        self.end_date.setDate(QDate.currentDate())
        
        # 정규식 규칙 설정(글자수 제한 없이 숫자만 입력)
        re = QtCore.QRegExp("[0-9]*")
        self.acc_num.setValidator(QtGui.QRegExpValidator(re))
        self.acc_pw.setValidator(QtGui.QRegExpValidator(re))
        self.birth.setValidator(QtGui.QRegExpValidator(re))
    
    def RadioBtnclick(self):
        if self.one_day.isChecked():
            self.start_date.setDate(QDate.currentDate())
            self.end_date.setDate(QDate.currentDate())
            
        elif self.one_month.isChecked():
            next_month = self.end_date.date().toPyDate() - relativedelta.relativedelta(months=1)
            self.start_date.setDate(QDate(next_month.year, next_month.month, next_month.day))
        
        elif self.three_month.isChecked():
            next_month = self.end_date.date().toPyDate() - relativedelta.relativedelta(months=3)
            self.start_date.setDate(QDate(next_month.year, next_month.month, next_month.day))
        
        elif self.six_month.isChecked():
            next_month = self.end_date.date().toPyDate() - relativedelta.relativedelta(months=6)
            self.start_date.setDate(QDate(next_month.year, next_month.month, next_month.day))
            
            
        
    def btnClick(self):
        try:
            # 입력된 값 가져오기
            bank_acc = self.acc_num.text()
            bank_pw = self.acc_pw.text()
            usr_birth = self.birth.text()
            SDate = self.start_date.date().toPyDate()
            EDate = self.end_date.date().toPyDate()
            if ((len(bank_acc) == 14) and(len(bank_pw) == 4) and (len(usr_birth) == 6)):
                # 입력된 값 출력(확인 차)
                print('bank_acc\t', end = ' ')
                print(bank_acc)
                print('bank_pw\t\t', end = ' ')
                print(bank_pw)
                print('usr_birth\t', end = ' ')
                print(usr_birth)
                print('start_date\t', end = ' ')
                print(SDate)
                print('end_date\t', end = ' ')
                print(EDate)
                print()
                # 거래내역 크롤링 함수 실행
                deal_data = get_transactions(bank_acc, usr_birth, bank_pw, SDate, EDate)
                print('홈페이지 접속 완료')
            else:
                QMessageBox.about(self,'error','빈칸을 채워주세요.')
                return 0
            
        except Exception as e:
            print(e)
            QMessageBox.about(self,'접속 애러','홈페이지 접속에 오류가 발생했습니다.\
                              \n다시 시도해주세요.')
            return 0
        
        try:
            SubWindow(deal_data)
        except Exception as e:
            print(e)
            QMessageBox.about(self,'접속 애러','홈페이지 접속에 오류가 발생했습니다.\
                              \n다시 시도해주세요.')
            

                
            

if __name__ == "__main__":
    # QApplication:프로그램을 실행시켜주는 클래스
    app = QApplication(sys.argv)
    # MainWindow() 인스턴스 생성
    main_window = MainWindow()
    # 프로그램 화면을 보여주는 코드
    main_window.show()
    # 프로그램을 이벤트루프로 진입시키는(프로그램을 작동시키는) 코드
    # exec_()은 app이 종료되면 0을 return
    # return된 0은 sys.exit(0)로 받아 시스템이 종료된다.
    app.exec_()