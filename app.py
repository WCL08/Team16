from bs4 import BeautifulSoup
import requests
import datetime
# import pyautogui
import time
import certifi
import json
# jwt 토큰, 패스워드 해쉬화
import jwt
import hashlib
#
from pymongo import MongoClient
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)


# 맥 유저들 안되면 이거 주석으로 바꾸세요.
# ca = certifi.where()
# client = MongoClient("mongodb+srv://sparta16:sparta16@cluster16.b0dkofq.mongodb.net/?retryWrites=true&w=majority", tlsCAFile = ca)
client = MongoClient(
    "mongodb+srv://sparta16:sparta16@cluster16.b0dkofq.mongodb.net/?retryWrites=true&w=majority")
db = client.movie
user_db = client.group_16 #유저 db

# 시크릿 키
SECRET_KEY = 'GROUP16' 

@app.route('/')
def home():
    return render_template('index.html')


@app.route("/movie/flag", methods=["GET"])
def flag_check():
    # flag 값 가져오기.(맨 처음에 비어있으면 True로 값 넣어줌. 이후부터는 False로 바꿔줌.)
    flagList = list(db.flag.find({}, {"_id": False}))
    if flagList == None or len(flagList) == 0:
        db.flag.insert_one({"flag": True})
        flagList = list(db.flag.find({}, {"_id": False}))
    else:
        flagList = list(db.flag.find({}, {"_id": False}))
    flag = flagList[-1]
    # print(flag)  ## 맨처음에는 무조건 {'flag': True}, 그 다음부터는 False로 영화 메인 화면에 포스팅 되는 거 막는 역할
    # 여기 밑에서  {"flag":{'flag': True}} 아니면 {"flag":{'flag': False}}이렇게 넘어감.
    return jsonify({"flag": flag})


@app.route("/movie", methods=["POST"])
def movie_crawl():
    ### ---------------------------------------랭크 크롤링 --------------------------------------------###
    # 오늘 날짜(아니면 특정 날짜 정해둬도 됨 => 요일 지날 때마다 계속 바뀜. 아예 날짜 한 날짜로 정하는게 좋을 듯)
    today = datetime.datetime.today()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}

    # lastPage = int(pyautogui.prompt("총 검색할 페이지 수를 입력하세요."))
    # 순위는 수동으로 지정했음. 아이디 클래스 태그 속성 심지어 위아래 태그까지 아예 똑같은데 값은 다른게 겹쳐 있어서 못 뽑음.
    # lastPage 가져올 페이지 입력(한 페이지당 50개)
    lastPage = 1
    rank = 0
    CrawlBox = []
    # starBox = []
    # urlBox = []
    for i in range(1, lastPage+1):
        # + str(i)
        url = f'https://movie.naver.com/movie/sdb/rank/rmovie.naver?sel=pnt&date={today}&page={i}'
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        name = soup.select('div.tit5')
        score = soup.select('td.point')
        link = soup.select("div.tit5 > a[href]")
        for n, s, l in zip(name, score, link):
            rank += 1

            # 오늘 가져온 것 확인(근데, rank, name 안 쓸 거. 확인하기 위한 코드)
            print(rank, n.text.strip(), s.text.strip(), l['href'], sep="\t"*2)

            # 별점 확인(실수 형태 9.xx)
            star = float(s.text.strip())
            print(star)  # <class 'float'>
            # starBox.append(star)

            # 코드 확인
            code = int(l['href'].split("=")[-1])
            print(code)  # <class 'int'>
            # urlBox.append(code)
            CrawlBox.append({"code": code, "star": star})

    ## -------------- 여기서 과부하 때문에 time.sleep(second) 쓸까 말까 고민됨. 포스트url 크롤링---------------##

    ### CrawlBox (안에 code = url랑, star = 점수) 가지고 이동해서 데이터 가져오기 ###
    docList = []
    for Crawl in CrawlBox:
        data = requests.get(
            f"https://movie.naver.com/movie/bi/mi/basic.naver?code={Crawl['code']}", headers=headers)
        soup = BeautifulSoup(data.text, 'html.parser')

        title = soup.select_one('meta[property="og:title"]')['content']
        image = soup.select_one('meta[property="og:image"]')['content']
        desc = soup.select_one('meta[property="og:description"]')['content']
        url = soup.select_one('meta[property="og:url"]')['content']
        comment = "테스트용 코멘트입니다. 주석필요"

        # --------------이 num이 각 포스터의 고유 인덱스이자 랭킹을 나타내는 숫자역할을 할 것임. 두 가지 역할을 하는 것. 예를 들어 포스터 삭제를 하거나 찜 등록을 할 때 이 num을 이용해서 등록할 것.--------------
        num = 1 if len(docList) == 0 else docList[-1]['num'] + 1
        docList.append({"num": num, "url": url, "title": title,
                       "image": image, "star": Crawl['star'], "desc": desc, "comment":comment})

    db.movie.insert_many(docList)

    # --------------다시 플래그 상태 바꿔서 영화 데이터 더 이상 못 불러오게 하기. --------------
    db.flag.update_one({"flag": True}, {"$set": {"flag": False}})
    flagList = list(db.flag.find({}, {"_id": False}))
    flag = flagList[-1]
    # print(flag) ## {'flag': False}
    return jsonify({"flag": flag})


@app.route("/movie", methods=["GET"])
def movie_get():
    movie_list = list(db.movie.find({}, {"_id": False}))
    return jsonify({"movie_list": movie_list})


@app.route("/movie/delete", methods=["POST"])
def movie_delete():
    num_receive = request.form["num_give"]
    # -----------fetch함수를 사용하여 서버로 넘어올 때는 데이터베이스에 넘어가기 직전의 JSON형태로 변환시켜주기 때문에 숫자는 문자화가 되서 넘어와진다. 그래서 int메서드로 다시 정수형으로 바꿔준다.------------
    # https://www.daleseo.com/js-json/ JSON 숫자 변형과 관련된 블로그
    num = int(num_receive)
    db.movie.delete_one({"num": num})
    return jsonify({'msg': "삭제 완료!"})


@app.route("/movie/edit", methods=["POST"])
def movie_edit():
    num_receive = request.form["num_give"]
    comment_receive = request.form["comment_give"]
    num = int(num_receive)
    db.movie.update_one({"num": num},{"$set",{"comment": comment_receive}})
    return jsonify({'msg': "수정 완료!"})

# 회원가입 
@app.route('/api/register', methods=['POST'])
def api_register():
	id_receive = request.form['id_give']
	pw_receive = request.form['pw_give']
	nickname_receive = request.form['nickname_give']

	existing_id = user_db.user.find_one({'id': id_receive})
	if existing_id:
		return jsonify({'result': 'error', 'msg': 'ID already exists'})
	existing_nickname = user_db.user.find_one({'nick': nickname_receive})
	if existing_nickname:
		return jsonify({'result': 'error', 'msg': 'Nickname already exists'})

	pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()
	user_db.user.insert_one({'id': id_receive, 'pw': pw_hash, 'nick': nickname_receive})
	return jsonify({'result': 'success'})

#로그인
@app.route('/api/login', methods=['POST'])
def api_login():
	id_receive = request.form['id_give']
	pw_receive = request.form['pw_give']
	pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()
	result = user_db.user.find_one({'id': id_receive, 'pw': pw_hash})

	if result is not None:
		payload = {
			'id': id_receive,
			'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30),
			'nickname': result['nick']
        }
		token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
		return jsonify({'result': 'success', 'token': token, 'nickname': result['nick']})
	else:
		return jsonify({'result': 'fail', 'msg': 'Incorrect ID or PW.'})

# @app.route('/page1')
# def review_get():
# 	data = request.args.get('data')
# 	return f'Url Data passed: {data}'

# ----------------------------------review page ---------------------------------------------------

@app.route("/review", methods=["POST"])
def review_post():
    star_receive = request.form['star_give']
    comment_receive = request.form['comment_give']
    nickname_receive= request.form['nickname_give']


    doc={
        'star':star_receive,
        'comment':comment_receive,
        'nickname':nickname_receive
    }

    db.review.insert_one(doc)
  
    return jsonify({'msg':'저장 완료!'})

# 이거도 일단 주석처리@@@
@app.route("/review/getcomment", methods=["GET"])
def review_get():
    all_reviews = list(db.review.find({},{'_id':False}))
    # return render_template('review.index.html')
    return jsonify({'result':all_reviews})

@app.route('/review/<string:nickname>', methods=['DELETE']) 
def nickname_del(nickname): 
    db.review.delete_one({'nickname': nickname}) 
    return jsonify({'msg': '삭제완료!'})

@app.route('/review')
def review_get_url_and_crawl():
    # data = request.args.get('data') / ?data=
    # myObject = json.loads(data) >>> object 형태 {} 가 됨.
    # url_receive = request.args.get('post')
    url_receive = request.args.get('post')  ## >>> Object 형태
    ul = json.loads(url_receive) 
    url_give = ul["url"]   ## >>> url
    ## 크롤링
    # all_reviews = list(db.review.find({},{'_id':False}))
    # url_receive = request.form['url_give']
    today = datetime.datetime.today()
    # url = url_receive
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    res = requests.get(url_give, headers= headers)
    soup = BeautifulSoup(res.text, 'html.parser')
    print(soup)
    g = soup.select_one('dl > div:nth-child(1) > dd') ## 영화 장르  
    o = soup.select_one('dl > div:nth-child(2) > dd') ## 영화 개봉일
    genre = g.text.split("")[0].strip()
    opening = o.text.strip()
    url_receive["genre"] = genre  ## 옵젝에 추가  
    url_receive["opening"] = opening
    # Box = {"genre": genre, "opening": opening}
    # for g, o in zip(genre, opening):
    #     print(g.text.strip(), o.text.strip(), sep="\t"*2)
    #     Box = {"genre": g.text.strip(), "opening": o.text.strip()}
    # return jsonify({'Box': Box})
    ## index.html 에서 post에 담아서 넘긴 객체
    # let postBox = {
    #                         "num": num,
    #                         "title": title,
    #                         "image": image,
    #                         "star_count": star_count,
    #                         "comment": comment,
    #                         "desc": desc,
    #                         "url": url
                            # "genre": genre, "opening": opening

    #                     }

    ## 여기에 크롤링이 오래 걸리지 않도록 딱 2개만 크롤링 빠르게 하도록
    ## 장르
    ## 오프닝

    ## postBox + 장르, 오프닝
    ## 얘네를 진자?방식으로 한꺼번에 넘긴다.
    return render_template('review.html', Box = url_receive)

# @app.route('/page1')
# def page1():
#     post = request.args.get('post')

#  ------------------------서버에서 review 들어가자마자 동시에 크롤링해서 jinja에 담아서 넘기기@@@------------------------------------ 
# @app.route("/review", methods=["POST"])
# def review_crawl():
#     # all_reviews = list(db.review.find({},{'_id':False}))
#     url_receive = request.form['url_give']
#     today = datetime.datetime.today()
#     url = url_receive
#     headers = {
#         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
#     res = requests.get(url, headers= headers)
#     soup = BeautifulSoup(res.text, 'html.parser')
#     print(soup)
#     genre = soup.select('dl > div:nth-child(1) > dd')
#     opening = soup.select('dl > div:nth-child(2) > dd')
#     # name = soup.select('div.tit5')
#     # score = soup.select('td.point')
#     # link = soup.select("div.tit5 > a[href]")
#     Box = {}
#     for g, o in zip(genre, opening):
#         print(g.text.strip(), o.text.strip(), sep="\t"*2)
#         Box = {"genre": g.text.strip(), "opening": o.text.strip()}
#     return jsonify({'Box': Box})


    # div.cm_content_wrap > div.cm_content_area._cm_content_area_info > div.cm_info_box > div.detail_info > dl > div:nth-child(1) > dd
    # div.cm_content_wrap > div.cm_content_area._cm_content_area_info > div.cm_info_box > div.detail_info > dl > div:nth-child(1) > dd

    # dl > div:nth-child(2) > dd
    # main_pack > div.sc_new.cs_common_module.case_empasis.color_16._au_movie_content_wrap > div.cm_content_wrap > div.cm_content_area._cm_content_area_info > div.cm_info_box > div.detail_info > dl > div:nth-child(2) > dd
    
    # main_pack > div.sc_new.cs_common_module.case_empasis.color_5._au_movie_content_wrap > div.cm_content_wrap > div.cm_content_area._cm_content_area_info > div.cm_info_box > div.detail_info > dl > div:nth-child(2) > dd

    

    ## 개요 - 장르 (컬러가 다름)
    # main_pack > div.sc_new.cs_common_module.case_empasis.color_5._au_movie_content_wrap > div.cm_content_wrap > div.cm_content_area._cm_content_area_info > div.cm_info_box > div.detail_info > dl > div:nth-child(1) > dd
    # main_pack > div.sc_new.cs_common_module.case_empasis.color_16._au_movie_content_wrap > div.cm_content_wrap > div.cm_content_area._cm_content_area_info > div.cm_info_box > div.detail_info > dl > div:nth-child(1) > dd
   

    ## 개봉일자
    # main_pack > div.sc_new.cs_common_module.case_empasis.color_5._au_movie_content_wrap > div.cm_content_wrap > div.cm_content_area._cm_content_area_info > div.cm_info_box > div.detail_info > dl > div:nth-child(2) > dd
    # main_pack > div.sc_new.cs_common_module.case_empasis.color_16._au_movie_content_wrap > div.cm_content_wrap > div.cm_content_area._cm_content_area_info > div.cm_info_box > div.detail_info > dl > div:nth-child(2) > dd

    

    #main_pack > div.sc_new.cs_common_module.case_empasis.color_5._au_movie_content_wrap > div.cm_content_wrap > div.cm_content_area._cm_content_area_info > div.cm_info_box > div.detail_info > dl > div:nth-child(2)
    #main_pack > div.sc_new.cs_common_module.case_empasis.color_5._au_movie_content_wrap > div.cm_content_wrap > div.cm_content_area._cm_content_area_info > div.cm_info_box > div.detail_info > dl > div:nth-child(2) > dd
    #  ------------------------------------------------------------   

    # @app.route('/page1')
    # def page1():
    #     post = request.args.get('post')






if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
