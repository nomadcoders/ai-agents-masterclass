import yfinance as yf
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm


MODEL = LiteLlm(model="openai/gpt-4o")


def get_company_info(ticker: str) -> str:
    """
    Retrieves basic company information for a given stock ticker.

    This tool fetches fundamental company details including the official company name,
    industry classification, and sector categorization from Yahoo Finance.

    Args:
        ticker (str): The stock ticker symbol (e.g., 'AAPL' for Apple Inc.)

    Returns:
        dict: A dictionary containing:
            - ticker (str): The input ticker symbol
            - success (bool): True if the operation was successful
            - company_name (str): Full legal name of the company
            - industry (str): Specific industry classification
            - sector (str): Broader sector categorization

    Example:
        >>> get_company_info('MSFT')
        {
            'ticker': 'MSFT',
            'success': True,
            'company_name': 'Microsoft Corporation',
            'industry': 'Software - Infrastructure',
            'sector': 'Technology'
        }
    """
    stock = yf.Ticker(ticker)
    info = stock.info
    return {
        "ticker": ticker,
        "success": True,
        "company_name": info.get("longName", "NA"),
        "industry": info.get("industry", "NA"),
        "sector": info.get("sector", "NA"),
    }


def get_stock_price(ticker: str, period: str) -> str:
    """
    Fetches historical stock price data and current trading price for a given ticker.

    This tool retrieves both the current market price and historical price data
    over a specified time period, including open, high, low, close prices and volume.

    Args:
        ticker (str): Stock ticker symbol (e.g., 'AAPL' for Apple Inc.)
        period (str): Time period for historical data. Valid options:
            - '1d': 1 day
            - '5d': 5 days
            - '1mo': 1 month (default)
            - '3mo': 3 months
            - '6mo': 6 months
            - '1y': 1 year
            - '2y': 2 years
            - '5y': 5 years
            - '10y': 10 years
            - 'ytd': Year to date
            - 'max': Maximum available data

    Returns:
        dict: A dictionary containing:
            - ticker (str): The input ticker symbol
            - success (bool): True if the operation was successful
            - history (str): JSON-formatted historical price data with OHLCV
            - current_price (float): Current market price of the stock

    Example:
        >>> get_stock_price('TSLA', '3mo')
        {
            'ticker': 'TSLA',
            'success': True,
            'history': '{"Open": {...}, "High": {...}, ...}',
            'current_price': 245.67
        }
    """
    stock = yf.Ticker(ticker)
    info = stock.info
    history = stock.history(period=period)
    return {
        "ticker": ticker,
        "success": True,
        "history": history.to_json(),
        "current_price": info.get("currentPrice"),
    }


def get_financial_metrics(ticker: str) -> str:
    """
    Retrieves key financial metrics and valuation ratios for stock analysis.

    This tool fetches essential financial indicators that help assess a company's
    valuation, profitability, dividend policy, and market risk characteristics.

    Args:
        ticker (str): Stock ticker symbol (e.g., 'AAPL' for Apple Inc.)

    Returns:
        dict: A dictionary containing:
            - ticker (str): The input ticker symbol
            - success (bool): True if the operation was successful
            - market_cap (float): Total market capitalization in USD
            - pe_ratio (float): Trailing Price-to-Earnings ratio (price/earnings per share)
            - dividend_yield (float): Annual dividend yield as a percentage (0.02 = 2%)
            - beta (float): Stock's beta coefficient measuring volatility vs market

    Notes:
        - Market Cap: Represents company's total value (shares * price)
        - P/E Ratio: Lower may indicate undervalued; higher may indicate growth expectations
        - Dividend Yield: Annual dividends as percentage of stock price
        - Beta: <1 means less volatile than market; >1 means more volatile

    Example:
        >>> get_financial_metrics('JNJ')
        {
            'ticker': 'JNJ',
            'success': True,
            'market_cap': 385000000000,
            'pe_ratio': 15.2,
            'dividend_yield': 0.031,
            'beta': 0.65
        }
    """
    stock = yf.Ticker(ticker)
    info = stock.info
    return {
        "ticker": ticker,
        "success": True,
        "market_cap": info.get("marketCap", "NA"),
        "pe_ratio": info.get("trailingPE", "NA"),
        "dividend_yield": info.get("dividendYield", "NA"),
        "beta": info.get("beta", "NA"),
    }


data_analyst = LlmAgent(
    name="DataAnalyst",
    model=MODEL,
    description="Gathers and analyzes basic stock market data using multiple focused tools",
    instruction="""
    You are a Data Analyst who gathers stock information using 4 specialized tools:
    
    1. **get_company_info(ticker)** - Learn about the company (name, sector, industry)
    2. **get_stock_price(ticker, period)** - Get current pricing and trading ranges
    3. **get_financial_metrics(ticker)** - Check key financial ratios  
    
    Use multiple focused tools to gather different types of data.
    Explain what each tool provides and present the information clearly.
    """,
    tools=[
        get_company_info,
        get_stock_price,
        get_financial_metrics,
    ],
    output_key="data_analyst_result",
)
