# new-stock-price-feeder.py
# simulates a real-time stock feed
# ----------------------------------------------------------------------------
from twelvedata import TDClient
import sys
import pandas as pd
import time, datetime, sys
from dateutil.relativedelta import relativedelta
import os, pathlib
# ----------------------------------------------------------------------------
# Historical Daily Prices

# you will need a twelvedata account and an api_key. I stored in repo secrets
api_key = os.getenv('TWELVEDATA_KEY')
if not api_key:
    raise ValueError("API key not found. Ensure TWELVE_DATA_KEY is set.")
td = TDClient(apikey=api_key)

# get the last 4 years of data
end_date = datetime.now().date()
start_date = end_date - relativedelta(years=4)
symbols = ["AAPL", "MSFT", "IBM"]
past_df = []

# query API for four years of daily data for each symbol
for i, symbol in enumerate(symbols):
    past_df[symbol] = td.time_series(
        symbol=symbol,
        interval="1day",
        timezone="America/New_York",
        start_date=start_date,
        end_date=end_date,
        outputsize=1500
    ).as_pandas()

    # don't call too many times within the minute
    if len(symbols > 8) and i % 8 == 0:
        time.sleep(60)

# we want the max of the init dates, and the min of the last dates
init_date = max(stock_data[symbol].index.min().date() for symbol in symbols)
last_date = min(stock_data[symbol].index.max().date() for symbol in symbols)

init_delay_seconds = 30
interval = 5

# scale the stock prices with respect to AAPL
scaled_df = []
for symbol in symbols:
    try:
        scaler = past_df['AAPL'].loc[init_date]/past_df[symbol].loc[init_date]
        scaled_df[symbol] = past_df[symbol]*scaler
    except KeyError:
        print("Could not scale the data.")
        scaled_df = past_df

# print processing error messages
print ('Sending daily prices from %10s to %10s ...' % (str(init_date)[:10], str(last_date)[:10]), flush=True, file=sys.stderr)
print ("... each day's data sent every %d seconds ..." % (interval), flush=True, file=sys.stderr)
print ('... beginning in %02d seconds ...' % (init_delay_seconds), flush=True, file=sys.stderr)
print ("... prices adjusted to match AAPL prices on %10s ..."  % (init_date), flush=True, file=sys.stderr)

# visually display the progress
from tqdm import tqdm
for left in tqdm(range(init_delay_seconds)):
    time.sleep(0.5)

for date in list(scaled_df.index):
    # print the date
    print_line = f'{str(date)[:10]}'
    for symbol in symbols:
        # and the price for each symbol
        print_line += f'\t{scaled_df[symbol][date]:.4f}'
    print(print_line, flush=True)
    time.sleep(float(interval))

exit(0)

# ----------------------------------------------------------------------------
# Real Time Prices
import datetime, time
from yahoo_fin import stock_info

for t in range(10):
    now = datetime.datetime.now()
    for symbol in symbols:
        price = stock_info.get_live_price(symbol)
        prices.append(f'{price:.4f}')
    print(f'{str(now)[:19]}\t' + '\t'.join(prices))
    time.sleep(5.0)

exit(0)
