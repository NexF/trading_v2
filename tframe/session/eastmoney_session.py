import asyncio
import json
from pyppeteer import launch
import logging
import ddddocr
from tframe.session.base_session import BaseSession
"""
初次安装pypeteer需要安装chromium依赖，可以看看
ldd ~/.local/share/pyppeteer/local-chromium/588429/chrome-linux/chrome | grep 'not found'
yum install libX11-devel nss pango.x86_64 libXcomposite.x86_64 libXcursor.x86_64 libXdamage.x86_64 libXext.x86_64 libXi.x86_64 libXtst.x86_64 cups-libs.x86_64 libXScrnSaver.x86_64 libXrandr.x86_64 GConf2.x86_64 alsa-lib.x86_64 atk.x86_64 gtk3.x86_64 -y
"""

class EastMoneySession(BaseSession):
    def __init__(self, user, passwd):
        super().__init__(user, passwd)
        self.ocr = ddddocr.DdddOcr(beta = True)
        self.url = 'https://jywg.eastmoneysec.com/Login'
        
    async def __login__(self):
        # 新建一个浏览器对象
        browser = await launch(options={'args': ['--no-sandbox', "--window-size=1920,1080"]})
        page = await browser.newPage()
        await page.setViewport({"width":1920,"height":1080})    # 页面长度，页面宽度
        await page.goto(self.url)                               # 转到login
        await page.type('#txtZjzh',self.user)                   # 设置账户，selector可以通过chrome开发者模式右键获取
        await page.type('#txtPwd',self.passwd)                  # 设置密码
        VaildImg = await page.xpath('//*[@id="imgValidCode"]')  # 得到验证码对象，通过xpath
        await VaildImg[0].screenshot({'path': 'yzm.png'})       # 验证码对象截图
        await page.click('#rdsc45')                             # 登录时长设为3小时

    
        with open("yzm.png", 'rb') as f:                        # 读取验证码，进行ocr
            image = f.read()
        res = self.ocr.classification(image)
        logging.info(f'验证码识别结果：{res}')

        await page.type('#txtValidCode', res)                   # 输入ocr得到的验证码

        await page.click('#btnConfirm')                         # 点击登录按钮
        await page.waitFor(1000)                                # 等待加载完成
        await page.screenshot({'path': 'example.png'})          
        

        if page.url != self.url:
            logging.warning('登录成功')
            ret = await page.cookies()
        else:
            logging.warning('登录失败，可能是验证码识别错误')
            ret = -1

        await browser.close()
        return ret
    
    def get_session(self):
        cookies = asyncio.get_event_loop().run_until_complete(self.__login__())
        return cookies
