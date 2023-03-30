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

$(document).ready(function () {
  const token = $.cookie('mytoken');
  checkTokenExpiration();
  if (token) {
    showLogout();
  } else {
    showTabs();
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
