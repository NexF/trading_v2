import requests
from encodings.utf_8 import encode
import json

class EastMoneyCommon:
    kUserAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

    def __init__(self):
        pass

    def GetHtml(self, url, cookies = {}, params = {}, headers = {"user-agent": kUserAgent}):
        resp = requests.get(url,headers=headers, cookies=cookies, data = params)
        resp.encoding = 'utf-8'
        return resp.text

    def PostHtml(self, url, cookies = {}, params = {}, headers = {"user-agent": kUserAgent}):
        resp = requests.post(url,headers=headers, cookies=cookies, data = params)
        resp.encoding = 'utf-8'
        return resp.text
    
    # 获取五档行情
    # stock_id: 股票代码 如 600022.sh
    def GetFiveQuote(self, stock_id: str) -> dict:
        market = stock_id[-2:]
        stock_id = stock_id[:-3]
        url = f"https://emhsmarketwg.eastmoneysec.com/api/SHSZQuoteSnapshot?id={stock_id}&market={market}"
        resp = requests.get(url=url)
        resp.encoding = 'utf-8'
        return json.loads(resp.text)
