function showTabs() {
  $('.input-tabs-section').show();
  $('.tabs').show();
  $('.logout').hide();
}

function showLogout() {
  $('.input-tabs-section').hide();
  $('.tabs').hide();
  $('.logout').show();
}

function onLogoutEvent() {
  $.removeCookie('mytoken');
  $('#reg-id').val('');
  $('#login-id').val('');
  $('#reg-pw').val('');
  $('#login-pw').val('');
  $('#reg-nick').val('');

  showTabs();
}

function checkTokenExpiration() {
  const token = $.cookie('mytoken');
  if (token) {

    const payload = JSON.parse(atob(token.split('.')[1]));
    $('.greeting').text('Welcome! ' + payload['nickname']);

    const expirationTime = payload.exp * 1000;
    if (Date.now() >= expirationTime) {
      onLogoutEvent();
      alert('Login Session Has Expired!');
    } else {
      setTimeout(checkTokenExpiration, expirationTime - Date.now());
    }
  } else {
    showTabs();
  }
}

function login() {
  $.ajax({
    type: "POST",
    url: "/api/login",
    data: { id_give: $('#login-id').val(), pw_give: $('#login-pw').val() },
    success: function (response) {
      if (response['result'] == 'success') {
        const token = response['token'];
        $.cookie('mytoken', token);

        $.ajaxSetup({
          headers: { 'Authorization': 'Bearer ' + token }
        });

        showLogout();
        $('.greeting').text('Welcome! ' + response['nickname']);
        checkTokenExpiration();
      } else {
        alert(response['msg'])
      }
    }
  })
}
function register() {
  const id = $('#reg-id').val().trim();
  const pw = $('#reg-pw').val().trim();
  const nickname = $('#reg-nick').val().trim();

  if (!id || !pw || !nickname) {
    alert('Please fill in all fields'); // 빈 문자열 확인
    return;
  }
  const idRegex = /^[a-zA-Z0-9_]+$/; //ID 특수문자 확인
  if (!idRegex.test(id)) {
    alert('올바른 ID를 입력하세요!');
    return;
  }
  const pwRegex = /^[a-zA-Z0-9!@#$%^&*()_+\-=[\]{};':"\\|,.<>/?]+$/;  // 패스워드 특수문자 확인
  if (!pwRegex.test(pw)) {
    alert('올바른 패스워드를 입력하세요!');
    return;
  }
  $.ajax({
    type: "POST",
    url: "/api/register",
    data: {
      id_give: $('#reg-id').val(),
      pw_give: $('#reg-pw').val(),
      nickname_give: $('#reg-nick').val()
    },
    success: function (response) {
      if (response['result'] == 'success') {
        alert('You have been registered!')
      } else {
        alert(response['msg'])
      }
    }
  })
}


window.addEventListener('load', function () {
  var button = document.getElementById("back-to-top-button");
  
  window.onscroll = function () {
    if (document.body.scrollTop > 50 || document.documentElement.scrollTop > 50) {
      button.style.display = "block";
    } else {
      button.style.display = "none";
    }
  };

  button.addEventListener('click', function () {
    requestAnimationFrame(function () {
      document.body.scrollTop = 0;
      document.documentElement.scrollTop = 0;
    });
  });
});

function getsomedata() {
  $.getJSON('/mydata', function (data) {
    // Handle the data here
    console.log(data);
  });
}

$(document).ready(async function () {
  const token = $.cookie('mytoken');
  checkTokenExpiration();
  let flag = await checking()
  if (token) {
    showLogout();
  } else {
    showTabs();
  }
  if (flag === true) {
    await crawling();
    await listing();
} else {
    await listing();
}

  $('.tab').eq(0).click(function () {
    $('#login-section').show();
    $('#register-section').hide();
    $('.tab').eq(0).addClass('active-tab');
    $('.tab').eq(1).removeClass('active-tab');
  });

  $('.tab').eq(1).click(function () {
    $('#register-section').show();
    $('#login-section').hide();
    $('.tab').eq(1).addClass('active-tab');
    $('.tab').eq(0).removeClass('active-tab');
  });
});

async function listing() {
  $("#cards-box").empty()
  fetch('/movie')
      .then((res) => res.json())
      .then((data) => {
          let rows = data["movie_list"]
          rows.forEach(a => {
              let num = a['num']
              let title = a["title"]
              let image = a["image"]
              let star_count = a["star"]
              let comment = a["comment"]
              let desc = a["desc"]
              console.log(typeof (star_count)) // >>> 여기서 star_count는 float 실수( 9.xx ) 형태임. CSS 공부해서 네이버처럼 10점 만점으로 9.8점이면 98%만 별 칠하던가, 그게 힘들면 소수점 덜어주려면 Math.floor 쓰던가 해야함. number 형태로 바꿔줘야 함.
              // star_count = Number(a["star"])

              let star = '⭐'.repeat(star_count)
              // src = "${image}" 가 아니라 그냥 src = ${image} 해도 오류 발생 안하네?!
              let temp_html = `<div class="col">
                                  <div class="card h-100">
                                      <img src=${image}
                                          class="card-img-top">
                                      <div class="card-body">
                                          <h5 class="card-title">${title}</h5>
                                          <p class="card-text">${desc}</p>
                                          <p>${star}</p>
                                          <p class="mycomment">${comment}</p>
                                          <button onclick="edit_comment(${num, comment})" type="button" class="btn btn-outline-dark">수정하기</button>
                                          <button onclick="delete_post(${num});" type="button" class="btn btn-outline-dark">삭제하기</button>
                                      </div>
                                  </div>
                              </div>`
              $("#cards-box").append(temp_html)
          });
      })
}
// 수정하기 버튼을 누르면 수정할 수 있는 칸이 나타나야 함.
// 현재 보여지는 comment 밑에 수정하기 부분은 display:none 으로 안보이게 했다가
// 수정하기 버튼을 누르면 나타나게 해야함.
// 수정하기 상위 블록은 display:none 했다가 javascript jquery로 버튼 누르면 클래스 붙이도록해서 display:block 이런 방향으로 가야 할 듯.

// --------------------------------------------------------------------------------------------
// flag 상태 체크 flag가 true면 포스팅이루어지고, flag가 false면 크롤링 또해서 재포스팅하는 현상 막음.
async function checking() {
  let flag;
  await fetch('/movie/flag')
      .then((res) => res.json())
      .then((data) => {
          console.log(data)
          flag = data["flag"]
          console.log(data)
          flag = data["flag"]["flag"]
      })
  return flag
}

// --------------------------------------------------------------------------------------------
// 크롤링
async function crawling() {
  let test = "test start"
  console.log("test start")
  let formData = new FormData();
  formData.append("test_give", test)

  await fetch('/movie', { method: "POST", body: formData })
      .then((res) => res.json())
      .then((data) => {
          console.log(data)
          window.location.reload()
      })
      .catch((error) => console.log(error));
}

// --------------------------------------------------------------------------------------------
// 포스트별 고유 num 찾아서 포스트 삭제
function delete_post(num) {
  let formData = new FormData();
  formData.append("num_give", num)

  fetch('/movie/delete', { method: "POST", body: formData })
      .then((res) => res.json())
      .then((data) => {
          console.log(data)
          alert(data['msg'])
          window.location.reload()
      })
      .catch((error) => {
          console.log("delete failed: ", error)
      })
}
// --------------------------------------------------------------------------------------------
function edit_comment(num, comment) {
  let formData = new FormData();
  formData.append("num_give", num)
  formData.append("comment_give", comment)

  fetch('/movie/edit', { method: "POST", body: formData })
      .then((res) => res.json())
      .then((data) => {
          console.log(data)
          alert(data['msg'])
          window.location.reload()
      })
      .catch((error) => {
          console.log("edit failed: ", error)
      })
}

function open_box() {
  $('#post-box').show()
}
function close_box() {
  $('#post-box').hide()
}


