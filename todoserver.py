from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json
import re

PORT = 8080

API = "api"
V1 = "v1"
EVENT = "event"

EVENT_KEY_DEADLINE = "deadline"
EVENT_KEY_TITLE = "title"

RESPONSE_KEY_STATUS = "status"
RESPONSE_KEY_MESSAGE = "message"

DATA_KEY_EVENTS = "events"
data = {
    DATA_KEY_EVENTS: []
}

# RFC3399 regular expression: https://mattallan.me/posts/rfc3339-date-time-validation/
REG_RFC3339 = r"^(\d{4})-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])T([01][0-9]|2[0-3]):([0-5][0-9]):([0-5][0-9]|60)?(\.[0-9]+)?(Z|(\+|-)([01][0-9]|2[0-3]):([0-5][0-9]))$"
reg_date_format = re.compile(REG_RFC3339)

class RequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        parsed_query, path_elements = self.parse_path()
        result = {}
        code = -1

        # APIチェック
        if (not self.is_valid_path(path_elements)):
            self.respond(404)
            return
        
        # 入力受け取り
        try:
            content_len = int(self.headers.get('content-length'))
            event = json.loads(self.rfile.read(content_len).decode('utf-8'))
        except Exception as e:
            print(e)
            self.respond(500)
            return

        # バリデーション後登録
        error_message = self.__validate_event(event)
        if (error_message == ""):
            # OK
            id = self.__register_event(event)
            result = {RESPONSE_KEY_STATUS: "success", RESPONSE_KEY_MESSAGE: "registered", "id": id}
            code = 200
        else:
            # Bad request
            result = {RESPONSE_KEY_STATUS: "failure", RESPONSE_KEY_MESSAGE: error_message}
            code = 400

        self.respond(code, result)
        return

    def do_GET(self):
        parsed_query, path_elements = self.parse_path()
        
        # APIチェック
        if (not self.is_valid_path(path_elements)):
            self.respond(404)
            return

        # idが指定されていれば個別，なければすべてを返す
        if(len(path_elements) > 3):
            try:
                id = int(path_elements[3])
                self.__get_event(int(path_elements[3]))
            except ValueError as e:
                # 数字以外がidとして指定されている場合
                print(e)
                self.respond(400)
        else:
            self.__get_all_event()
        return

    def parse_path(self):
        parsed_path = urlparse(self.path)
        parsed_query = parse_qs(parsed_path.query)
        path_elements = parsed_path.path.split('/')[1:]

        return parsed_query, path_elements
    
    def respond(self, code, dic = None):
        try:
            self.send_response(code)
            self.end_headers()
            if (dic != None):
                js = json.dumps(dic)
                self.wfile.write('{}\n'.format(js).encode('utf-8'))
        except Exception as e:
            print(e)
            self.send_response(500)
            self.end_headers()
        return
    
    def is_valid_path(self,path_elements):
        if (len(path_elements) < 3):
            return False
        return path_elements[:3] == [API, V1, EVENT]

    def __get_all_event(self):
        self.respond(200, data)
        return

    def __get_event(self, id):
        events = data[DATA_KEY_EVENTS]
        if (id < 0 or len(events) <= id):
            self.respond(404)
        else:
            self.respond(200, events[id])
        return
        
    def __validate_event(self, event):
        # 締切とタイトルの存在確認
        event_keys = event.keys()
        if ((EVENT_KEY_DEADLINE or EVENT_KEY_TITLE) not in event_keys):
            return "invalid event format"
        
        # 日付フォーマットの確認
        date = event[EVENT_KEY_DEADLINE]
        if(reg_date_format.match(date) == None):
            print(date)
            return "invalid date format"

        return ""

    def __register_event(self, event):
        events = data[DATA_KEY_EVENTS]
        id = len(events)
        event["id"] = id
        events.append(event)

        return id


def main():
    with HTTPServer(('', PORT), RequestHandler) as server:
        server.serve_forever()

if __name__ == "__main__":
    main()
