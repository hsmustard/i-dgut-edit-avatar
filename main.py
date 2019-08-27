# -*- encoding：utf-8 -*-
import requests
from lxml import etree
import time
import getpass
import random
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
}


def getCasToken(headers=None):
    if headers == None:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
        }
    requests.packages.urllib3.disable_warnings()
    r = requests.get(
        'https://cas.dgut.edu.cn/home/Oauth/getToken/appid/dgutApp', headers=headers, verify=False)
    html = etree.HTML(r.content)
    script = html.xpath('/html/body/script[7]')
    if len(script) == 0:
        raise RuntimeError('获取cas页面的token失败')
    tokenHtml = script[0].text
    tokenStart = tokenHtml.find('var token')
    cas_token = tokenHtml[tokenStart+13:tokenStart++13+32]
    print('csrf token:', cas_token)
    return cas_token, r.cookies.get_dict()


def getAccessToken(cookies, param, headers=None):
    if headers == None:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
            'Referer': 'https://cas.dgut.edu.cn/home/Oauth/getToken/appid/dgutApp'
        }
    requests.packages.urllib3.disable_warnings()
    r = requests.post(
        'https://cas.dgut.edu.cn/home/Oauth/getToken/appid/dgutApp', param, headers=headers, cookies=cookies, verify=False)
    # print(r.cookies)
    res =  (r.json())
    if (len(res) > 0) & ('code' in res.keys()):
        if res['code'] == 1:
            return res['info'][45:]
        if res['code'] == 23:
            param['wechat_verify'] = input('请输入微信验证码：')
            getAccessToken(cookies,param)
    else:
        raise RuntimeError(res['message'])


def getIDgutAccessToken(oauth_token,headers=None):
    if headers == None:
        headers = {
            'Content-Type': 'application/json',
            'Connection': 'keep-alive',
            'Accept': 'application/json',
            'User-Agent': 'ILoveDGUT/1.0.0 (iPhone iOS 12.4 Scale/2.00)',
            'Accept-Language': 'zh-Hans-CN'
        }
    device_id = random.sample('zyxwvutsrqponmlkjihgfedcba', 8)
    url = 'http://lgapp.dgut.edu.cn/api/cas/login?device_id=%s-1234-1234-1234-123456789111&device_title=ILoveDGUT&device_type=hsmus&token=%s' % (device_id[:8],oauth_token)
    r = requests.get(url,headers=headers)
    json = r.json()
    if (len(json) > 0) & ('code' in json.keys()):
        if (json['code'] == 200) & ('info' in json.keys()):
            return json['info']['access_token']
        else:
            raise RuntimeError('没有获取到i莞工access_token（code==200）')
    else:
        raise RuntimeError('没有收到i莞工access_token（code!==200）')
        
def getUserInfo(BearerToken):
    url = 'http://lgapp.dgut.edu.cn/api/getCurrentUserInfo'
    headers = {
        'Content-Type': 'application/json',
        'Connection': 'keep-alive',
        'Accept': 'application/json',
        'User-Agent': 'ILoveDGUT/1.0.0 (iPhone iOS 12.4 Scale/2.00)',
        'Accept-Language': 'zh-Hans-CN',
        'Authorization':BearerToken
    }
    r = requests.get(url,headers=headers)
    json = r.json()
    if json['code'] != 200:
        # print(json)
        raise RuntimeError(json['message']+'获取个人信息失败，也就是说明登录失败。。')
    else:
        return json['info']


def uploadImg(imgDir,BearerToken) :
    url = 'http://lgapp.dgut.edu.cn/api/home/uploadFile'
    headers = {
        'Connection': 'keep-alive',
        'Accept': 'application/json',
        'User-Agent': 'ILoveDGUT/1.0.0 (iPhone iOS 12.4 Scale/2.00)',
        'Accept-Language': 'zh-Hans-CN',
        'Authorization': BearerToken
    }
    fileName = time.strftime("%Y%m%d%H%M%S.jpg", time.localtime())
    files = {'file': (fileName, open(imgDir, 'rb'), 'image/jpeg',{})}
    # print(files)
    r = requests.post(url, files=files,headers=headers)
    json = r.json()
    if json['code'] != 200:
        # print(json)
        raise RuntimeError(json['message']+'，图片上传失败')
    else:
        # print(json)
        return json['info']['file_url']

def editAvatar(pic_url,BearerToken):
    url = 'http://lgapp.dgut.edu.cn/api/home/editLocalUserInfo'
    headers = {
        'Connection': 'keep-alive',
        'Accept': 'application/json',
        'User-Agent': 'ILoveDGUT/1.0.0 (iPhone iOS 12.4 Scale/2.00)',
        'Accept-Language': 'zh-Hans-CN',
        'Authorization': BearerToken
    }
    param = {'avatar':pic_url}
    r = requests.post(url, data=param, headers=headers)
    json = r.json()
    if json['code'] != 200:
        # print(json)
        raise RuntimeError(json['message']+'，头像修改失败。')
    else:
        return json['message']

if __name__ == '__main__':
    print('''
    **************************************
          欢迎使用 i 莞工 头像修改工具
            本工具所有请求均在本地发起
          不经过第三方服务器，请放心使用

    ======================================

           所有输入均以 **回车** 确认
               2019年8月27日
        
            ** 仅限学习交流使用 **
            ** 请勿用作其他用途 **
    ***************************************
    ''')
    username = input('请输入学号：')
    password = getpass.getpass('请输入密码(输入不可见，输入完成回车即可)：')
    if len(username) == 0 or len(password) == 0:
        raise RuntimeError('学号密码不能为空哦~') 
    cas_token, cookies = getCasToken()
    # print('token', cas_token, "\ncookies:", cookies)
    info = {'username': username, 
            'password': password,
            '__token__': cas_token, 
            'wechat_verify': ''}
    oauth_token = getAccessToken(cookies, info)
    print('''
    ******************************
    cas登录成功，正在换取token...
    ******************************
    ''')
    # print(oauth_token)
    Bearer = getIDgutAccessToken(oauth_token)
    print('''
    ******************************
    token换取成功，准备测试是否登录正常...
    ******************************
    ''')
    # print(Bearer)
    userInfo = getUserInfo(Bearer)
    print('*****登录正常******')
    print('==========================')
    print('您好，',userInfo['name'],"\n当前的头像地址是：",userInfo['avatar'])
    print('''

    ''')
    imgDir = input('请输入要上传的头像的文件地址(可直接用鼠标拖拽图片于此)：')
    # imgDir = r'C:\Users\张芥末\Desktop\Ws-8-hswimzy4458913.jpg'
    pic_url = uploadImg(imgDir,Bearer)
    print('上传图片的地址是：',pic_url)
    res = editAvatar(pic_url,Bearer)
    print(res,"\n\n头像修改成功，请退出i莞工重新登录查看！")


