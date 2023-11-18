function maxLengthCheck(object){
  if(object.value.length > object.maxLength){
      object.value = object.value.slice(0, object.maxLength);
  }
}

function validatePassword(object) {
  object.value = object.value.replace(/[^0-9]/g,"");
}

$(document).ready(function() {
  $("#accountForm").submit(function(event) {
      // 폼이 실제로 제출되는 것을 막음
      event.preventDefault();

      // 사용자 입력값 수집
      var accountNum = $("#inputAccountNum").val();
      var accountPassword = $("#inputAccountPassword").val();

      // JavaScript의 Date 객체 사용
      var birth = new Date($("#inputBirth").val());

      // 생년월일을 990318 형식으로 가공
      var birthFormatted = (birth.getFullYear() % 100).toString().padStart(2, '0') +
          (birth.getMonth() + 1).toString().padStart(2, '0') +
          birth.getDate().toString().padStart(2, '0');

      // JavaScript의 Date 객체 사용
      
      var startDate = new Date($("#inputStartDate").val());
      var endDate = new Date($("#inputEndDate").val());

      // 날짜를 ISO 형식의 문자열로 변환
      birth = birthFormatted.toString();
      startDate = startDate.toISOString().split('T')[0];
      endDate = endDate.toISOString().split('T')[0];

      console.log("계좌번호 : ", accountNum);
      console.log("계좌 비밀번호 : ", accountPassword);
      console.log("생일 : ", birth);
      console.log("조회 시작일 : ", startDate);
      console.log("조회 종료일 : ", endDate);

      // Flask 서버로 데이터 전송
      $.ajax({
          type: "POST",
          url: "/inputAccountData",  // Flask 서버의 엔드포인트
          data: {
              accountNum: accountNum,
              accountPassword: accountPassword,
              birth: birth,
              startDate: startDate,
              endDate: endDate
          },
          success: function(response) {
              // 서버에서 받은 결과를 처리
              console.log(response);

              // 여기서는 예시로 콘솔에 결과를 출력함
              // 실제로는 원하는 대로 처리하면 됨
          },
          error: function(error) {
              console.log("Error:", error);
          }
      });
  });
});
