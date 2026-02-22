
def test_yfinance_info_fetch():
    import yfinance as yf
    stock = yf.Ticker("AAPL")
    info = stock.info
    
    assert info.get('symbol') == 'AAPL'
    assert 'longName' in info
    assert 'exchange' in info
    
    # Calculate IPO year
    ipo_year = None
    first_trade_millis = info.get('firstTradeDateMilliseconds')
    first_trade_epoch = info.get('firstTradeDateEpochUtc')
    if first_trade_millis:
        from datetime import datetime as dt
        ipo_year = dt.fromtimestamp(first_trade_millis / 1000).year
    elif first_trade_epoch:
        from datetime import datetime as dt
        ipo_year = dt.fromtimestamp(first_trade_epoch).year
    
    assert ipo_year is not None
    assert 1970 <= ipo_year <= 2026
