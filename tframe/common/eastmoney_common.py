import requests


class EastMoneyCommon:
    kUserAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

    def __init__(self):
        pass

    def GetHtml(self, url, cookies={}, params={}, headers={"user-agent": kUserAgent}):
        resp = requests.get(url, headers=headers, cookies=cookies, data=params)
        resp.encoding = "utf-8"
        return resp.text

    def PostHtml(self, url, cookies={}, params={}, headers={"user-agent": kUserAgent}):
        resp = requests.post(url, headers=headers, cookies=cookies, data=params)
        resp.encoding = "utf-8"
        return resp.text
