# coding=utf8
import base64
import hashlib
import json
import os

import itchat, time
import requests
from itchat.content import *
from pydub import AudioSegment


class bot:
    def __init__(self):
        self.xiaoice_id = None
        self.regist_groups = {}
        self.chat_queue = []
        self.last_replay = 0
        self.last_chat = 0

    def send_to_xiaoice(self):
        print(self.chat_queue)
        if len(self.chat_queue) > 0:
            item = self.chat_queue[0]
            try:
                if item['type'] == 'Picture':

                    itchat.send_image(item['msg'], self.xiaoice_id)
                elif item['type'] == 'ProductGif':
                    itchat.send_image(u'./bak/b.gif', self.xiaoice_id)
                else:
                    itchat.send(item['msg'], self.xiaoice_id)
            except:
                print("-" * 10)
                itchat.send_image(u'./bak/b.gif', self.xiaoice_id)

    def register(self):
        @itchat.msg_register([TEXT, PICTURE, RECORDING], isMpChat=True)
        def text_reply_xiaoice(msg):
            print('text_reply_xiaoice:', msg['Type'], msg['Content'], msg)
            if msg['FromUserName'] == self.xiaoice_id:
                now = time.time()
                double_replay = False
                if (now - self.last_replay <= 6 and msg['Type'] == 'Recording') or now - self.last_replay <= 2:
                    double_replay = True

                self.last_replay = now
                if len(self.chat_queue) > 0 or double_replay:
                    if double_replay:
                        item = self.last_chat
                    else:
                        item = self.chat_queue.pop(0)

                    self.last_chat = item

                    if item['target'] in self.regist_groups:
                        if msg['Type'] == 'Picture':
                            path = u"./imgs/%s" % msg['FileName']
                            msg['Text'](path)
                            itchat.send_image(path, item['target'])
                        elif msg['Type'] == 'Recording':
                            path = u"./records/%s" % msg['FileName']
                            msg['Text'](path)
                            itchat.send_file(path, item['target'])
                        else:
                            itchat.send(msg['Content'], item['target'])

                    if not double_replay:
                        self.send_to_xiaoice()

        # @itchat.msg_register([RECORDING], isFriendChat=True)
        # def text_reply_rec(msg):
        #     print "yuying", msg
        #     msg['Text'](msg['FileName'])
        #     print itchat.send_file(msg['FileName'], msg['FromUserName'])

        @itchat.msg_register([TEXT, PICTURE, RECORDING], isGroupChat=True, isFriendChat=True)
        def text_reply_group_txt(msg):
            print('text_reply_group_txt', msg)
            try:
                print ('GroupChat:', msg['Text'], msg['Content'], msg['FromUserName'])
            except:
                pass
            # print u'ActualNickName' in msg
            if msg['FromUserName'] != itchat.originInstance.storageClass.userName:
                if u'#小笋' in msg['Content']:
                    self.regist_groups[msg['FromUserName']] = 1
                    itchat.send(
                        u'小笋来啦，你可以直接在群里和我对话。\n我能看图片和表情，但是我听不懂语音，所以语音我都不会回复。\n\n如果不想聊了\n就对我说：#再见  \n这样我就不会再说话了。\n\n说：#小笋  \n我就又回来啦。',
                        msg['FromUserName'])
                elif u'#再见' in msg['Content'] and msg['FromUserName'] in self.regist_groups:
                    del self.regist_groups[msg['FromUserName']]
                elif msg['FromUserName'] in self.regist_groups:
                    if len(self.chat_queue) > 20:
                        self.chat_queue.pop(0)
                        return

                    # 图片
                    if msg['Type'] == 'Picture':
                        path = u"./imgs/%s" % msg['FileName']
                        if int(msg["HasProductId"]) == 1:
                            # 表情动画
                            self.chat_queue.append({
                                'msg': path,
                                'target': msg['FromUserName'],
                                'type': "ProductGif"
                            })
                        else:
                            # 普通图片
                            msg['Text'](path)
                            self.chat_queue.append({
                                'msg': path,
                                'target': msg['FromUserName'],
                                'type': msg['Type']
                            })
                    # 语音
                    elif msg['Type'] == 'Recording':
                        path = u"./records/%s" % msg['FileName']
                        ans = msg['Text'](path)
                        print("ans", ans, path)
                        ans_text = xf_audio(path)
                        if ans_text:
                            self.chat_queue.append({
                                'msg': ans_text,
                                'target': msg['FromUserName'],
                                'type': msg['Type']
                            })
                        else:
                            self.chat_queue.append({
                                'msg': "",
                                'target': msg['FromUserName'],
                                'type': "ProductGif"
                            })
                    # 其他文字
                    else:
                        self.chat_queue.append({
                            'msg': msg['Content'],
                            'target': msg['FromUserName'],
                            'type': msg['Type']
                        })

                    self.send_to_xiaoice()

                    # itchat.send('%s: %s' % (msg['Type'], msg['Text']), msg['FromUserName'])

                    # @itchat.msg_register([PICTURE, RECORDING, ATTACHMENT, VIDEO])
                    # def download_files(msg):
                    #     msg['Text'](msg['FileName'])
                    #     return '@%s@%s' % ({'Picture': 'img', 'Video': 'vid'}.get(msg['Type'], 'fil'), msg['FileName'])

                    # @itchat.msg_register(FRIENDS)
                    # def add_friend(msg):
                    #     itchat.add_friend(**msg['Text'])  # 该操作会自动将新好友的消息录入，不需要重载通讯录
                    #     itchat.send_msg('Nice to meet you!', msg['RecommendInfo']['UserName'])

                    # itchat.send(u'@%s\u2005I received: %s' % (msg['ActualNickName'], msg['Content']), msg['FromUserName'])

    def run(self):
        itchat.auto_login(enableCmdQR=2, hotReload=True)
        search_res = itchat.search_mps(name='小冰')
        print(json.dumps(search_res, indent=4))
        self.xiaoice_id = search_res[0]['UserName']
        self.register()
        itchat.run(debug=True)


abs_path = os.path.abspath(os.path.dirname(__file__))
print(abs_path)


def xf_audio(file_path):
    url = "http://api.xfyun.cn/v1/service/v1/iat"
    params = {
        "engine_type": "sms8k",
        "aue": "raw",
    }

    x_appid = '5bf512c4'
    api_key = 'd6951845261a0962b4e5952d199edebd'
    x_param = base64.b64encode(json.dumps(params).replace(' ', ''))
    x_time = str(int(int(round(time.time() * 1000)) / 1000))
    x_checksum = hashlib.md5(api_key + str(x_time) + x_param).hexdigest()
    x_header = {'X-Appid': x_appid,
                'X-CurTime': x_time,
                'X-Param': x_param,
                'X-CheckSum': x_checksum}
    sound = AudioSegment.from_mp3(file_path)
    sound.export(file_path + ".wav", format="wav")
    with open(file_path + ".wav", 'rb') as f:
        # print(f.read())
        res = base64.b64encode(f.read())
    data = {"audio": res}
    req = requests.post(url, headers=x_header, data=data)
    print('-' * 200)
    req.encoding = "utf8"
    print(req.text)

    try:
        res = req.json()
        if res["code"] == "0":
            return res["data"] or None
    except:
        pass

    return None


if __name__ == '__main__':
    bt = bot()
    bt.run()

    # xf_audio('./records/181121-171554.mp3')
