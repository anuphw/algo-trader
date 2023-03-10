import backtrader as bt


class Strategy(bt.Strategy):
    """
    Wrapper for `bt.Strategy` to log orders and perform other generic tasks.
    """

    params = {
        'riskfreerate': 0.035,
        'cheat_on_open': False,
        'verbose': False
    }

    def __init__(self, kwargs=None):
        bt.Strategy.__init__(self)
        self.order = None
        self.buyprice = None
        self.buycomm = None
        self.order_rejected = False
        self.verbose = self.params.verbose
        self.high_price = 1e7
        self.inTradeDays = 0
        self.num_trades = 0
        self.profitable_trades = 0
        self.profit = 0
        self.loss = 0

    def next(self):
        self.numDays += 1
        self.high_price = max(self.high_price,self.data.high)

    def log(self, txt, date=None):
        if self.verbose:
            date = date or self.data.datetime.date(0)
            print('{}, {}'.format(date.isoformat(), txt))

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enought cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('BUY {}\t{:.2f}\t  Cost: {:.2f}\tComm: {:.2f}'.format(
                    order.data._name,
                    order.executed.price,
                    order.executed.value,
                    order.executed.comm))
                self.buyprice = order.executed.price
                self.high_price = self.buyprice
                self.buycomm = order.executed.comm
                self.buyday = self.data.datetime.date(0)
            if order.issell():
                self.log('Trade {}\t{:.2f}\t  Cost: {:.2f}\tComm: {:.2f}\tBuy: {:.2f}\tProfit: {:.2f}\tDays: {}'.format(
                    order.data._name,
                    order.executed.price,
                    order.executed.value,
                    order.executed.comm,
                    self.buyprice,
                    (order.executed.price-self.buyprice)*abs(order.executed.size),
                    (self.data.datetime.date(0)-self.buyday).days))
                self.inTradeDays += (self.data.datetime.date(0)-self.buyday).days + 1
                self.num_trades += 1
                if order.executed.price > self.buyprice:
                    self.profitable_trades += 1
                    self.profit += (order.executed.price-self.buyprice)/self.buyprice
                else:
                    self.loss += (order.executed.price-self.buyprice)/self.buyprice
                self.buyprice = -1
                self.high_price = 1e7
                
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            status_reason = {
                order.Canceled: 'Canceled',
                order.Margin: 'Margin Called',
                order.Rejected: 'Rejected'
            }
            self.log('Order {}: {} {}'.format(
                status_reason[order.status],
                'BUY' if order.isbuy() else 'SELL',
                order.data._name
            ))
            # self.log('Cash: {:.2f}, Order: {:.2f}'.format(self.broker.get_cash(),
            #                                               (order.price or 0) * (order.size or 0)))
            self.order_rejected = True

        # Write down: no pending order
        self.order = None
