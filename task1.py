import yfinance as yf
import pandas as pd


class AlgorithmicTrader:
    """
    Golden Cross / Death Cross algorithmic trading strategy.

    Golden Cross  → MA50 crosses above MA200 → BUY
    Death Cross   → MA50 crosses below MA200 → SELL
    Budget        → $5,000 (default)
    """

    def __init__(self, symbol, from_date, to_date, budget=5000):
        self.symbol = symbol
        self.from_date = from_date
        self.to_date = to_date
        self.budget = budget
        self.data = None
        self.trades = []

    # ------------------------------------------------------------------
    # Step 1 – Data Acquisition
    # ------------------------------------------------------------------
    def acquire_data(self):
        """Download historical OHLCV data via yfinance."""
        raw = yf.download(
            self.symbol,
            start=self.from_date,
            end=self.to_date,
            auto_adjust=True,
            progress=False,
        )
        # yfinance ≥0.2 returns a MultiIndex – flatten it
        if isinstance(raw.columns, pd.MultiIndex):
            raw.columns = raw.columns.get_level_values(0)
        self.data = raw

    # ------------------------------------------------------------------
    # Step 2 – Data Cleanup
    # ------------------------------------------------------------------
    def clean_data(self):
        """Remove duplicate dates and forward-fill NaN values."""
        self.data = self.data[~self.data.index.duplicated(keep="first")]
        self.data = self.data.ffill()

    # ------------------------------------------------------------------
    # Step 3 – Analytical Insights (Moving Averages)
    # ------------------------------------------------------------------
    def compute_moving_averages(self):
        """Compute 50-day and 200-day simple moving averages."""
        self.data["MA50"] = self.data["Close"].rolling(window=50).mean()
        self.data["MA200"] = self.data["Close"].rolling(window=200).mean()

    # ------------------------------------------------------------------
    # Step 4 – Signal Detection
    # ------------------------------------------------------------------
    def identify_signals(self):
        """
        Signal = 1 when MA50 > MA200 (bullish zone), else 0.
        Crossover = +1 → Golden Cross (buy)
        Crossover = -1 → Death Cross (sell)
        """
        self.data["Signal"] = (self.data["MA50"] > self.data["MA200"]).astype(int)
        self.data["Crossover"] = self.data["Signal"].diff()

    # ------------------------------------------------------------------
    # Step 5 – Trade Execution
    # ------------------------------------------------------------------
    def execute_trades(self):
        """
        Iterate through every trading day and act on crossover signals.

        Rules:
        - Buy on Golden Cross; can't buy again while in a position.
        - Sell on Death Cross.
        - Force-close any open position on the very last row.
        - Maximum shares = floor(budget / price).
        """
        position = None   # None or 'long'
        shares = 0
        buy_price = 0.0
        total_profit = 0.0

        rows = list(self.data.iterrows())

        for idx, (date, row) in enumerate(rows):
            # Skip rows before both MAs are available
            if pd.isna(row["MA50"]) or pd.isna(row["MA200"]):
                continue

            is_last_row = idx == len(rows) - 1
            crossover = row["Crossover"]
            close = float(row["Close"])

            # --- No position: look for buy signal ---
            if position is None:
                if crossover == 1:                          # Golden Cross
                    shares = int(self.budget // close)
                    if shares > 0:
                        buy_price = close
                        cost = shares * buy_price
                        position = "long"
                        self.trades.append(
                            {
                                "Date": date.date(),
                                "Action": "BUY",
                                "Price": buy_price,
                                "Shares": shares,
                                "Amount": cost,
                                "Profit": None,
                            }
                        )
                        print(
                            f"{date.date()} │ BUY        │ Price: ${buy_price:>8.2f} "
                            f"│ Shares: {shares:>5} │ Cost:    ${cost:>10,.2f}"
                        )

            # --- In position: look for sell signal or force-close ---
            elif position == "long":
                if crossover == -1 or is_last_row:          # Death Cross or last day
                    sell_price = close
                    revenue = shares * sell_price
                    profit = revenue - shares * buy_price
                    total_profit += profit

                    action = "SELL" if crossover == -1 else "FORCE CLOSE"
                    self.trades.append(
                        {
                            "Date": date.date(),
                            "Action": action,
                            "Price": sell_price,
                            "Shares": shares,
                            "Amount": revenue,
                            "Profit": profit,
                        }
                    )
                    print(
                        f"{date.date()} │ {action:<10} │ Price: ${sell_price:>8.2f} "
                        f"│ Shares: {shares:>5} │ Revenue: ${revenue:>10,.2f} "
                        f"│ Profit: ${profit:>+10,.2f}"
                    )
                    position = None
                    shares = 0

        return total_profit

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------
    def run(self):
        """Run the full pipeline and print a summary."""
        print(f"\n{'═'*75}")
        print(f"  Algorithmic Trading Strategy  │  {self.symbol}")
        print(f"  Period : {self.from_date}  →  {self.to_date}")
        print(f"  Budget : ${self.budget:,.2f}")
        print(f"{'═'*75}\n")

        self.acquire_data()
        self.clean_data()
        self.compute_moving_averages()
        self.identify_signals()
        total_profit = self.execute_trades()

        num_completed = len([t for t in self.trades if t["Action"] in ("SELL", "FORCE CLOSE")])
        final_balance = self.budget + total_profit

        print(f"\n{'═'*75}")
        print(f"  SUMMARY")
        print(f"{'─'*75}")
        print(f"  Completed Trades : {num_completed}")
        print(f"  Total P&L        : ${total_profit:>+,.2f}")
        print(f"  Final Balance    : ${final_balance:>,.2f}  (started with ${self.budget:,.2f})")
        print(f"{'═'*75}\n")

        return total_profit


# ----------------------------------------------------------------------
# Run
# ----------------------------------------------------------------------
if __name__ == "__main__":
    trader = AlgorithmicTrader("AAPL", "2018-01-01", "2023-12-31")
    trader.run()
