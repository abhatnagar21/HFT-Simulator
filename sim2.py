import random
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

class order:
    def __init__(self,price,quantity,order_type):
        self.price=price
        self.quantity=quantity
        self.order_type=order_type

class marketsimulator:
    def __init__(self,initial_price,volatility,initial_cash):
        self.current_price=initial_price
        self.volatility=volatility
        self.cash=initial_cash
        self.shares=0
        self.initial_cash=initial_cash
        self.price_history=[]
        self.timestamp=datetime.now()

    def generate_order(self):
        price=self.current_price*(1+random.uniform(-self.volatility,self.volatility))#current price time volatility in percent
        quantity=random.randint(1, 10)
        order_type=random.choice(['buy','sell'])
        return order(price, quantity, order_type)

    def execute_order(self,order):
        if order.order_type=='buy':#buy order
            cost=order.price*order.quantity
            if self.cash>=cost:
                self.cash-=cost
                self.shares+=order.quantity
        elif order.order_type=='sell' and self.shares>=order.quantity:#sell order
            revenue=order.price*order.quantity
            self.cash+=revenue
            self.shares-=order.quantity

    def simulate_step(self):
        order=self.generate_order()#generate order
        self.execute_order(order)#execute order
        self.current_price=order.price#order price
        self.price_history.append(self.current_price)#adds order to history with current price
        self.timestamp += timedelta(seconds=1)

    def plot_price_movement(self):
        plt.plot(self.price_history)
        plt.title('Price Movement')
        plt.xlabel('Time Steps')
        plt.ylabel('Price')
        plt.show()

    def display_portfolio_summary(self):
        portfolio_value=self.cash+self.shares*self.current_price#left cash+shares*quatity
        pnl=((portfolio_value-self.initial_cash)/self.initial_cash)*100
        print(f"Initial Cash: ${self.initial_cash:.2f}")
        print(f"Final Portfolio Value: ${portfolio_value:.2f}")
        print(f"P&L:{pnl:.2f}%")
simulator=marketsimulator(initial_price=100,volatility=0.01,initial_cash=1000)
for _ in range(100):  
    simulator.simulate_step()
simulator.plot_price_movement()
simulator.display_portfolio_summary()
