import random #for generating random prices and order types
from datetime import datetime, timedelta#for handling timestamps
import matplotlib.pyplot as plt #for plotting price movement
from collections import deque#or efficient storage of price and volume history

class Order:
    def __init__(self, price, quantity, order_type, timestamp):
        self.price = price#price which order placed
        self.quantity = quantity#quantity of the asset to be bought/sold
        self.order_type = order_type#type of order buy or sell
        self.timestamp = timestamp#timestamp of when the order was created

class OrderBook:#manages a collection of orders and matches buy/sell orders
    def __init__(self):
        self.orders = []#list to store all orders

    def add_order(self, order):#adds a new order to the order book
        self.orders.append(order)

    def match_orders(self):#matches available buy and sell orders
        trades = []#list to store executed trades
        #separate buy and sell orders from the list of all orders
        buyorders = [order for order in self.orders if order.order_type == 'buy']
        sellorders = [order for order in self.orders if order.order_type == 'sell']

        while buyorders and sellorders:#while both buy and sell orders are available
            buy_order = buyorders.pop(0)#get the first buy order
            sell_order = sellorders.pop(0)#get the first sell order
           
            trade_price = (buy_order.price + sell_order.price) / 2 #calculate trade price as the average of buy and sell order prices
            trade_quantity = min(buy_order.quantity, sell_order.quantity)#trade quantity is the minimum quantity between buy and sell orders
            trades.append((trade_price, trade_quantity))#add the executed trade's price and quantity to the list of trades
            buy_order.quantity -= trade_quantity#decrease quantities by the traded amount for both orders
            sell_order.quantity -= trade_quantity
            if buy_order.quantity > 0:#if buy order still has quantity left, put it back in the buy list
                buyorders.insert(0, buy_order)
            
            if sell_order.quantity > 0:#if sell order still has quantity left, put it back in the sell list
                sellorders.insert(0, sell_order)

        return trades#return all matched trades

class Portfolio:
    def __init__(self, initial_cash):
        self.cash = initial_cash#cash available in the portfolio
        self.shares = 0#number of shares currently held
        self.initial_value = initial_cash#record the initial value of the portfolio

    def execute_trade(self, price, quantity, is_buy):
        if is_buy:#it's a buy order
            self.cash -= price * quantity#deduct cash for buying shares
            self.shares += quantity#increase the share count
        else:  # If it's a sell order
            self.cash += price * quantity#add cash for selling shares
            self.shares -= quantity#decrease the share count

    def get_value(self, current_price):#calculate total portfolio value
        return self.cash + self.shares * current_price#cash + market value of shares

class MarketSimulator:
    def __init__(self, initial_price, volatility, initial_cash):
        self.current_price = initial_price#current price of the asset
        self.volatility = volatility#volatility level for price movement
        self.order_book = OrderBook()#initialize the order book
        self.timestamp = datetime.now()#start timestamp for the simulation
        self.price_history = deque(maxlen=1000)#track price history with max length 1000
        self.volume_history = deque(maxlen=1000)#track volume history with max length 1000
        self.portfolio = Portfolio(initial_cash)#initialize portfolio with starting cash

    def simulate_step(self):
        #random price movement based on current price and volatility
        new_price = max(1, self.current_price * (1 + random.uniform(-self.volatility, self.volatility)))

        #generate a random order type and quantity
        order_type = random.choice(['buy', 'sell'])#randomly choose buy or sell
        quantity = random.randint(1, 10)#rndomly choose quantity between 1 and 10
        new_order = Order(new_price, quantity, order_type, self.timestamp)#create new order
        self.order_book.add_order(new_order)#add order to the order book

        #match buy and sell orders in the order book
        trades = self.order_book.match_orders()#get list of trades after matching
        self.current_price = new_price #update the current price to the latest simulated price

        #update portfolio based on executed trades
        for trade_price, trade_quantity in trades:
            is_buy = order_type == 'buy'#check if the initial order was a buy
            self.portfolio.execute_trade(trade_price, trade_quantity, is_buy)#update portfolio

        #store the new price in the price history
        self.price_history.append(self.current_price)
        # store the trade volume in the volume history
        self.volume_history.append(sum(trade[1] for trade in trades))
        # move forward the timestamp by one second for the next simulation step
        self.timestamp += timedelta(seconds=1)

    def plot_price_movement(self):#plot the recorded price movement over time
        plt.plot(self.price_history)
        plt.title('Price Movement')
        plt.xlabel('Time')
        plt.ylabel('Price')
        plt.show()

    def display_portfolio_summary(self):#display initial and final portfolio value and P&L
        final_value = self.portfolio.get_value(self.current_price)#get final portfolio value
        pnl_percentage = ((final_value - self.portfolio.initial_value) / self.portfolio.initial_value) * 100#calculate p&l percentage
        print(f"Initial Portfolio Value: ${self.portfolio.initial_value:.2f}")
        print(f"Final Portfolio Value: ${final_value:.2f}")
        print(f"P&L Percentage: {pnl_percentage:.2f}%")

# Example usage
simulator = MarketSimulator(initial_price=100, volatility=0.001, initial_cash=100000)

for _ in range(1000):#run 1000 steps of the simulation
    simulator.simulate_step()

simulator.plot_price_movement()#plot the price movement over time
simulator.display_portfolio_summary()#display summary of portfolio performance
