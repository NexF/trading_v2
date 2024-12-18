import json
import logging

from lxml import etree

import tframe.common.eastmoney_common as common
from tframe.accontinfo.base_accontinfo import BaseAccountInfo, BasePosition
from tframe.session.eastmoney_session import EastMoneySession

_logger = logging.getLogger(__name__)


# 获取东财账户信息的类
class EastMoneyAccountInfo(BaseAccountInfo):
    # 东财账户信息获取api地址
    __kAccountInfoUrl = "https://jywg.eastmoneysec.com/Com/queryAssetAndPositionV1"
    # 东财validatekey获取api地址，这个地址今后可以改变
    __kValidateKeyUrl = "https://jywg.eastmoneysec.com/Search/Position"

    # 初始化
    def __init__(self, user, passwd):
        super().__init__(user, passwd)
        self.session = EastMoneySession(user, passwd).get_session()
        self.UpdateAccountInfo()
        # 获取初始总资产，用于计算总收益率
        self.__base_total_value = self.TotalValue()

    # 由于 session 会过期，需要定期更新登录状态
    def UpdateLogin(self):
        try:
            self.session = EastMoneySession(self.user, self.passwd).get_session()
            _logger.info(f"更新登录状态，session[{self.session}]")
        except Exception as e:
            _logger.error(f"更新登录状态失败，错误信息：{e}")
            self.session = None

    # 更新账户信息
    def UpdateAccountInfo(self):
        # 获取账户信息
        ret_json = common.GetHtml(self.__kAccountInfoUrl, cookies=self.session)
        self.account_info = json.loads(ret_json)
        _logger.info(f"get eastmoney accountinfo[{self.account_info}]")
        # 获取交易时需要的validatekey
        ret_html = common.GetHtml(self.__kValidateKeyUrl, cookies=self.session)
        doc = etree.HTML(ret_html)
        self.__validatekey = doc.xpath('//*[@id="em_validatekey"]/@value')[0]
        _logger.info(f"get eastmoney validatekey[{self.__validatekey}]")

    # 获取账户可用资金
    def AvailableCash(self):
        return self.account_info["Data"][0]["Kyzj"]

    # 获取账户持仓市值
    def PositionMarketValue(self):
        return self.account_info["Data"][0]["totalSecMkval"]

    # 获取账户总资产
    def TotalValue(self):
        return self.account_info["Data"][0]["Zzc"]

    # 获取账户持仓,返回持仓字典，key为证券代码，value为持仓对象
    def Position(self):
        position_dict = {}
        for position in self.account_info["Data"][0]["positions"]:
            position_dict[position["Zqdm"]] = EastMoneyPosition(position)
        return position_dict

    # 获取账户冻结资金
    def FrozenCash(self):
        return self.account_info["Data"][0]["Djzj"]

    # 获取账户当日盈亏
    def TodayProfit(self):
        return self.account_info["Data"][0]["Dryk"]

    # 获取账户持仓盈亏
    def PositionProfit(self):
        return self.account_info["Data"][0]["Ljyk"]

    # 获取账户总收益率
    def TotalReturnRate(self):
        return self.TotalValue() / self.__base_total_value


class EastMoneyPosition(BasePosition):
    def __init__(self, position_json: dict):
        self.position_json = position_json

    # 获取证券代码
    def StockId(self):
        return self.position_json["Zqdm"]

    # 获取证券名称
    def StockName(self):
        return self.position_json["Zqmc"]

    # 获取持仓数量
    def StockAmount(self):
        return self.position_json["Zqsl"]

    # 获取可卖数量
    def SellableAmount(self):
        return self.position_json["Kysl"]

    # 获取成本价
    def CostPrice(self):
        return self.position_json["Cbjg"]

    # 获取当前价
    def CurrentPrice(self):
        return self.position_json["Zxjg"]

    # 获取当前市值
    def MarketValue(self):
        return self.position_json["Zxsz"]

    # 获取持仓盈亏
    def Profit(self):
        return self.position_json["Ljyk"]

    # 获取持仓盈亏率
    def ProfitRate(self):
        return self.position_json["Ykbl"]

    # 获取当日盈亏
    def TodayProfit(self):
        return self.position_json["Dryk"]

    # 获取当日盈亏率
    def TodayProfitRate(self):
        return self.position_json["Drykbl"]
