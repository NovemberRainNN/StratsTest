# -*- coding: utf-8 -*-
"""


@author: lixin
"""

import pandas as pd
import backtrader as bt
import os
import sys
import datetime

df = pd.read_csv(r"C:\Users\lixin\Desktop\data\data.csv")
# print(list(df.groupby(["ticker"])))

df["date"] = df["date"].map(lambda x: datetime.datetime.strptime(x, "%m/%d/%Y"))

type(df["date"][0])

class MyStrategy(bt.Strategy):

    def log(self, txt, dt=None, doprint=True):
        ''' trading record '''
        if doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):

        # initialize relavant data
        self.dataclose = self.datas[0].close
        self.order = None
        self.buyprice = None
        self.buycomm = None

        # Trading stragtegy
        # MA5
        self.sma5 = bt.indicators.SimpleMovingAverage(
            self.datas[0], period=5)
        #  MA10
        self.sma10 = bt.indicators.SimpleMovingAverage(
            self.datas[0], period=10)

    def notify_order(self, order):
        """
        Arguments:
            order {object} -- order status
        """
        if order.status in [order.Submitted, order.Accepted]:
            # 如订单已被处理，则不用做任何事情
            return

        # 检查订单是否完成
        if order.status in [order.Completed]:
            if order.isbuy():
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            self.bar_executed = len(self)

        # 订单因为缺少资金之类的原因被拒绝执行
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # 订单状态处理完成，设为空
        self.order = None

    def notify_trade(self, trade):
        """
        
        Arguments:
            trade {object} -- 交易状态
        """
        if not trade.isclosed:
            return
        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm), doprint=False)

    def next(self):

        self.log('Close, %.2f' % self.dataclose[0])

        if self.order:
            return

        if not self.position:
            if self.sma5[0] > self.sma10[0]:
                self.order = self.buy()
        else:
            
            if self.sma5[0] < self.sma10[0]:
                self.order = self.sell()

    def stop(self):
        self.log(u'Ending Value %.2f' %
                 (self.broker.getvalue()), doprint=True)
        
cerebro = bt.Cerebro()

strats = cerebro.addstrategy(MyStrategy)
# buy 100 shares each time
cerebro.addsizer(bt.sizers.FixedSize, stake=100)



data = bt.feeds.PandasData(dataname=df,   
#     fromdate=datetime.datetime(2013, 1, 4),
#     todate=datetime.datetime(2021, 3, 19),
#     nullvalue=0.0,  # NA value to 0
#     dtformat="%Y-%m-%d",
    datetime=1,  
    close=2,
    volume=3)

cerebro.adddata(data)


cerebro.broker.setcash(1000000.0)
cerebro.broker.setcommission(0.005)


print('Initial Cash amount: %.2f' % cerebro.broker.getvalue())

# execute strat
thestrat = cerebro.run()
print('Sharpe Ratio:', thestrat[0].analyzers.mysharpe.get_analysis())
print("Final Portfolio Value: %.2f" % cerebro.broker.getvalue())