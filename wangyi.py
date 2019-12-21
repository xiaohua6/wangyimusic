#
# http://music.163.com/song/media/outer/url?id=436514312.mp3，也可以直接通过这个连接直接获取mp3文件
import os
import re
import requests
import json
import jsonpath
import threading


class wangyi(object):
    def __init__(self,playlist):

        # self.sessions=requests.session()
    # 定义请求头
        self.headers={"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36",

                    "cookie":"_iuqxldmzr_=32; _ntes_nnid=becea385fac6ab9c4612887143499d20,1576721888799; _ntes_nuid=becea385fac6ab9c4612887143499d20; WM_NI=YQ3IH2hvPWNGPPtoSB6XMtfWOX818a7e4Eb%2BEUfe31L1FufQ%2Fn7aFkKggWpKnTHGzxemF%2B%2B7TykbVr7OwUHV82Ipf%2BoPlHBVRNJmUvH2SXyYwR5L4d%2Fyg6yHbnV3rCjdRmM%3D; WM_NIKE=9ca17ae2e6ffcda170e2e6eed3ec3b949f88bad848bb968ab3d14a969b9faef33ea5bfae96f673ac8f8abac22af0fea7c3b92a9b8ffdaacb3aacaaa0b8cd4d9490bc90d24af6888395e55d8d88f8d2bb6bf5bbfca6e121878baa86b23b90ef8a96e55bedb2f982c56189b9a9b8f341ae8c88a8f974a7b38accaa3d98a7a583d57af591b9b6cb5efcee8791e521ad90a4a9c15e9292868ed87e8cee9db9fc53b58efbadb770eda7a9d7fc44a2b29ad4f149aabc9e8ed037e2a3; WM_TID=M9ASxFsUO7ZFVQAAAQd5rkeb%2BkzkBQZW; playerid=37900165; JSESSIONID-WYYY=Ii%2BHKhbVHlXp6%5CeRfdUK7IP5%5C2F8yZ3TphAdljc46AZ3qY7RlgGOefihSpp3fKqY9fGav0qVKBTJ5Fa856iyfEKvnw%2FBR7z%2BfNKgGaakvbQu8R9yEGvxYJAeqC4%5C9utJPrD%2B%2BWpl7eV8%5C48JhbgQ2%2FBPrOkJtskfMJP5K6pkNaroYF2Y%3A1576743857871",

                  }
        self.playlist=playlist
    def get_playlist(self):
    # 获取歌单的url
        url='https://music.163.com/playlist?id=%s'%self.playlist

        # 启用session保持长连接

        result=requests.get(url,headers=self.headers)
        # 获取页面文本
        result=result.text
        # 根据正则获取歌曲id
        c=re.findall(r'<a href="/song\?id=(\d*?)">',result)
        # 获取歌曲名字
        name=re.findall(r'<a href="/song\?id=\d*?">(\w*?)</a>',result)
        # 只获取m4a文件
        c=c[0:len(name)]
        return c,name

    def paramas(self,a):

        # 生成params和encSecKey参数

        import execjs
        with open('wang.js', 'r', encoding='UTF-8') as f:
            exc = execjs.compile(f.read())

        sign = exc.call('d',a,'010001','00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7','0CoJUm6Qyw8W8jud')
        # print(sign)

        # print(sign['encSecKey'])
        data={
            "params": sign['encText'],
            "encSecKey":sign['encSecKey']

        }
        return data


    def get_song(self,song_id,name):


        a = '{"ids":"[%s]","level":"standard","encodeType":"aac","csrf_token":""}' % song_id

        data = self.paramas(a)
        # print(data)
        headers={

            "accept": "*/*",
            "content-type": "application/x-www-form-urlencoded",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "zh-CN,zh;q=0.9",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36",
            "origin": "https://music.163.com",
            "referer": "https://music.163.com/",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",

        }

        # 获取歌曲的url
        result=requests.post(url='https://music.163.com/weapi/song/enhance/player/url/v1?csrf_token=',headers=headers,data=data)

        c=json.loads(result.text)
        urls=jsonpath.jsonpath(c,'$..url')
        url=urls[0]


        try:
        # print(url)
            data=requests.get(url)

            # print(url)
            with open('./%s/%s.m4a'% (self.playlist,name),'wb') as f:
                f.write(data.content)
        except Exception:
            pass


    def start(self):

        n, name = self.get_playlist()

        i = 0
        while i<len(name):
            try:
                c=threading.Thread(target=self.get_song,args=(n[i],name[i]))
                c.start()

                if i%8==0:
                    # 等待此线程执行完在去创建新线程
                    c.join()
                i = i + 1
            except Exception:
                # 因为有的歌单歌曲已经下架所以要捕获空异常
                continue



if __name__ == '__main__':
    while True:
        playlist = input('请输入您要下载的网易云音乐歌单id,退出请输入no:')

        if playlist == "no" and not playlist.isdigit():
            playlist = "2916766519"

        if os.path.exists(playlist):
            print('此歌单已经存在')
            exit()
        path1 = os.getcwd()
        os.mkdir(path1 + '/' + playlist)


        try:
            c=wangyi(playlist)
            c.start()
        except:
            print('歌单id输入错误')
            break



