import backtrader as bt

from . import BaseStrategy as base


class PriceCrossOver(base.Strategy):
    params = {
        'target_percent': 0.95
    }

    def __init__(self):
        base.Strategy.__init__(self)

        # Define Indicators
        self.sma20 = bt.indicators.MovingAverageSimple(period=20)
        self.sma200 = bt.indicators.MovingAverageSimple(period=200)
        self.buysell = bt.indicators.CrossOver(self.data.close, self.sma200, plot=True)
        self.buysell_short = bt.indicators.CrossOver(self.data.close,self.sma20,plot=True)
        self.target = 1.1
        self.sl = 0.9
        self.numDays = 0

    def next(self):
        base.Strategy.next(self)
        
        if self.order:
            # Skip if order is pending
            return

        if not self.position:
            if (self.buysell_short > 0 and self.data.close > self.sma200) or self.order_rejected:
                # Buy the up crossover
                self.log('BUY CREATE, {:.2f}'.format(self.data.close[0]))
                self.order = self.order_target_percent(target=self.params.target_percent)
                self.order_rejected = False
        else:
            # if (self.buysell < 0) or (self.buysell_short < 0) or (self.data.close < self.sl*self.high_price):
            # (self.data.close > self.target*self.buyprice) \
            close = self.data.close
            if (close < self.sma20 or close < self.sma200 or self.data.close < self.sl*self.high_price):
                # Sell the down crossover
                self.log('SELL CREATE, {:.2f}'.format(self.data.close[0]))
                self.order = self.close(exectype=bt.Order.Market)
