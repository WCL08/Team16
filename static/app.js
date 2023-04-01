async function showTabs() {
  $('.input-tabs-section').show();
  $('.tabs').show();
  $('.logout').hide();
}

async function showLogout() {
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
  // window.location.reload();
  listing();
}
async function hideAdmin(){
  $('.deleteButton').hide()
}
async function checkTokenExpiration() {
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
        // window.location.reload();
        listing();
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
        window.location.reload();
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

// 얘는 기존 거 지우면 안되는 거.
// $(document).ready(async function () {
//   // const token = await $.cookie('mytoken');
//   // await checkTokenExpiration();
//   let flag = await checking()
//   if (flag === true) {  // movie2에서는 f 면 크롤링해라였는데, 여기서는 true면 크롤링해라 이거임.
//     await crawling();
//     await listing();
    
//   } else {
//     await listing();
//   }


// 얘는 막 delete기능 사용해도 되는 거.
$(document).ready(async function () {
  // const token = await $.cookie('mytoken');
  await checkTokenExpiration();
  let flag = await checking()
  if (flag === "f") {  // movie2에서는 f 면 크롤링해라였는데, 여기서는 true면 크롤링해라 이거임.
    await crawling();
    await listing();
    
  } else {    // flag가 s면
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
  const token = await $.cookie('mytoken');
  await $("#cards-box").empty();
  let queue1 = await fetch("/movie")
  let queue2 = await queue1.json()
  let rows = await queue2["movie_list"]
  rows.forEach((a) => {
    let num = a["num"];
    let title = a["title"];
    let image = a["image"];
    let star_count = a["star"];
    let comment = a["comment"];
    let desc = a["desc"];
    let url = a["url"]
    console.log(typeof star_count); // >>> 여기서 star_count는 float 실수( 9.xx ) 형태임. CSS 공부해서 네이버처럼 10점 만점으로 9.8점이면 98%만 별 칠하던가, 그게 힘들면 소수점 덜어주려면 Math.floor 쓰던가 해야함. number 형태로 바꿔줘야 함.
    // star_count = Number(a["star"])
    
    let postBox = {
        "num": num,
        "title": title,
        "image": image,
        "star_count": star_count,
        "comment": comment,
        "desc": desc,
        "url": url
    }
    // --------------얘네 주석 처리 안했었음 ...;;--------------------
    // const myObject = { a:1 };   
    const queryParams = new URLSearchParams();
    queryParams.append('data', JSON.stringify(postBox));  // >>> data 에 담아서 넘기는 거.
    // window.location.href = '/review?' + queryParams.toString();
    let star = "⭐".repeat(star_count);
    // "/review?post=${postBox}"
    // src = "${image}" 가 아니라 그냥 src = ${image} 해도 오류 발생 안하네?!
    // 문제되면 이 밑에 jinja2 방식으로 서버로 넘길 때 문제임.
    // "window.location.href = '/review?'+ queryParams.toString()}"
    let temp_html = ` <div class="col">
                        <div class="card h-100">
                            <a href="/review?${queryParams.toString()}" >
                              <img src="${image}"
                                  class="card-img-top"/>
                              <div class="card-body">
                                <h5 class="card-title">${title}</h5>
                                <p class="card-text">${desc}</p>
                                <p class="mycomment">${comment}</p>
                              </div>
                            </a> 
                            <div class="right_bottom">     
                                <p class="rb_star">${star}</p>
                                <button onclick="delete_post(${num});" type="button" class="btn btn-outline-dark deleteButton rb_button">삭제하기</button>
                            </div>    
                        </div>
                    </div>`;
    $("#cards-box").append(temp_html);
  });
  if (token) {
    await showLogout();
  } else {
    await showTabs();
    await hideAdmin();
  };
}


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
          // window.location.reload()
          listing();
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

// function open_box() {
//   $('#post-box').show()
// }
// function close_box() {
//   $('#post-box').hide()
// }


