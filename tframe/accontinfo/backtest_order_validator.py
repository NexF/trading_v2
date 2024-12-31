import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from tframe.accontinfo.backtest_accountinfo import BacktestAccount, BacktestOrder

# 交易验证结果
@dataclass
class ValidationResult:
    is_valid: bool
    message: str = ""

# 交易验证器接口
class OrderValidator(ABC):
    @abstractmethod
    def validate(self, order: 'BacktestOrder', account: 'BacktestAccount') -> ValidationResult:
        pass

# 具体验证器
class CashValidator(OrderValidator):
    def validate(self, order: 'BacktestOrder', account: 'BacktestAccount') -> ValidationResult:
        if order.GetAmount() <= 0:   # 卖出不需要检查资金
            return ValidationResult(True)
        
        required_cash = order.GetAmount() * order.GetPrice()
        if account.AvailableCash() >= required_cash:
            return ValidationResult(True)
        return ValidationResult(
            False, 
            f"可用资金不足: 需要 {required_cash}, 实际 {account.AvailableCash()}"
        )

class PositionValidator(OrderValidator):
    def validate(self, order: 'BacktestOrder', account: 'BacktestAccount') -> ValidationResult:
        if order.GetAmount() >= 0:  # 买入不需要检查持仓
            return ValidationResult(True)
        
        position = account.Position().get(order.GetStockId())
        if not position:
            logging.warning(f"下单失败，没有持仓: {order.GetStockId()}")
            return ValidationResult(False, "没有持仓")
        
        if position.SellableAmount() >= abs(order.GetAmount()):
            return ValidationResult(True)
        else:
            logging.warning(f"下单失败，可卖数量不足: {order.GetStockId()}")
            return ValidationResult(
                False,
                f"可卖数量不足: 需要 {abs(order.GetAmount())}, 实际 {position.SellableAmount()}"
            )

# 验证器管理器
class OrderValidatorManager:
    def __init__(self):
        self._validators: list[OrderValidator] = []
    
    def add_validator(self, validator: OrderValidator):
        self._validators.append(validator)
    
    def validate(self, order: 'BacktestOrder', account: 'BacktestAccount') -> ValidationResult:
        for validator in self._validators:
            result = validator.validate(order, account)
            if not result.is_valid:
                return result
        return ValidationResult(True)