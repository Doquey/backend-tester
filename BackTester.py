import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import datetime as dt


class BackTester():

    def __init__(self, stocks: list, start: dt.datetime, end: dt.datetime, method: int = 0, initial_investment: float = 1000.0, aport_mensal: float = 500.0):
        self.stocks = stocks
        self.map_methods_to_string = {
            0: "equally",
            1: "random_weighted"
        }
        self.start_date = start
        self.end_date = end
        self.total_return = 0
        self.return_per_stock = {}
        self.aport_mensal = aport_mensal
        self.divide_method = method
        self.initial_investment = initial_investment
        self.invested_value = initial_investment
        self.stocks_money = {}
        self.monthly_returns = {}
        if self.map_methods_to_string[self.divide_method] == "equally":
            self.divide_equally()
        else:
            self.divide_random_weighted()

    def divide_equally(self):
        money_per_stock = self.initial_investment / len(self.stocks)
        for stock in self.stocks:
            self.stocks_money[stock] = money_per_stock

    def divide_random_weighted(self):
        weights = np.random.random(len(self.stocks))
        weights /= sum(weights)

        for ind, stock in enumerate(self.stocks):
            self.stocks_money[stock] = self.initial_investment * weights[ind]

    def get_data(self, stocks: list, start: dt.datetime, end: dt.datetime) -> dict:
        stock_data = {}
        for stock in stocks:
            current_start = start
            while current_start <= end:
                try:
                    data = yf.download(stock, start=current_start, end=end)
                    if not data.empty:
                        stock_data[stock] = data
                        break
                except Exception as e:
                    print(f"Exception for {stock}: {e}")
                current_start += dt.timedelta(days=365)
            else:
                stock_data[stock] = []
        return stock_data

    def get_total_return(self, stock_data: pd.DataFrame, money_to_stock: float) -> float:
        stock_data['Daily Return'] = stock_data['Close'].pct_change()
        cumulative_return = (stock_data['Daily Return'] + 1).prod() - 1
        stock_return = money_to_stock * (1 + cumulative_return)
        return stock_return

    def get_monthly_return(self, stock_data: pd.DataFrame, money_stock: float) -> list:
        current_value = money_stock
        returns = [money_stock]

        # Resample the data to monthly frequency and calculate monthly returns
        monthly_returns = stock_data['Close'].resample(
            'M').ffill().pct_change()

        # Iterate over the monthly returns to calculate the portfolio value
        for date, value in monthly_returns.items():
            if pd.notna(value):
                growth_factor = value + 1
                new_value = growth_factor * current_value
                current_value = new_value
                returns.append(new_value)

        return returns

    def plot_monthly_returns(self):
        fig, ax = plt.subplots(figsize=(12, 8))
        fig.patch.set_facecolor('white')  # Set background color to white

        # Plot individual stock monthly returns
        for stock, returns in self.monthly_returns.items():
            months_count = np.arange(len(returns))
            ax.plot(months_count, returns,
                    label=f'{stock} Monthly Returns', linewidth=1.5)

        # Calculate and plot portfolio monthly returns
        portfolio_returns = np.sum(
            list(self.monthly_returns.values()), axis=0)
        months_count = np.arange(len(portfolio_returns))
        ax.plot(months_count, portfolio_returns,
                label='Portfolio Monthly Returns', linewidth=2, linestyle='--', color='black')

        ax.set_title('Monthly Returns of Stocks and Portfolio', fontsize=16)
        ax.set_xlabel('Months', fontsize=14)
        ax.set_ylabel('Returns', fontsize=14)
        ax.tick_params(axis='both', labelsize=12)
        ax.legend(fontsize=12, loc='upper left')
        ax.grid(True, linestyle='--', alpha=0.7)

        # Set y-axis limits to include zero
        ax.set_ylim(ymin=ax.get_ylim()[0], ymax=ax.get_ylim()[1] * 1.1)

        plt.tight_layout()
        plt.show()

    def run(self):
        stock_data = self.get_data(self.stocks, self.start_date, self.end_date)
        for stock_name, stock_data in stock_data.items():
            stock_total_return = self.get_total_return(
                stock_data, self.stocks_money[stock_name])
            monthly_returns = self.get_monthly_return(
                stock_data, self.stocks_money[stock_name])
            self.monthly_returns[stock_name] = monthly_returns
            self.total_return += stock_total_return
            self.return_per_stock[stock_name] = stock_total_return
        # self.plot_monthly_returns()
        portfolio_returns = np.sum(
            list(self.monthly_returns.values()), axis=0)
        return self.total_return, portfolio_returns, self.return_per_stock


if __name__ == "__main__":

    stockList = ["KEPL3", "RAPT3", "CMIG3", "GOAU3", "MTSA4", "ITUB3"]
    stocks = [stock + ".SA" for stock in stockList]

    endDate = dt.datetime.now()
    startDate = endDate - dt.timedelta(days=365*5)

    back_test = BackTester(stocks, startDate, endDate, 0, 5000, 150)

    return_, _, _ = back_test.run()

    print(return_)
