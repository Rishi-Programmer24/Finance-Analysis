import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime
from pathlib import Path

def fetch_data(tickers, start_date, end_date):
    #fetches close prices, handles shape problems, and warns about missing tickers
    

    raw_data = yf.download(tickers, start=start_date, end=end_date, auto_adjust=True, progress=False)

    #fail if no data returned
    if raw_data.empty:
        raise ValueError(f"No data returned for tickers={tickers}. Check symbols or internet connection.")

    if isinstance(raw_data.columns, pd.MultiIndex):
        data = raw_data["Close"]
    else:
        data = raw_data["Close"] if "Close" in raw_data.columns else raw_data

    #make sure  it is a dataframe even if only one ticker is fetched
    if isinstance(data, pd.Series):
        data = data.to_frame()

    #convert both to sets to find the difference
    if isinstance(tickers, list):
        missing_tickers = set(tickers) - set(data.columns)
        if missing_tickers:
            print(f"Warning: The following tickers were not found in the returned data: {missing_tickers}")

    #handle missing data
    data = data.ffill().dropna()

    #final check 
    if data.empty:
        raise ValueError(f"All data rows dropped after cleaning for tickers={tickers}.")
    
    return data

def calculate_portfolio_returns(data, weights=None):
    
    #calculates weighted portfolio returns with strict validation (long-only, zero-div safe).
    
    #calculate daily simple returns for each stock
    returns = data.pct_change().dropna()
    
    #match weights to the shape of the return cols
    num_assets = returns.shape[1]
    
    if weights is None:
        #default to equal weighting
        weights = np.array([1/num_assets] * num_assets)
    else:
        weights = np.array(weights)
        #check length matches
        if len(weights) != num_assets:
            raise ValueError(f"Weight length ({len(weights)}) does not match number of assets ({num_assets})")
        
        if (weights < 0).any():
            raise ValueError("Negative weights detected. This model supports long-only portfolios.")

        total_weight = weights.sum()
        if np.isclose(total_weight, 0.0):
             raise ValueError("Weights sum to zero — cannot normalise.")
             
        if not np.isclose(total_weight, 1.0):
            print(f"Warning: Weights sum to {total_weight}, not 1.0. Normalising...")
            weights = weights / total_weight

    #calculate weighted portfolio returns
    portfolio_returns = returns.dot(weights)
    return portfolio_returns

def calculate_risk_metrics(returns, conf_level=0.95):
    
    #calculates VaR, CVaR, and Annualised Volatility.
    
    #VaR: the threshold at the (1-alpha) quantile
    var_percentile = 1 - conf_level
    var_value = returns.quantile(var_percentile)
    
    #CVaR: the average of all returns that fall below the VaR threshold
    cvar_value = returns[returns <= var_value].mean()
    
    #annualised volatility 
    daily_vol = returns.std()
    annual_vol = daily_vol * np.sqrt(252)
    
    return var_value, cvar_value, annual_vol

def plot_distribution(returns, var_value, cvar_value, portfolio_name, n_days, conf_level):
    
    #visualises the histogram of returns and saves to outputs folder with dynamic labelling.
    
    plt.figure(figsize=(10, 6))
    
    #convert confidence level to percentage integer for the label 
    cl_pct = int(conf_level * 100)
    
    #make the histogram
    plt.hist(returns, bins=50, alpha=0.75, color='cornflowerblue', edgecolor='black', label='Daily Returns')
    
    #plot VaR line with dynamic labelling
    plt.axvline(var_value, color='red', linestyle='--', linewidth=2, 
                label=f'VaR {cl_pct}%: {var_value:.2%} (|Loss|={abs(var_value):.2%})')
    
    #plot CVaR line with dynamic labelling
    plt.axvline(cvar_value, color='darkred', linestyle='-', linewidth=2, 
                label=f'CVaR {cl_pct}%: {cvar_value:.2%} (|Loss|={abs(cvar_value):.2%})')
    
    plt.title(f'Historical Distribution: {portfolio_name} (Last {n_days} Trading Days)')
    plt.xlabel('Daily Return')
    plt.ylabel('Frequency')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    #save into outputs/ folder using pathlib
    out_dir = Path("outputs")
    out_dir.mkdir(exist_ok=True)
    filename = out_dir / f"{portfolio_name}_risk_profile.png"
    
    plt.savefig(filename, dpi=150)
    plt.close()
    print(f"Plot saved as {filename}")

def main():
    #config
    portfolios = {
        "Tech_Portfolio": ["AAPL", "MSFT", "NVDA", "GOOGL"],
        "Banking_Portfolio": ["JPM", "BAC", "GS", "MS"]
    }

    #fetch 2 years of data
    start_date = (datetime.datetime.now() - datetime.timedelta(days=730)).strftime('%Y-%m-%d')
    end_date = datetime.datetime.now().strftime('%Y-%m-%d')
    confidence_level = 0.95

    print(f"--- Market Risk Analysis (Trading Days Method) ---\n")
    
    results = {}

    for name, tickers in portfolios.items():
        print(f"Processing {name}...")
        
        try:
            #get data
            stock_data = fetch_data(tickers, start_date, end_date)
            
            #slice to exactly the last 500 trading days for standardisation
            stock_data = stock_data.tail(500)
            n_days = len(stock_data)
            
            if n_days < 450:
                print(f"Warning: Only {n_days} trading days available for {name}. Results may be less reliable.")
            
            #calculate returns
            p_returns = calculate_portfolio_returns(stock_data)
            
            #calculate risk metrics 
            var, cvar, ann_vol = calculate_risk_metrics(p_returns, confidence_level)
            
            #store results
            results[name] = {"VaR": var, "CVaR": cvar, "Vol": ann_vol}
            
            #output & visualise 
            print(f"  > VaR ({int(confidence_level*100)}%): {abs(var):.2%} (Max expected loss)")
            print(f"  > CVaR ({int(confidence_level*100)}%): {abs(cvar):.2%} (Avg loss in tail)")
            print(f"  > Annualised Vol: {ann_vol:.2%} (Standard Deviation)")
            print("")
            
            plot_distribution(p_returns, var, cvar, name, n_days, confidence_level)
            
        except Exception as e:
            print(f"Error processing {name}: {e}")
            print("")

    #final comparison
    print("--- Risk Insights ---")
    
    #both portfolios to compare
    if "Tech_Portfolio" in results and "Banking_Portfolio" in results:
        tech_var_mag = abs(results['Tech_Portfolio']['VaR'])
        bank_var_mag = abs(results['Banking_Portfolio']['VaR'])

        print(f"Tech VaR (Loss Magnitude):    {tech_var_mag:.2%}")
        print(f"Banking VaR (Loss Magnitude): {bank_var_mag:.2%}")

        if tech_var_mag > bank_var_mag:
            print("Conclusion: The Tech portfolio exhibits higher downside risk compared to Banking.")
        else:
            print("Conclusion: The Banking portfolio exhibits higher downside risk compared to Tech.")
            
    elif len(results) > 0:
        print("Comparison skipped: One or more portfolios failed to process.")
        print(f"Available results: {list(results.keys())}")
    else:
        print("No results available.")

if __name__ == "__main__":
    main()