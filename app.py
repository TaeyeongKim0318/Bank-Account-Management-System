from flask import Flask, render_template, request, jsonify
from crawler import get_transactions
from datetime import datetime

app = Flask(__name__)


@app.route('/')
def formpage():
    return render_template('index.html')

@app.route('/inputAccountData', methods=['POST'])
def inputAccountData():
    # AJAX로부터 받은 데이터
    account_num = request.form.get("accountNum")
    account_password = request.form.get("accountPassword")
    birth = request.form.get("birth")
    start_date_str = request.form.get("startDate")
    end_date_str = request.form.get("endDate")

    # ISO 형식의 문자열을 datetime.date로 변환
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()

    print("계좌번호 : ", account_num)
    print("계좌 비밀번호 : ", account_password)
    print("생년월일 : ", birth)
    print("조회 시작일 : ", start_date)
    print("조회 종료일 : ", end_date)

    # crawler.py의 함수 호출
    result = get_transactions(account_num, account_password, birth, start_date, end_date)
    print(result)
    # 결과를 JSON 형식으로 반환
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)