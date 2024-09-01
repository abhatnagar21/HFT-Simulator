import numpy as np
import pandas as pd
import time
import random
import matplotlib.pyplot as plt

class MarketSimulator:
    def __init__(self, symbol, start_price=100, volatility=0.01, tick_size=0.01):
        self.symbol = symbol
        self.price = start_price
        self.volatility = volatility
        self.tick_size = tick_size
        self.order_book = pd.DataFrame(columns=["price", "volume", "side"])
        self.prices = []
        self.buy_signals = []
        self.sell_signals = []
        self.order_book_sizes = []
        self.logs = []
    
    def update_price(self):
        # Simulate random walk for price
        change_percent = np.random.normal(0, self.volatility)
        self.price += self.price * change_percent
        self.price = round(self.price, 2)  # Round to 2 decimal places
        self.prices.append(self.price)
    
    def update_order_book(self):
        # Simulate order book updates
        for _ in range(random.randint(1, 5)):
            price = round(self.price + random.uniform(-0.05, 0.05), 2)
            volume = random.randint(1, 100)
            side = random.choice(["buy", "sell"])
            new_order = pd.DataFrame({"price": [price], "volume": [volume], "side": [side]})
            self.order_book = pd.concat([self.order_book, new_order], ignore_index=True)
    
    def get_order_book(self):
        return self.order_book
    
    def simulate(self, iterations=100):
        for _ in range(iterations):
            self.update_price()
            self.update_order_book()
            self.order_book_sizes.append(len(self.order_book))
            self.logs.append({
                "Price": self.price,
                "Order Book Size": len(self.order_book)
            })
            print(f"Price: {self.price}, Order Book Size: {len(self.order_book)}")
            time.sleep(0.1)  # Simulate time delay for HFT
    
    def save_to_excel(self, filename="hft_simulation.xlsx", transactions=None, pnl_statement=None, positions=None):
        with pd.ExcelWriter(filename) as writer:
            # Save market prices
            prices_df = pd.DataFrame({"Time": range(len(self.prices)), "Price": self.prices})
            prices_df.to_excel(writer, sheet_name="Market Prices", index=False)
            
            # Save order book
            self.order_book.to_excel(writer, sheet_name="Order Book", index=False)
            
            # Save buy and sell signals
            signals_df = pd.DataFrame({
                "Buy Signals": self.buy_signals,
                "Sell Signals": self.sell_signals
            })
            signals_df.to_excel(writer, sheet_name="Signals", index=False)
            
            # Save logs
            logs_df = pd.DataFrame(self.logs)
            logs_df.to_excel(writer, sheet_name="Logs", index=False)
            
            # Save transaction records if provided
            if transactions is not None:
                transactions_df = pd.DataFrame(transactions)
                transactions_df.to_excel(writer, sheet_name="Transactions", index=False)
            
            # Save profit and loss statement if provided
            if pnl_statement is not None:
                pnl_df = pd.DataFrame({"P&L": pnl_statement})
                pnl_df.to_excel(writer, sheet_name="P&L Statement", index=False)
            
            # Save positions if provided
            if positions is not None:
                positions_df = pd.DataFrame({"Positions": positions})
                positions_df.to_excel(writer, sheet_name="Positions", index=False)

    def plot(self):
        plt.figure(figsize=(12, 6))
        plt.plot(self.prices, label='Market Price', color='blue')
        plt.scatter(self.buy_signals, [self.prices[i] for i in self.buy_signals], marker='^', color='green', label='Buy Signal', s=100)
        plt.scatter(self.sell_signals, [self.prices[i] for i in self.sell_signals], marker='v', color='red', label='Sell Signal', s=100)
        plt.title('Market Price with Buy/Sell Signals')
        plt.xlabel('Time')
        plt.ylabel('Price')
        plt.legend()
        plt.show()


class HFTTrader:
    def __init__(self, symbol, market, spread=0.02):
        self.symbol = symbol
        self.market = market
        self.spread = spread
        self.position = 0
        self.pnl = 0
        self.orders = []
        self.executed_orders = []
        self.position_log = []
        self.pnl_log = []

    def place_orders(self):
        # Place buy and sell orders separately
        buy_price = round(self.market.price - self.spread / 2, 2)
        sell_price = round(self.market.price + self.spread / 2, 2)
        
        # Only place buy orders if no recent buy signal
        if not self.market.buy_signals or len(self.market.buy_signals) < 1 or self.market.buy_signals[-1] != len(self.market.prices) - 1:
            buy_order = {"price": buy_price, "volume": 10, "side": "buy"}
            self.orders.append(buy_order)
            self.market.buy_signals.append(len(self.market.prices) - 1)  # Record buy signal index
            print(f"Placed buy order at {buy_price}")
        
        # Only place sell orders if no recent sell signal
        if not self.market.sell_signals or len(self.market.sell_signals) < 1 or self.market.sell_signals[-1] != len(self.market.prices) - 1:
            sell_order = {"price": sell_price, "volume": 10, "side": "sell"}
            self.orders.append(sell_order)
            self.market.sell_signals.append(len(self.market.prices) - 1)  # Record sell signal index
            print(f"Placed sell order at {sell_price}")
    
    def execute_orders(self):
        order_book = self.market.get_order_book()
        for order in self.orders.copy():  # Use a copy of the orders list to avoid modifying it during iteration
            matching_orders = order_book[(order_book['price'] == order['price']) & (order_book['side'] != order['side'])]
            if not matching_orders.empty:
                executed_order = matching_orders.iloc[0]
                if order['side'] == 'buy':
                    self.position += order['volume']
                    self.pnl -= order['volume'] * order['price']
                else:
                    self.position -= order['volume']
                    self.pnl += order['volume'] * order['price']
                print(f"Executed {order['side']} order at {order['price']} for {order['volume']} shares")
                self.orders.remove(order)

                # Remove the executed order from the order book
                self.market.order_book = self.market.order_book.drop(matching_orders.index[0])
                
                # Log executed orders
                self.executed_orders.append({
                    "price": order['price'],
                    "volume": order['volume'],
                    "side": order['side'],
                    "time": len(self.market.prices) - 1
                })
                
                # Log position and P&L
                self.position_log.append(self.position)
                self.pnl_log.append(self.pnl)

    def print_status(self):
        print(f"Position: {self.position}, P&L: {self.pnl}")


# Example usage
market = MarketSimulator(symbol="AAPL")
trader = HFTTrader(symbol="AAPL", market=market)

# Simulate the market and trading activity
for _ in range(20):
    market.simulate(1)
    trader.place_orders()
    trader.execute_orders()
    trader.print_status()
    time.sleep(0.1)

# Save results to Excel
market.save_to_excel(filename="hft_simulation.xlsx", transactions=trader.executed_orders, positions=trader.position_log, pnl_statement=trader.pnl_log)

# Plotting results
market.plot()
