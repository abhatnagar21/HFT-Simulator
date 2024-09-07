import random
from datetime import datetime, timedelta
import numpy as np
import matplotlib.pyplot as plt
from collections import deque

class Order:
    def __init__(self, price, quantity, order_type, order_subtype, timestamp):
        self.price = price
        self.quantity = quantity
        self.order_type = order_type  # 'buy' or 'sell'
        self.order_subtype = order_subtype  # 'market', 'limit', or 'cancel'
        self.timestamp = timestamp

class OrderBook:
    def __init__(self):
        self.bids = []  # Buy orders
        self.asks = []  # Sell orders

    def add_order(self, order):
        if order.order_subtype == 'cancel':
            self.cancel_order(order)
        elif order.order_subtype == 'market':
            self.execute_market_order(order)
        else:  # limit order
            if order.order_type == 'buy':
                self.bids.append(order)
                self.bids.sort(key=lambda x: (-x.price, x.timestamp))
            else:
                self.asks.append(order)
                self.asks.sort(key=lambda x: (x.price, x.timestamp))

    def cancel_order(self, cancel_order):
        target_list = self.bids if cancel_order.order_type == 'buy' else self.asks
        target_list[:] = [order for order in target_list if order.price != cancel_order.price or order.quantity != cancel_order.quantity]

    def execute_market_order(self, market_order):
        target_list = self.asks if market_order.order_type == 'buy' else self.bids
        executed_quantity = 0
        while target_list and executed_quantity < market_order.quantity:
            best_order = target_list[0]
            execute_quantity = min(market_order.quantity - executed_quantity, best_order.quantity)
            best_order.quantity -= execute_quantity
            executed_quantity += execute_quantity
            if best_order.quantity == 0:
                target_list.pop(0)

    def match_orders(self):
        trades = []
        while self.bids and self.asks and self.bids[0].price >= self.asks[0].price:
            buy_order = self.bids[0]
            sell_order = self.asks[0]
            trade_price = (buy_order.price + sell_order.price) / 2  # Mid-price execution
            trade_quantity = min(buy_order.quantity, sell_order.quantity)
            
            trades.append((trade_price, trade_quantity, buy_order.timestamp))
            
            buy_order.quantity -= trade_quantity
            sell_order.quantity -= trade_quantity
            
            if buy_order.quantity == 0:
                self.bids.pop(0)
            if sell_order.quantity == 0:
                self.asks.pop(0)
        
        return trades

    def get_depth(self, levels=5):
        bid_depth = [(order.price, order.quantity) for order in self.bids[:levels]]
        ask_depth = [(order.price, order.quantity) for order in self.asks[:levels]]
        return bid_depth, ask_depth

class MarketMaker:
    def __init__(self, spread_percentage, order_size):
        self.spread_percentage = spread_percentage
        self.order_size = order_size

    def generate_orders(self, current_price, timestamp):
        half_spread = current_price * (self.spread_percentage / 2)
        bid_price = current_price - half_spread
        ask_price = current_price + half_spread
        
        bid_order = Order(bid_price, self.order_size, 'buy', 'limit', timestamp)
        ask_order = Order(ask_price, self.order_size, 'sell', 'limit', timestamp)
        
        return [bid_order, ask_order]

class Portfolio:
    def __init__(self, initial_cash, initial_shares):
        self.cash = initial_cash
        self.shares = initial_shares
        self.initial_value = initial_cash + initial_shares * 100  # Assuming initial price is 100

    def execute_trade(self, price, quantity, is_buy):
        if is_buy:
            self.cash -= price * quantity
            self.shares += quantity
        else:
            self.cash += price * quantity
            self.shares -= quantity

    def get_current_value(self, current_price):
        return self.cash + self.shares * current_price

    def get_pnl_percentage(self, current_price):
        current_value = self.get_current_value(current_price)
        return ((current_value - self.initial_value) / self.initial_value) * 100

class HFTSimulator:
    def __init__(self, initial_price, volatility, initial_cash, initial_shares):
        self.current_price = initial_price
        self.volatility = volatility
        self.order_book = OrderBook()
        self.timestamp = datetime.now()
        self.market_maker = MarketMaker(spread_percentage=0.001, order_size=10)
        self.price_history = deque(maxlen=1000)
        self.volume_history = deque(maxlen=1000)
        self.portfolio = Portfolio(initial_cash, initial_shares)

    def generate_new_price(self):
        return max(0.01, self.current_price * (1 + random.uniform(-self.volatility, self.volatility)))

    def simulate_step(self):
        new_price = self.generate_new_price()
        order_type = random.choice(['buy', 'sell'])
        order_subtype = random.choices(['market', 'limit', 'cancel'], weights=[0.2, 0.7, 0.1])[0]
        quantity = random.randint(1, 100)
        
        order = Order(new_price, quantity, order_type, order_subtype, self.timestamp)
        self.order_book.add_order(order)
        
        # Add market maker orders
        mm_orders = self.market_maker.generate_orders(self.current_price, self.timestamp)
        for mm_order in mm_orders:
            self.order_book.add_order(mm_order)
        
        trades = self.order_book.match_orders()
        
        if trades:
            self.current_price = trades[-1][0]  # Last trade price
            self.price_history.append(self.current_price)
            self.volume_history.append(sum(trade[1] for trade in trades))
            
            # Update portfolio based on trades
            for trade_price, trade_quantity, _ in trades:
                is_buy = random.choice([True, False])  # Randomly decide if we're buying or selling
                self.portfolio.execute_trade(trade_price, trade_quantity, is_buy)
        else:
            self.price_history.append(self.current_price)
            self.volume_history.append(0)
        
        self.timestamp += timedelta(milliseconds=random.randint(1, 100))
        
        return trades

    def plot_price_movement(self):
        plt.figure(figsize=(12, 6))
        plt.plot(self.price_history)
        plt.title('Price Movement')
        plt.xlabel('Time')
        plt.ylabel('Price')
        plt.show()

    def plot_volume(self):
        plt.figure(figsize=(12, 6))
        plt.bar(range(len(self.volume_history)), self.volume_history)
        plt.title('Trading Volume')
        plt.xlabel('Time')
        plt.ylabel('Volume')
        plt.show()

    def plot_order_book_depth(self):
        bid_depth, ask_depth = self.order_book.get_depth()
        
        bid_prices, bid_sizes = zip(*bid_depth) if bid_depth else ([], [])
        ask_prices, ask_sizes = zip(*ask_depth) if ask_depth else ([], [])
        
        plt.figure(figsize=(12, 6))
        plt.bar(bid_prices, bid_sizes, color='g', alpha=0.5, label='Bids')
        plt.bar(ask_prices, ask_sizes, color='r', alpha=0.5, label='Asks')
        plt.title('Order Book Depth')
        plt.xlabel('Price')
        plt.ylabel('Size')
        plt.legend()
        plt.show()

    def display_portfolio_summary(self):
        initial_value = self.portfolio.initial_value
        final_value = self.portfolio.get_current_value(self.current_price)
        pnl_percentage = self.portfolio.get_pnl_percentage(self.current_price)
        
        print(f"Initial Portfolio Value: ${initial_value:.2f}")
        print(f"Final Portfolio Value: ${final_value:.2f}")
        print(f"P&L Percentage: {pnl_percentage:.2f}%")

# Example usage
simulator = HFTSimulator(initial_price=100, volatility=0.001, initial_cash=100000, initial_shares=1000)

for _ in range(10000):
    trades = simulator.simulate_step()

simulator.plot_price_movement()
simulator.plot_volume()
simulator.plot_order_book_depth()
simulator.display_portfolio_summary()
