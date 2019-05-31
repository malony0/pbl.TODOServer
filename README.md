# pbl.TODOServer

[![CircleCI](https://circleci.com/gh/malony0/pbl.TODOServer/tree/master.svg?style=svg)](https://circleci.com/gh/malony0/pbl.TODOServer/tree/master)

PBLのレポート課題: TODO管理サービス用の簡易なHTTPサーバ

---

## 概要

- TODOイベントをPOSTで登録しGETで取得できるHTTPサーバ
- データのやり取りはJSONで行う
- ローカルホスト，ポートは8080

## API

### イベント登録

イベントの要素には`deadline`と`title`のみ必須．あとは任意

```
# イベント登録 API request
POST /api/v1/event
{"deadline": "2019-06-11T14:00:00+09:00", "title": "レポート提出", "memo": ""}

# イベント登録 API response
200 OK
{"status": "success", "message": "registered", "id": 1}

400 Bad Request
{"status": "failure", "message": "invalid date format"}
```

### イベント取得

イベントのidは0から順に振られる

```
# イベント全取得 API request
GET /api/v1/event

#イベント全取得 API response
200 OK
{"events": [
    {"id": 1, "deadline": "2019-06-11T14:00:00+09:00", "title": "レポート提出", "memo": ""},
    ...
]}
```

```
#イベント1件取得 API request
GET /api/v1/event/${id}

#イベント1件取得 API response
200 OK
{"id": 1, "deadline": "2019-06-11T14:00:00+09:00", "title": "レポート提出", "memo": ""}

404 Not Found
```