# HFT-Simulator
Market Simulator and HFT Trading Strategy
Objective: To simulate a financial market and implement a High-Frequency Trading (HFT) strategy for testing and analysis.

Market Simulator:

Price Generation: The market price is generated using a random walk based on a volatility parameter. The price changes over time, simulating real-world market conditions.
Order Book: The order book is a simulated set of buy and sell orders at various price levels. The simulator updates the order book dynamically, representing the market depth.
Logging and Analysis: The simulator logs market prices, order book sizes, and buy/sell signals. It also provides functionality to save this data to an Excel file for further analysis.
HFT Trading Strategy:

Spread-Based Orders: The strategy places buy orders slightly below the current market price and sell orders slightly above it, aiming to profit from small price fluctuations.
Order Execution: The trader checks the order book for matching orders and executes trades if conditions are met. Positions and P&L (Profit and Loss) are updated accordingly.
Performance Logging: The strategy logs each executed trade, the current position, and the cumulative P&L over time.
Key Features:

Real-Time Simulation: The market and trading activities are simulated in real-time with a slight delay to mimic HFT environments.
Data Export: The simulation results, including prices, order book, signals, transactions, positions, and P&L, are saved to an Excel file for comprehensive analysis.
Visualization: Market prices and buy/sell signals are plotted to provide visual insights into the strategy's performance.
Potential Resume Points:

Developed a market simulation tool using Python, capable of dynamically updating prices and order books to emulate real-world trading environments.
Implemented a High-Frequency Trading (HFT) strategy, utilizing spread-based order placement and order book analysis for trade execution.
Analyzed trading performance by logging and visualizing key metrics such as positions, profit & loss (P&L), and trade execution details.
Exported comprehensive trading simulation data to Excel, enabling in-depth post-simulation analysis and performance review.
