# Market Risk Analysis: Historical VaR of Different Portfolios

## Introduction
This project is a quantitative analysis of risk exposure, comparing a Technology portfolio against a Banking portfolio. Using the **Historical Value at Risk (VaR)** method, the project simulates potential daily losses based on market data from the last 500 trading days.

The idea of this project is to answer: *"With 95% confidence, what is the maximum percentage loss this portfolio could suffer in a single day?"*

## Methodology
The analysis utilises Python to automate the risk calculation process:
* **Data Source:** Yahoo Finance API (`yfinance`) for real-time adjusted close prices.
* **Timeframe:** Last 2 years
* **Risk Model:** Historical Simulation. This assumes that past return distributions are a reliable indicator of future risk.
* **Formula:** $VaR_{\alpha} = -Quantile(R, 1-\alpha)$
    * Where $R$ is the vector of daily returns and $\alpha$ is the confidence level (0.95).

## Technology Stack
* **Python 3.10+**
* **Pandas & NumPy:** For vectorised calculation of daily returns and statistical quantiles.
* **Matplotlib:** For visualising the "Fat Tail" risks in return distributions.

## Key Findings
**Volatility Spread:** The Tech portfolio demonstrates a significantly higher VaR, implying a higher risk appetite is required to hold these assets.
**Market Conditions:** In the current high-interest-rate environment, the Banking portfolio shows tighter return variance, offering better capital preservation properties.
**Diversification:** The analysis confirms that sector-specific concentration increases tail risk. A merged portfolio would likely lower the aggregate VaR due to imperfect correlation between the Tech and Financial sectors.
