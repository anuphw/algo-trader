import backtrader as bt

from . import BaseStrategy as base


class RSI(base.Strategy):
    params = {
        'target_percent': 0.95
    }

    def __init__(self):
        base.Strategy.__init__(self)

        # Define Indicators
        self.rsi = bt.indicators.RelativeStrengthIndex(self.data.close)
        self.buysignal = bt.indicators.CrossOver(self.rsi,65)
        self.sellsignal = bt.indicators.CrossDown(self.rsi,35)
        self.target = 1.1
        self.sl = 0.9
        self.numDays = 0

    def next(self):
        base.Strategy.next(self)
        if self.order:
            # Skip if order is pending
            return

        if not self.position:
            if self.buysignal > 0 or self.order_rejected:
                # Buy the up crossover
                self.log('BUY CREATE, {:.2f}'.format(self.data.close[0]))
                self.order = self.order_target_percent(target=self.params.target_percent)
                self.order_rejected = False
        else:
            # if (self.buysell < 0) or (self.buysell_short < 0) or (self.data.close < self.sl*self.high_price):
            # (self.data.close > self.target*self.buyprice) \
            if self.sellsignal > 0 or self.data.close < self.sl*self.high_price:
                # Sell the down crossover
                self.log('SELL CREATE, {:.2f}'.format(self.data.close[0]))
                self.order = self.close(exectype=bt.Order.Market)
