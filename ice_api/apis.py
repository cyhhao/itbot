# coding=utf-8
import json

from itBot.ice_api.http import base
from pyquery import PyQuery as pq


class apis(base):
    def __init__(self, headers=None):
        if headers is None:
            headers = {
                'X-Requested-With': 'XMLHttpRequest',
                'Origin': 'http://webapps.msxiaobing.com',
                'Referer': 'http://webapps.msxiaobing.com/simplechat'
            }
        base.__init__(self, headers)
        self.init()

    def init(self):
        self.get('/simplechat')

    def sendText(self, text):
        res = self.getresponse(text, '')

    def getresponse(self, text, image):
        url = '/simplechat/getresponse'
        data = {
            "SenderId": "123",
            "Content": {
                "Text": text,
                "Image": image
            }
        }
        res = self.post(url, data)

        self.parser(res)

    def parser(self, html):
        print(html)
        doc = pq(html)
        json_text = doc('#xb_responses').attr('data-json')

        print( '-' * 20)

        res_list = json.loads(json_text)


        # print doc('.xb_conv_left').text()


if __name__ == '__main__':
    api = apis()
    api.sendText('我爱猜歌词')
