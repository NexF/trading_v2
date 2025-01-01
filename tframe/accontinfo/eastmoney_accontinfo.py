import logging
import json
import tframe.common.eastmoney_common as common
from lxml import etree
from tframe.accontinfo.base_accontinfo import BaseAccount, BasePosition, BaseOrder, OrderStatus
from tframe.session.eastmoney_session import EastMoneySession
from datetime import datetime, timedelta

# 订单集合
class EastMoneyOrderSet:
    __kOrderUrl = "https://jywg.eastmoneysec.com/Search/GetOrdersData"
    __kOrderUrl = "https://jywg.eastmoneysec.com/Search/GetOrdersData"
    __kHistoryOrderUrl = "https://jywg.eastmoneysec.com/Search/GetHisOrdersData"
    __order_set: dict # 订单集合
    __account_info: 'EastMoneyAccount' # 账户信息
    __order_info: dict # 订单信息

    def __init__(self, account_info: EastMoneyAccount):
        self.__account_info = account_info
    
    def Update(self):
        if datetime.now() - self.__update_time > timedelta(minutes=1):
            """{"Message":null,"Status":0,"Data":[{"Wtsj":"131729","Zqdm":"159842","Zqmc":"券商ETF","Mmsm":"证券卖出","Mmlb":"S","Wtsl":"100","Wtzt":"已成","Wtjg":"1.152","Cjsl":"100","Cjje":"115.20","Cjjg":"1.152000","Market":"SA","Wtbh":"956640","Gddm":"0289684468","Dwc":"20241227|956640","Qqhs":null,"Wtrq":"20241227","Wtph":"956640","Khdm":"540860216117","Khxm":"陈刘柱","Zjzh":"540860216117","Jgbm":"5408","Bpsj":"131729","Cpbm":"","Cpmc":"","Djje":".00","Cdsl":"0","Jyxw":"012134","Cdbs":"F","Czrq":"20241227","Wtqd":"9","Bzxx":"","Sbhtxh":"0700956640","Mmlb_ex":"S","Mmlb_bs":"S"}]}"""
            ret_json = common.GetHtml(self.__kOrderUrl, cookies = self.__account_info.session)
            self.__order_info = json.loads(ret_json)
            for order in self.__order_info['Data']:
                self.__order_set[order['Wtbh']] = EastMoneyOrder(order)

            ret_json = common.PostHtml(self.__kHistoryOrderUrl, params = {"st" : datetime.now().strftime('%Y-%m-%d'), "et" : (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'), "qqhs" : 100}, cookies = self.__account_info.session)
            self.__order_info = json.loads(ret_json)
            for order in self.__order_info['Data']:
                self.__order_set[order['Wtbh']] = EastMoneyOrder(order)

    def GetOrder(self, order_code: str):
        return self.__order_set.get(order_code)  # 如果不存在返回 None

class EastMoneyOrder(BaseOrder):
    _update_time: datetime # 更新时间
    _order_code: int # 订单号

    def __init__(self, order_json: dict):
        # 将东财的证券代码转换为tframe的证券代码
        if order_json['Market'] == "SA":
            self._stock_id = order_json['Zqdm'] + ".SZ"
        elif order_json['Market'] == "HA":
            self._stock_id = order_json['Zqdm'] + ".SH"
        else:
            logging.error(f"东财的market[{order_json['Market']}]格式错误")
            return

        # 转换委托时间
        if 'Wtrq' in order_json:
            date_str = order_json['Wtrq']  # 格式为 'YYYYMMDD'
        else:
            date_str = datetime.now().strftime('%Y%m%d')
        time_str = order_json['Wtsj']  # 格式为 'HHMMSS'
        self._create_time = datetime.strptime(date_str + time_str, '%Y%m%d%H%M%S')

        self._order_code = order_json['Wtbh']
        self._amount = order_json['Wtsl']
        self._price = order_json['Wtjg']
        self._filled_amount = order_json['Cjsl']
        self._average_filled_price = order_json['Cjje'] / order_json['Cjsl']
        if order_json['Wtzt'] == "已成":
            self._status = OrderStatus.COMPLETED
        elif order_json['Wtzt'] == "未成" or order_json['Wtzt'] == "部成":
            self._status = OrderStatus.ACTIVE
        elif order_json['Wtzt'] == "已撤":
            self._status = OrderStatus.CANCELLED
        elif order_json['Wtzt'] == "待报" or order_json['Wtzt'] == "已受理":
            self._status = OrderStatus.PENDING
        else:
            self._status = OrderStatus.FAILED
        self._update_time = datetime.now()

    def GetOrderCode(self):
        return self._order_code

# 获取东财账户信息的类
class EastMoneyAccount(BaseAccount):
    # 东财账户信息获取api地址
    __kAccountInfoUrl = "https://jywg.eastmoneysec.com/Com/queryAssetAndPositionV1"
    # 东财validatekey获取api地址，这个地址今后可以改变
    __kValidateKeyUrl = "https://jywg.eastmoneysec.com/Search/Position"
    # 东财下单api地址
    __kTradeUrl = "https://jywg.eastmoneysec.com/Trade/SubmitTradeV2"

    ____account_info: dict # 账户信息
    __validatekey: str # validatekey

    __order_set: EastMoneyOrderSet # 订单集合
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
            ret_json = common.GetHtml(self.__kAccountInfoUrl, cookies = self.session)
            self.__account_info = json.loads(ret_json)
        except json.decoder.JSONDecodeError as e:
            logging.error(f"登录态过期，重新登录")
            self.session = EastMoneySession(self.user, self.passwd).get_session()
    # 更新账户信息
    def UpdateAccountInfo(self):
        try:
            ret_json = common.GetHtml(self.__kAccountInfoUrl, cookies = self.session)
            self.__account_info = json.loads(ret_json)
        except json.decoder.JSONDecodeError as e:
            logging.error(f"登录态过期，重新登录")
            self.session = EastMoneySession(self.user, self.passwd).get_session()
        # 获取交易时需要的validatekey
        ret_html = common.GetHtml(self.__kValidateKeyUrl, cookies = self.session)
        doc = etree.HTML(ret_html)
        self.__validatekey = doc.xpath('//*[@id="em_validatekey"]/@value')[0]
        logging.info(f"get eastmoney validatekey[{self.__validatekey}]")

    # 获取账户可用资金
    def AvailableCash(self):
        return self.__account_info['Data'][0]['Kyzj']

    # 获取账户持仓市值
    def PositionMarketValue(self):
        return self.__account_info['Data'][0]['totalSecMkval']

    # 获取账户总资产
    def TotalValue(self):
        return self.__account_info['Data'][0]['Zzc']

    # 获取账户持仓,返回持仓字典，key为证券代码，value为持仓对象
    def Position(self):
        position_dict = {}
        for position in self.__account_info['Data'][0]['positions']:
            position_dict[position['Zqdm']] = EastMoneyPosition(position)
        return position_dict

    # 获取账户冻结资金
    def FrozenCash(self):
        return self.__account_info['Data'][0]['Djzj']

    # 获取账户当日盈亏
    def TodayProfit(self):
        return self.__account_info['Data'][0]['Dryk']

    # 获取账户持仓盈亏
    def PositionProfit(self):
        return self.__account_info['Data'][0]['Ljyk']

    # 获取账户总收益率
    def TotalReturnRate(self):
        return self.TotalValue() / self.__base_total_value
    
    # 下单
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
        # 如果价格为None，则使用当前买5/卖5价格, 保证成交
        if price is None:
            if amount > 0:  # 买入
                price = common.GetFiveQuote(stock_id)['fivequote']['sale5']
            else:  # 卖出
                price = common.GetFiveQuote(stock_id)['fivequote']['buy5']
                
        params["price"] = price
        ret_json = common.PostHtml(self.__kTradeUrl,cookies = self.session, params=params)
        """{"Status":0,"Count":1,"Data":[{"Htxh":"0701195683","Wtbh":"1195683"}],"Errcode":0}"""
        if ret_json['Errcode'] == 0:
            order_code = ret_json['Data'][0]['Wtbh']
            self.__order_set.Update()
            return self.__order_set.GetOrder(order_code)
        else:
            logging.error(f"下单失败，错误信息：{ret_json}")
            return None

    # 按金额下单
    def OrderByValue(self, stock_id: str, cash_amount: float, price: float = None) -> BaseOrder:
        if price is None:
            if cash_amount > 0:  # 买入
                price = common.GetFiveQuote(stock_id)['fivequote']['sale1']
            else:  # 卖出
                price = common.GetFiveQuote(stock_id)['fivequote']['buy1']
        # 计算数量，100的整数倍
        amount = int(cash_amount / price * 100) * 100
        if amount == 0:
            logging.error(f"下单失败：下单数量为 0. 价格[{price}]，金额[{cash_amount}]")
            return None
        return self.Order(stock_id, amount, price)

    # 按百分比下单
    def OrderByPercent(self, stock_id: str, percent: float, price: float = None) -> BaseOrder:
        if percent < 0 or percent > 1:
            logging.error(f"下单失败：百分比[{percent}]不在0到1之间")
            return None
        
        return self.OrderByValue(stock_id, self.TotalValue() * percent, price)

    # 调仓
    def Rebalance(self, stock_id: str, amount: int, price: float = None) -> BaseOrder:
        if self.Position()[stock_id] is None:
            return self.Order(stock_id, amount, price)
        return self.Order(stock_id, amount - self.Position()[stock_id].StockAmount(), price)
    
    # 按金额调仓
    def RebalanceByValue(self, stock_id: str, cash_amount: float, price: float = None) -> BaseOrder:
        if self.Position()[stock_id] is None:
            return self.OrderByValue(stock_id, cash_amount, price)
        return self.OrderByValue(stock_id, cash_amount - self.Position()[stock_id].MarketValue(), price)
    
    # 按百分比调仓
    def RebalanceByPercent(self, stock_id: str, percent: float, price: float = None) -> BaseOrder:
        if self.Position()[stock_id] is None:
            return self.OrderByPercent(stock_id, percent, price)
        return self.OrderByPercent(stock_id, percent - self.Position()[stock_id].MarketValue() / self.TotalValue(), price)

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
