import backtrader as bt
import pandas as pd
import os

# Definieer je Strategie
class SOPROscillatorStrategy(bt.Strategy):
    params = (
        ('sopr_threshold', 80),  # Drempel voor closeness_score
    )

    def __init__(self):
        # Houd de status van posities bij
        self.order = None
        self.buyprice = None
        self.buycomm = None

    def log(self, txt, dt=None):
        ''' Logging functie '''
        dt = dt or self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()} {txt}')

    def next(self):
        if self.order:
            return

        # Inschalen bij prijs piek
        if self.datas[0].price_peak[0] and not self.position:
            self.log('BUY CREATE, Price: %.2f' % self.datas[0].close[0])
            self.order = self.buy()

        # Uitschalen bij SOPR closeness_score drempel
        if self.datas[0].closeness_score[0] > self.params.sopr_threshold and self.position:
            self.log('SELL CREATE, Price: %.2f' % self.datas[0].close[0])
            self.order = self.sell()

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return  # Wacht tot de order wordt uitgevoerd

        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'BUY EXECUTED, Price: {order.executed.price:.2f}, Cost: {order.executed.value:.2f}, Comm: {order.executed.comm:.2f}')
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            elif order.issell():
                self.log(f'SELL EXECUTED, Price: {order.executed.price:.2f}, Cost: {order.executed.value:.2f}, Comm: {order.executed.comm:.2f}')
            self.bar_executed = len(self)
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        self.order = None

# Laad de Data
data_path = '/Users/kimgrifhorst/Desktop/final charts 2024/repository/Now_I_Know/quant/bitcoin_peaks_scores.csv'
data = pd.read_csv(data_path, parse_dates=['timestamp'])
data.set_index('timestamp', inplace=True)

# Zet data in Backtrader
class PandasDataSOPR(bt.feeds.PandasData):
    lines = ('price_peak', 'SOPR_peak', 'closeness_score',)
    params = (
        ('datetime', None),
        ('open', -1),
        ('high', -1),
        ('low', -1),
        ('close', 'Price'),
        ('volume', -1),
        ('openinterest', -1),
        ('price_peak', 'price_peak'),
        ('SOPR_peak', 'SOPR_peak'),
        ('closeness_score', 'closeness_score'),
    )

data_feed = PandasDataSOPR(dataname=data)

# Initialiseer Cerebro
cerebro = bt.Cerebro()
cerebro.addstrategy(SOPROscillatorStrategy)
cerebro.adddata(data_feed)
cerebro.broker.setcash(10000.0)
cerebro.addsizer(bt.sizers.FixedSize, stake=10)
cerebro.broker.setcommission(commission=0.001)  # Stel een commission in (0.1%)

# Run Backtest
print('Start Portfolio Value: %.2f' % cerebro.broker.getvalue())
cerebro.run()
print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

# Plot de Resultaten
cerebro.plot()
