import logging
import json
import tframe.common.eastmoney_common as common
from lxml import etree
from tframe.accontinfo.base_accontinfo import BaseAccount, BasePosition, BaseOrder
from tframe.session.eastmoney_session import EastMoneySession
from datetime import datetime

class EastMoneyOrder(BaseOrder):
    def __init__(self, stock_id: str, amount: int, create_time: datetime, order_code: int, price: float = None):
        super().__init__(stock_id, amount, create_time, price)
        self.order_code = order_code


# 获取东财账户信息的类
class EastMoneyAccount(BaseAccount):
    # 东财账户信息获取api地址
    __kAccountInfoUrl = "https://jywg.eastmoneysec.com/Com/queryAssetAndPositionV1"
    # 东财validatekey获取api地址，这个地址今后可以改变
    __kValidateKeyUrl = "https://jywg.eastmoneysec.com/Search/Position"
    # 东财下单api地址
    __kTradeUrl = "https://jywg.eastmoneysec.com/Trade/SubmitTradeV2"

    # 初始化
    def __init__(self, user, passwd):
        super().__init__(user, passwd)
        self.init(user, passwd)

    def __init__(self):
        super().__init__()

    def init(self, user, passwd):
        self.user = user
        self.passwd = passwd
        self.session = EastMoneySession(user, passwd).get_session()
        self.UpdateAccountInfo()
        # 获取初始总资产，用于计算总收益率
        self.__base_total_value = self.TotalValue()

    # 由于 session 会过期，需要定期更新登录状态
    def UpdateLogin(self):
        try:
            self.session = EastMoneySession(self.user, self.passwd).get_session()
            logging.info(f"更新登录状态，session[{self.session}]")
        except Exception as e:
            logging.error(f"更新登录状态失败，错误信息：{e}")
            self.session = None

    # 更新账户信息
    def UpdateAccountInfo(self):
        # 获取账户信息
        ret_json = common.GetHtml(self.__kAccountInfoUrl, cookies = self.session)
        self.account_info = json.loads(ret_json)
        logging.info(f"get eastmoney accountinfo[{self.account_info}]")
        # 获取交易时需要的validatekey
        ret_html = common.GetHtml(self.__kValidateKeyUrl, cookies = self.session)
        doc = etree.HTML(ret_html)
        self.__validatekey = doc.xpath('//*[@id="em_validatekey"]/@value')[0]
        logging.info(f"get eastmoney validatekey[{self.__validatekey}]")

    # 获取账户可用资金
    def AvailableCash(self):
        return self.account_info['Data'][0]['Kyzj']

    # 获取账户持仓市值
    def PositionMarketValue(self):
        return self.account_info['Data'][0]['totalSecMkval']

    # 获取账户总资产
    def TotalValue(self):
        return self.account_info['Data'][0]['Zzc']

    # 获取账户持仓,返回持仓字典，key为证券代码，value为持仓对象
    def Position(self):
        position_dict = {}
        for position in self.account_info['Data'][0]['positions']:
            position_dict[position['Zqdm']] = EastMoneyPosition(position)
        return position_dict

    # 获取账户冻结资金
    def FrozenCash(self):
        return self.account_info['Data'][0]['Djzj']

    # 获取账户当日盈亏
    def TodayProfit(self):
        return self.account_info['Data'][0]['Dryk']

    # 获取账户持仓盈亏
    def PositionProfit(self):
        return self.account_info['Data'][0]['Ljyk']

    # 获取账户总收益率
    def TotalReturnRate(self):
        return self.TotalValue() / self.__base_total_value
    
    def Order(self, stock_id: str, amount: int, price: float = None) -> BaseOrder:
        stock_code = stock_id[:-3]
        
        if stock_id[-2:].upper() == "SH":
            market = "HA"
        elif stock_id[-2:].upper() == "SZ":
            market = "SA"
        else:
            raise ValueError(f"stock_id[{stock_id}]格式错误")
        
        params = {
            "stockCode": stock_code,
            "tradeType": "B" if amount > 0 else "S",
            "amount": abs(amount),
            "market": market
        }
        # 如果价格为None，则使用当前买1/卖1价格
        if price is None:
            if amount > 0:  # 买入
                price = common.GetFiveQuote(stock_id)['fivequote']['sale1']
            else:  # 卖出
                price = common.GetFiveQuote(stock_id)['fivequote']['buy1']
                
        params["price"] = price
        ret_json = common.PostHtml(self.__kTradeUrl,cookies = self.session, params=params)
        """{"Status":0,"Count":1,"Data":[{"Htxh":"0701195683","Wtbh":"1195683"}],"Errcode":0}"""
        if ret_json['Errcode'] == 0:
            return EastMoneyOrder(stock_id, amount, datetime.now(), ret_json['Data'][0]['Wtbh'], price)
        else:
            logging.error(f"下单失败，错误信息：{ret_json}")
            return None

    def OrderByValue(self, stock_id: str, cash_amount: float, price: float = None) -> BaseOrder:
        if price is None:
            if cash_amount > 0:  # 买入
                price = common.GetFiveQuote(stock_id)['fivequote']['sale1']
            else:  # 卖出
                price = common.GetFiveQuote(stock_id)['fivequote']['buy1']
        # 计算数量，100的整数倍，向下取整
        amount = int(cash_amount / price * 100) * 100
        if amount == 0:
            logging.error(f"下单失败：下单数量为 0. 价格[{price}]，金额[{cash_amount}]")
            return None
        return self.Order(stock_id, amount, price)

    def OrderByPercent(self, stock_id: str, percent: float, price: float = None) -> BaseOrder:
        if percent < 0 or percent > 1:
            logging.error(f"下单失败：百分比[{percent}]不在0到1之间")
            return None
        
        return self.OrderByValue(stock_id, self.TotalValue() * percent, price)

    def Rebalance(self, stock_id: str, amount: int, price: float = None) -> BaseOrder:
        
        return self.Order(stock_id, amount - self.Position()[stock_id].StockAmount(), price)
    
    def RebalanceByValue(self, stock_id: str, cash_amount: float, price: float = None) -> BaseOrder:
        return self.OrderByValue(stock_id, cash_amount - self.Position()[stock_id].StockAmount(), price)
    
    def RebalanceByPercent(self, stock_id: str, percent: float, price: float = None) -> BaseOrder:
        return self.OrderByPercent(stock_id, percent - self.Position()[stock_id].StockAmount(), price)

class EastMoneyPosition(BasePosition):
    def __init__(self, position_json: dict):
        self.position_json = position_json

    # 获取证券代码
    def StockId(self):
        return self.position_json['Zqdm']

    # 获取证券名称
    def StockName(self):
        return self.position_json['Zqmc']

    # 获取持仓数量
    def StockAmount(self):
        return self.position_json['Zqsl']
    
    # 获取可卖数量
    def SellableAmount(self):
        return self.position_json['Kysl']

    # 获取成本价
    def CostPrice(self):
        return self.position_json['Cbjg']

    # 获取当前价
    def CurrentPrice(self):
        return self.position_json['Zxjg']

    # 获取当前市值
    def MarketValue(self):
        return self.position_json['Zxsz']

    # 获取持仓盈亏
    def Profit(self):
        return self.position_json['Ljyk']

    # 获取持仓盈亏率
    def ProfitRate(self):
        return self.position_json['Ykbl']

    # 获取当日盈亏
    def TodayProfit(self):
        return self.position_json['Dryk']

    # 获取当日盈亏率
    def TodayProfitRate(self):
        return self.position_json['Drykbl']
