Market Risk Analysis: Tech vs. Banking Portfolios
Overview

This project quantitatively assesses the risk exposure of two distinct equity portfolios: a Technology portfolio and a Banking portfolio. Using Historical Value at Risk (VaR) on 500 trading days of market data, we simulate potential daily losses to determine which sector exhibits greater downside risk.

Core Question: At 95% confidence, what is the maximum percentage loss each portfolio could face in a single trading day?
Methodology

The analysis is implemented in Python and follows these steps:

    Data Collection: Fetch adjusted closing prices for the past two years via Yahoo Finance API (yfinance)

    Portfolio Construction:

        Tech Portfolio: AAPL, MSFT, NVDA, GOOGL

        Banking Portfolio: JPM, BAC, GS, MS

    Risk Calculation: Apply Historical VaR methodology:

        Formula: VaR = -percentile(daily_returns, 1 - confidence_level)

        Confidence level: 95%

    Additional Metrics: Calculate Conditional VaR (CVaR) and annualized volatility for comprehensive risk assessment

Key Findings

    Higher Tech Volatility: The Technology portfolio demonstrates significantly greater Historical VaR, indicating it requires a higher risk tolerance

    Banking Stability: In the current high-interest-rate environment, banking stocks show tighter return distributions and better capital preservation characteristics

    Diversification Benefit: A combined portfolio would likely reduce aggregate VaR due to imperfect correlation between Tech and Financial sectors

Technical Implementation

    Language: Python 3.12.4

    Libraries:

        yfinance for market data

        pandas & numpy for vectorized returns and quantile calculations

        matplotlib for visualizing return distributions and tail risks

    Outputs: Risk metrics console output + distribution plots saved to /outputs

Usage
bash

# Clone repository
git clone <repo-url>

# Install dependencies
pip install yfinance pandas numpy matplotlib

# Run analysis
python risk_analysis.py

The script will:

    Download recent market data

    Calculate and display risk metrics for both portfolios

    Generate visualization plots comparing return distributions

    Output comparative risk insights
