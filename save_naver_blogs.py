# 나는 일상&일기 블로그 Data를 수집해보기로 했다!

from pymongo import MongoClient
from pymongo.errors import BulkWriteError

import json
import requests


def get_blogs(keywords, client_id, client_secret):
    """
    Naver 검색-블로그 api를 사용해서 특정 키워드에 대한 Blog 정보 수집
    :Params list keywords : 키워드 리스
    :Params str client_id : Api 사용 아이디
    :Params str client_pw : Api 사용 비밀번호
    :return blogs_items : Api 검색 결과 중 블로그 아이템들
    :rtype list
    """

    blog_items = []

    for keyword in keywords:
        url = "https://openapi.naver.com/v1/search/blog.json"
        sort = "date"
        display_num = 50
        start_num = 1

        params = {"query": keyword.encode("utf-8"), "display": display_num,
                  "start": start_num, "sort": sort}

        headers = {'X-Naver-Client-Id': client_id,
                   'X-Naver-Client-Secret': client_secret}
        r = requests.get(url, headers=headers, params=params)

        if r.status_code == requests.codes.ok:
            result_response = json.loads(r.content.decode('utf-8'))
            result = result_response["items"] #아이템만 수집!!
        else:
            print('request 실패!!')
            failed_msg = json.loads(r.content.decode('utf-8'))
            print(failed_msg)

        blog_items.extend(result)

    return blog_items


def save_to_DB(my_ip, username, password, db_name, collection_name, docs):
    """
    수집한 blog 정보들을 DB에 저장
    :Params str my_ip : 서버 공인 IP
    :Params str username : 서버 접속 ID
    :Params str password : 서버 접속 pw
    :Params str db_name : DB 이름
    :Params str collecion_name : 콜렉션 이름
    :Params list docs : 수집한 blog item 리스트

    """

    db_result = {'result': "success"}

    client = MongoClient(host=my_ip, port=27017,
                         username=username, password=password)

    db = client[db_name]
    collection = db[collection_name]

    collection.create_index([("link", 1)], unique=True)

    try:
        collection.insert_many(docs, ordered=False)

    except BulkWriteError as bwe:
        db_result["result"] = "insert and ignore duplictated data"

    return db_result

    # ========================입력 정보 중 개인 정보는 올리지 않도록 하겠습니다. =====================

    # naver api


client_id = '******'
client_secret = '******'

keywords = ["일상", "일기"]
docs = get_blogs(keywords, client_id, client_secret)

# print(docs)
# mongo DB

host = "******"
username = "*****"
password = "*****"

db_name = "likeyul"
collection_name = "naver_blogs"


result = save_to_DB(host, username, password, db_name, collection_name, docs)
# print(result)
