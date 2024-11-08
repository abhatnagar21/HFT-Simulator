#include <iostream>
#include <vector>
#include <algorithm>
#include <deque>
#include <ctime>
#include <cmath>
#include <iomanip>
#include <random>

// Class to represent an Order in the market
class Order {
public:
    double price; // The price of the order
    int quantity; // The quantity of the order
    std::string order_type; // "buy" or "sell"
    std::string order_subtype; // "market", "limit", or "cancel"
    time_t timestamp; // The timestamp when the order was created

    // Constructor to initialize the order
    Order(double p, int q, const std::string& type, const std::string& subtype, time_t time)
        : price(p), quantity(q), order_type(type), order_subtype(subtype), timestamp(time) {}
};

// Class to represent the Order Book
class OrderBook {
public:
    std::vector<Order> bids; // List of buy orders
    std::vector<Order> asks; // List of sell orders

    // Method to add an order to the order book
    void add_order(const Order& order) {
        if (order.order_subtype == "cancel") {
            cancel_order(order); // If the order is a cancel type, remove it
        } else if (order.order_subtype == "market") {
            execute_market_order(order); // If it's a market order, execute it
        } else {
            if (order.order_type == "buy") {
                bids.push_back(order); // Add buy order to bids
                // Sort bids by price (high to low), and then by timestamp (oldest first)
                std::sort(bids.begin(), bids.end(), [](const Order& a, const Order& b) {
                    return a.price > b.price || (a.price == b.price && a.timestamp < b.timestamp);
                });
            } else {
                asks.push_back(order); // Add sell order to asks
                // Sort asks by price (low to high), and then by timestamp (oldest first)
                std::sort(asks.begin(), asks.end(), [](const Order& a, const Order& b) {
                    return a.price < b.price || (a.price == b.price && a.timestamp < b.timestamp);
                });
            }
        }
    }

    // Method to cancel an order from the order book
    void cancel_order(const Order& cancel_order) {
        auto& target_list = (cancel_order.order_type == "buy") ? bids : asks; // Choose the right list (buy or sell)
        target_list.erase(
            std::remove_if(target_list.begin(), target_list.end(),
                           [&](const Order& order) {
                               return order.price == cancel_order.price && order.quantity == cancel_order.quantity;
                           }),
            target_list.end()); // Remove the order if it matches the cancel request
    }

    // Method to execute a market order (buy/sell)
    void execute_market_order(const Order& market_order) {
        auto& target_list = (market_order.order_type == "buy") ? asks : bids; // Buy order consumes sell orders, and vice versa
        int executed_quantity = 0;
        // Loop through the opposite side of the book and execute the order
        for (auto it = target_list.begin(); it != target_list.end() && executed_quantity < market_order.quantity;) {
            int execute_quantity = std::min(market_order.quantity - executed_quantity, it->quantity);
            it->quantity -= execute_quantity; // Reduce the quantity of the order
            executed_quantity += execute_quantity;

            if (it->quantity == 0) it = target_list.erase(it); // Remove fully executed order
            else ++it;
        }
    }

    // Method to match buy and sell orders
    void match_orders(std::vector<std::pair<double, int>>& trades) {
        while (!bids.empty() && !asks.empty() && bids[0].price >= asks[0].price) {
            // Match the top bid and ask orders
            double trade_price = (bids[0].price + asks[0].price) / 2.0; // Price is the average of bid and ask
            int trade_quantity = std::min(bids[0].quantity, asks[0].quantity); // The trade quantity is the min of the bid and ask quantities
            trades.emplace_back(trade_price, trade_quantity); // Record the trade

            // Update the quantities of the orders after trade
            bids[0].quantity -= trade_quantity;
            asks[0].quantity -= trade_quantity;

            if (bids[0].quantity == 0) bids.erase(bids.begin()); // Remove the order if fully executed
            if (asks[0].quantity == 0) asks.erase(asks.begin()); // Remove the order if fully executed
        }
    }
};

// Class to simulate a Market Maker (a trader that provides liquidity)
class MarketMaker {
public:
    double spread_percentage; // The spread percentage between the bid and ask prices
    int order_size; // The size of each order

    // Constructor to initialize the market maker's settings
    MarketMaker(double spread, int size) : spread_percentage(spread), order_size(size) {}

    // Method to generate buy and sell orders based on the current market price
    std::vector<Order> generate_orders(double current_price, time_t timestamp) {
        double half_spread = current_price * (spread_percentage / 2); // Calculate half the spread
        double bid_price = current_price - half_spread; // Bid price is below the current price
        double ask_price = current_price + half_spread; // Ask price is above the current price
        
        // Generate the buy and sell limit orders
        return { Order(bid_price, order_size, "buy", "limit", timestamp),
                 Order(ask_price, order_size, "sell", "limit", timestamp) };
    }
};

// Class to represent the trader's portfolio
class Portfolio {
public:
    double cash; // The cash available in the portfolio
    int shares; // The number of shares owned
    double initial_value; // The initial portfolio value (cash + shares * price)

    // Constructor to initialize the portfolio
    Portfolio(double initial_cash, int initial_shares)
        : cash(initial_cash), shares(initial_shares), initial_value(initial_cash + initial_shares * 100) {}

    // Method to execute a trade and update the portfolio
    void execute_trade(double price, int quantity, bool is_buy) {
        if (is_buy) {
            cash -= price * quantity; // Subtract money for buying
            shares += quantity; // Increase shares when buying
        } else {
            cash += price * quantity; // Add money for selling
            shares -= quantity; // Decrease shares when selling
        }
    }

    // Method to calculate the current value of the portfolio
    double get_current_value(double current_price) const {
        return cash + shares * current_price; // Cash + shares * current market price
    }

    // Method to calculate the profit and loss percentage of the portfolio
    double get_pnl_percentage(double current_price) const {
        double current_value = get_current_value(current_price);
        return ((current_value - initial_value) / initial_value) * 100; // PnL percentage
    }
};

// Class to simulate the High-Frequency Trading (HFT) environment
class HFTSimulator {
public:
    double current_price; // The current market price
    double volatility; // The market volatility
    OrderBook order_book; // The order book for buy/sell orders
    time_t timestamp; // The timestamp of the current simulation step
    MarketMaker market_maker; // The market maker providing liquidity
    Portfolio portfolio; // The portfolio holding cash and shares

    // Constructor to initialize the simulator
    HFTSimulator(double init_price, double vol, double init_cash, int init_shares)
        : current_price(init_price), volatility(vol), timestamp(std::time(nullptr)),
          market_maker(0.001, 10), portfolio(init_cash, init_shares) {}

    // Method to generate a new market price based on volatility
    double generate_new_price() {
        static std::mt19937 generator(std::random_device{}());
        std::uniform_real_distribution<double> distribution(-volatility, volatility); // Generate random price change based on volatility
        return std::max(0.01, current_price * (1 + distribution(generator))); // Ensure price doesn't go below 0
    }

    // Method to simulate one step in the market
    void simulate_step() {
        current_price = generate_new_price(); // Generate new price for this step
        std::string order_type = (rand() % 2 == 0) ? "buy" : "sell"; // Randomly choose whether it's a buy or sell order
        std::string order_subtype = (rand() % 10 < 2) ? "market" : "limit"; // Randomly choose order type (20% market, 80% limit)
        int quantity = rand() % 100 + 1; // Randomly choose quantity (1-100)

        Order order(current_price, quantity, order_type, order_subtype, timestamp);
        order_book.add_order(order); // Add the generated order to the order book

        // Add market maker orders to the book
        auto mm_orders = market_maker.generate_orders(current_price, timestamp);
        for (auto& mm_order : mm_orders) {
            order_book.add_order(mm_order);
        }

        std::vector<std::pair<double, int>> trades;
        order_book.match_orders(trades); // Match the orders in the order book

        // Execute trades and update the portfolio
        for (auto& trade : trades) {
            portfolio.execute_trade(trade.first, trade.second, trade.first < current_price);
        }

        timestamp += 1; // Increment the timestamp
    }

    // Method to display the portfolio status and trades
    void display_portfolio_status() {
        std::cout << "Cash: " << portfolio.cash << ", Shares: " << portfolio.shares << ", PnL: "
                  << portfolio.get_pnl_percentage(current_price) << "%" << std::endl;
    }
};

int main() {
    HFTSimulator simulator(100.0, 0.02, 10000.0, 0); // Initialize simulator with starting parameters

    // Simulate 100 steps
    for (int i = 0; i < 100; ++i) {
        simulator.simulate_step(); // Perform a step in the market simulation
        simulator.display_portfolio_status(); // Display portfolio after the step
    }

    return 0;
}
