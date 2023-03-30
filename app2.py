from bs4 import BeautifulSoup
import requests
import datetime
# import pyautogui
import time
import certifi
from pymongo import MongoClient
from flask import Flask, render_template, request, jsonify
from bson import json_util
import json
app = Flask(__name__)


## 맥 유저들 안되면 이거 주석으로 바꾸세요.
# ca = certifi.where()
# client = MongoClient("mongodb+srv://sparta16:sparta16@cluster16.b0dkofq.mongodb.net/?retryWrites=true&w=majority", tlsCAFile = ca)
client = MongoClient("mongodb+srv://sparta16:sparta16@cluster16.b0dkofq.mongodb.net/?retryWrites=true&w=majority")

# db = client.movie    이거 테스트하려고 잠굼.
db = client.movie2

@app.route('/')
def home():
    return render_template('index6.html')


@app.route("/movie/flag", methods=["GET"])
def Flag_get():
    time.sleep(1)
    # flag 값 가져오기.(맨 처음에 비어있으면 f로 값 넣어줌. 이후부터는 s로 바꿔줌.)
    flagList = list(db.flag.find({},{"_id":False}))
    flag = None
    # dumps() 함수: Python 객체를 JSON 문자열로 변환 // 문제 발생 예상 지역.!!!!
    if flagList == None or len(flagList)== 0:
        flag = {"flag":False}
    else:
        flagList = list(db.flag.find({},{"_id":False}))
        flag = flagList[-1]
    # print(flag)  ## 맨처음에는 무조건 {'flag': f}, 그 다음부터는 s로 영화 메인 화면에 포스팅 되는 거 막는 역할
    ## 여기 밑에서  {"flag":{'flag': f}} 아니면 {"flag":{'flag': s}}이렇게 넘어감.
    return jsonify({"flag": flag})

# def Flag_get():
#     # flag 값 가져오기.(맨 처음에 비어있으면 f로 값 넣어줌. 이후부터는 s로 바꿔줌.)
#     flagList = list(db.flag.find({},{"_id":False}))
#     if flagList == None or len(flagList)==0 :
#         db.flag.insert_one({"flag":"f"})
#         flagList = list(db.flag.find({},{"_id":False}))
#     else:
#         flagList = list(db.flag.find({},{"_id":False}))
#     flag = flagList[-1]
#     # print(flag)  ## 맨처음에는 무조건 {'flag': f}, 그 다음부터는 s로 영화 메인 화면에 포스팅 되는 거 막는 역할
#     ## 여기 밑에서  {"flag":{'flag': f}} 아니면 {"flag":{'flag': s}}이렇게 넘어감.
#     return jsonify({"flag": flag})

@app.route("/movie/init", methods=["GET"])
def flag_init():
    ## f로 바꿔줘서 돌아갈 수 있게
    db.flag.drop()
    db.flag.insert_one({"flag":"f"})
    return jsonify({"msg": "성공"})

@app.route("/movie/lotate", methods=["GET"])
def flag_lotate():
    ## s로 바꿔줘서 돌아갈 수 있게
    db.flag.drop()
    db.flag.insert_one({"flag":"s"})
    return jsonify({"msg": "성공"})


@app.route("/movie/sort", methods=["GET"])
def sort_get():
    ## 이게 초기 세팅이지 맨처음에 무조건 cur 보이게
    sortList = list(db.sort.find({},{"_id":False}))
    if sortList == None or len(sortList)==0:
        db.sort.insert_one({"sort": "cur"})
    sortList = list(db.sort.find({},{'_id':False}))
    sort = sortList[-1] 
    # {"sort":{'sort': "랭크종류"}}
    return jsonify({"sort": sort})


@app.route("/movie/sort", methods=["POST"])
def sort_change():
    sort_receive = request.form["sort_give"]
    ## 맨 처음에 무조건 cur보이도록 해주는 기능
    ## 무조건 맨 처음에는 Cur 페이지 보여주게
    ## 이거 나중에 프론트앤드 부분에서 버튼에 POST 방식 넣어서 누르 버튼에 맞춰서 페이지 바뀌도록 해줘야겠다.
    ## 초기로딩 cur // 맨 처음이라면 => flag가 아예 없다면.
    # sortList = list(db.sort.find({},{"_id":False}))
    # if sortList == None or len(sortList)==0:
    #     db.sort.insert_one({"sort": "cur"})
    # else:
    #     db.sort.update_one({"sort": "cur"}, {"$set":{"sort": sort_receive}})
    # 컬렉션 드랍.
    db.sort.drop() 
    db.sort.insert_one({"sort": sort_receive})
    # db.sort.update_one({"sort": "cur"}, {"$set":{"sort": sort_receive}})
    sortList = list(db.sort.find({},{'_id':False}))
    sort = sortList[-1] 
    # {"sort":{'sort': "랭크종류"}}
    return jsonify({"sort": sort})





## 안되면 여기 크롤링 3부분으로 다 가르자.
@app.route("/movie/crawl", methods=["POST"])
def movie_crawl():
    selBox = ["cur", "cnt", "pnt"]
    lastPage = 1
    today = datetime.datetime.today()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    CrawlCurBox = []
    CrawlCntBox = []
    CrawlPntBox = []
    totalBox = []
    docCurList = []
    docCntList = []
    docPntList = []
    flagList = list(db.flag.find({},{"_id":False}))
    if flagList == None or len(flagList)==0:
        ### ---------------------------------------랭크 크롤링 --------------------------------------------###
        # 오늘 날짜(아니면 특정 날짜 정해둬도 됨 => 요일 지날 때마다 계속 바뀜. 아예 날짜 한 날짜로 정하는게 좋을 듯)
        # lastPage = int(pyautogui.prompt("총 검색할 페이지 수를 입력하세요."))
        # 순위는 수동으로 지정했음. 아이디 클래스 태그 속성 심지어 위아래 태그까지 아예 똑같은데 값은 다른게 겹쳐 있어서 못 뽑음.
        # lastPage 가져올 페이지 입력(한 페이지당 50개)
        # selBox 순서:: 평점순(현재상영영화), 조회순, 평점순(모든영화)
            # for i in range(1, lastPage+1):
        for i in range(1):
            url = f'https://movie.naver.com/movie/sdb/rank/rmovie.naver?sel=cur&date={today}'
            # url = f'https://movie.naver.com/movie/sdb/rank/rmovie.naver?sel={sel}&date={today}&page={i}'
            res = requests.get(url, headers=headers)
            soup = BeautifulSoup(res.text, 'html.parser')
            name = soup.select('div.tit5')
            score = soup.select('td.point')
            link = soup.select("div.tit5 > a[href]")
            rank = 0
            for n, s, l in zip(name, score, link):
                rank += 1

                # 오늘 가져온 것 확인(근데, rank, name 안 쓸 거. 확인하기 위한 코드)
                print(rank, n.text.strip(), s.text.strip(), l['href'], sep="\t"*2)

                # 별점 확인(실수 형태 9.xx)
                star = float(s.text.strip())
                print(star) #<class 'float'>
                # starBox.append(star)

                # 코드 확인
                code = int(l['href'].split("=")[-1])
                print(code) #<class 'int'>
                # urlBox.append(code)
                CrawlCurBox.append({"code": code, "star": star})
        for i in range(1):
            url = f'https://movie.naver.com/movie/sdb/rank/rmovie.naver?sel=cnt&date={today}'
            # url = f'https://movie.naver.com/movie/sdb/rank/rmovie.naver?sel={sel}&date={today}&page={i}'
            res = requests.get(url, headers=headers)
            soup = BeautifulSoup(res.text, 'html.parser')
            name = soup.select('div.tit3')
            # score = soup.select('td.point') # 점수 없음.
            link = soup.select("div.tit3 > a[href]")
            rank = 0
            for n, l in zip(name, link):
                rank += 1

                # 오늘 가져온 것 확인(근데, rank, name 안 쓸 거. 확인하기 위한 코드)
                # print(rank, n.text.strip(), s.text.strip(), l['href'], sep="\t"*2)
                print(rank, n.text.strip(), l['href'], sep="\t"*2)

                # # 별점 확인(실수 형태 9.xx)
                # star = float(s.text.strip())
                # print(star) #<class 'float'>
                # # starBox.append(star)

                # 코드 확인
                code = int(l['href'].split("=")[-1])
                print(code) #<class 'int'>
                # urlBox.append(code)
                CrawlCntBox.append({"code": code})
                # CrawlCntBox.append({"code": code, "star": star})
        for i in range(1):
            ## 일단은 1페이지만
            url = f'https://movie.naver.com/movie/sdb/rank/rmovie.naver?sel=pnt&date={today}'
            # url = f'https://movie.naver.com/movie/sdb/rank/rmovie.naver?sel={sel}&date={today}&page={i}' ## 번호 넣었을 땐 안됐음. 맨처음 페이지는 맨처음 접속은 번호가 없긴 하던데 그거 때문인가.
            res = requests.get(url, headers=headers)
            soup = BeautifulSoup(res.text, 'html.parser')
            name = soup.select('div.tit5')
            score = soup.select('td.point')
            link = soup.select("div.tit5 > a[href]")
            rank = 0
            for n, s, l in zip(name, score, link):
                rank += 1

                # 오늘 가져온 것 확인(근데, rank, name 안 쓸 거. 확인하기 위한 코드)
                print(rank, n.text.strip(), s.text.strip(), l['href'], sep="\t"*2)

                # 별점 확인(실수 형태 9.xx)
                star = float(s.text.strip())
                print(star) #<class 'float'>
                # starBox.append(star)

                # 코드 확인
                code = int(l['href'].split("=")[-1])
                print(code) #<class 'int'>
                # urlBox.append(code)
                CrawlPntBox.append({"code": code, "star": star})
 
  
        totalBox.append(CrawlCurBox)
        totalBox.append(CrawlCntBox)
        totalBox.append(CrawlPntBox)
        

        for sort in totalBox:
            for Crawl in sort:
                data = requests.get(f"https://movie.naver.com/movie/bi/mi/basic.naver?code={Crawl['code']}", headers=headers)
                soup = BeautifulSoup(data.text, 'html.parser')

                title = soup.select_one('meta[property="og:title"]')['content']
                image = soup.select_one('meta[property="og:image"]')['content']
                desc = soup.select_one('meta[property="og:description"]')['content']
                url = soup.select_one('meta[property="og:url"]')['content']
                ## --------------이 num이 각 포스터의 고유 인덱스이자 랭킹을 나타내는 숫자역할을 할 것임. 두 가지 역할을 하는 것. 예를 들어 포스터 삭제를 하거나 찜 등록을 할 때 이 num을 이용해서 등록할 것.--------------
                if totalBox.index(sort) == 0:
                    num = 1 if len(docCurList) == 0 else docCurList[-1]['num'] + 1
                    docCurList.append({"num": num, "url": url, "title": title, "image": image, "star": Crawl['star'], "desc": desc, "comment":""})
                elif totalBox.index(sort) == 1:
                    ## 조회순에는 평점 없음.
                    num = 1 if len(docCntList) == 0 else docCntList[-1]['num'] + 1
                    docCntList.append({"num": num, "url": url, "title": title, "image": image,  "desc": desc, "comment":""})
                elif totalBox.index(sort) == 2:
                    num = 1 if len(docPntList) == 0 else docPntList[-1]['num'] + 1
                    docPntList.append({"num": num, "url": url, "title": title, "image": image, "star": Crawl['star'], "desc": desc, "comment":""})
        ## 데이터베이스 오타 수정했음.
        db.moviecur.insert_many(docCurList)
        db.moviecnt.insert_many(docCntList)
        db.moviepnt.insert_many(docPntList)

    # --------------다시 플래그 상태 바꿔서 영화 데이터 더 이상 못 불러오게 하기. --------------
    else:
        db.flag.drop()

    db.flag.insert_one({"flag":"s"})
    # db.flag.update_one({"flag": "f"}, {"$set":{"flag": "s"}})
    flagList = list(db.flag.find({},{"_id":False}))
    flag = flagList[-1]
    # print(flag) ## {"flag":{'flag': "s"}}
    # db.flag.insert_one({"flag":"s"})
    return jsonify({"flag": flag})


@app.route("/movie/list", methods=["POST"])
def movie_get():
    sort_receive = request.form["sort_give"]
    repository = "movie" + sort_receive
    movie_list = list(db[repository].find({}, {"_id": False}))
    return jsonify({"movie_list": movie_list})

@app.route("/movie/cur", methods=["GET"])
def moviecur_get():
    movie_list = list(db.moviecur.find({},{"_id":False}))
    return jsonify({"movie_list": movie_list})

@app.route("/movie/cnt", methods=["GET"])
def moviecnt_get():
    movie_list = list(db.moviecnt.find({},{"_id":False}))
    return jsonify({"movie_list": movie_list})

@app.route("/movie/pnt", methods=["GET"])
def moviepnt_get():
    movie_list = (db.moviepnt.find({},{"_id":False}))
    return jsonify({"movie_list": movie_list})

# @app.route("/movie", methods=["GET"])
# def movie_get():
#     movie_list = list(db.movie.find({}, {"_id": False}))
#     return jsonify({"movie_list": movie_list})


@app.route("/movie/delete", methods=["POST"])
def movie_delete():
    num_receive = request.form["num_give"]
    ## -----------fetch함수를 사용하여 서버로 넘어올 때는 데이터베이스에 넘어가기 직전의 JSON형태로 변환시켜주기 때문에 숫자는 문자화가 되서 넘어와진다. 그래서 int메서드로 다시 정수형으로 바꿔준다.------------
    ## https://www.daleseo.com/js-json/ JSON 숫자 변형과 관련된 블로그
    num = int(num_receive)
    db.movie.delete_one({"num": num})
    return jsonify({'msg': "삭제 완료!"})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)