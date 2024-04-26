from curses import window
from tracemalloc import start
import pandas as pd 
from binance.client import Client
import ta 
import numpy as np


def buy_condition(row, previous_row): 
    if row['EMA100']>row['EMA200'] and row['AO'] >= 0 and previous_row['AO'] > row['AO'] and row['WillR'] < -85 :
        return True
    else: 
        return False

def sell_condition(row, previous_row): 
    if (row['AO'] < 0 and row['STOCH_RSI'] > 0.20 or row['WillR'] > -10):
        return True

    else: 
        return False

    
klinesT = Client().get_historical_klines("ETHUSDT",Client.KLINE_INTERVAL_1HOUR,"01 January 2007")
df = pd.DataFrame(klinesT, columns =['timestamp', 'open','high','low','close','volume','close_time','quote_av','trades','tb_base_av','tb_quote_av','ignore'])

# clear data set
del df['ignore']
del df['close_time']
del df['quote_av']
del df['trades']
del df['tb_base_av']
del df['tb_quote_av']

df['close'] = pd.to_numeric(df['close'])
df['high'] = pd.to_numeric(df['high'])
df['low'] = pd.to_numeric(df['low'])
df['open'] = pd.to_numeric(df['open'])


#clear date form 
df = df.set_index(df['timestamp'])
df.index = pd.to_datetime(df.index, unit="ms")

del df['timestamp']


#  Define my indicator 


# EMA indicator 

df['EMA100'] = ta.trend.ema_indicator(df['close'],window = 100)

df['EMA200'] = ta.trend.ema_indicator(df['close'],window = 200)


# SMA Indicator 
df['SMA200'] = ta.trend.sma_indicator(df['close'],window = 200)
df['SMA600'] = ta.trend.sma_indicator(df['close'], window =600)


# ----------------------------------- BIG WILL STRAT ----------------------------------------------------------------

aoParam1 = 6
aoParam2 = 22
stochWindow = 14
willWindow = 14
 # -- Indicators, you can edit every value --
df['AO'] = ta.momentum.awesome_oscillator(df['high'],df['low'],window1=aoParam1,window2=aoParam2)
df['EMA100'] =ta.trend.ema_indicator(close=df['close'], window=100) 
df['EMA200'] =ta.trend.ema_indicator(close=df['close'], window=200)
df['STOCH_RSI'] = ta.momentum.stochrsi(close=df['close'], window=stochWindow)
df['WillR'] = ta.momentum.williams_r(high=df['high'], low=df['low'], close=df['close'], lbp=willWindow)

# ----------------------------------- BIG WILL STRAT ----------------------------------------------------------------




# simulation pour voir si c'est worth 

usdt = 100
starter = usdt
eth = 0

buy_price =0
sell_price = 0
positif_trade=0
worst_trade = 0
lastIndex = df.first_valid_index()
previous_row = previous_row = df.iloc[0].copy()
frais = 0 
for index, row  in df.iterrows():
    if (buy_condition(row, previous_row) and usdt > 1 ):
        eth = usdt/ row['close']

        eth = eth - (0.07/100)*eth 
        usdt =0
        buy_price = row['close']
        print( "BUY ETH at",row['close'] ,'$ the ',index )
    elif (sell_condition(row, previous_row)  and eth > 0.0001):
        usdt = eth * row['close']
        frais += (0.07/100) * usdt
        usdt = usdt - (0.07/100)* usdt
        
        eth = 0
        sell_price = row['close']
        print("Sell ETH at ", row['close'] ,'$ the ',index)
       
        if sell_price - buy_price > 0:
            positif_trade += 1;
        else: 
            worst_trade +=1;

    # lastIndex = index

    previous_row = row


# iloc -1 à l'origine 

print("---------------- RESULT ------------------------")
final_result = usdt + eth *row['close']
print("Final result : ", final_result, ' $')
print(" ETH in the wallet : ", eth)
pct_result = (final_result* starter)/100 -100
print(" Gain ou perte de de : ",pct_result , " %")

print("BUY and Hold result : ", 100 /df['close'].iloc[0] * df['close'].iloc[-1], "$ " )

print(" Good trade : ", positif_trade)
print(" Bad trade : ", worst_trade)
pct_good_trade = (positif_trade/(worst_trade+positif_trade))*100
print(" Pourcentage de la stratégie : ", pct_good_trade)

print(" FTX MA VOLER : ", frais, " $ ")
# Conditions to buy 

# Conditions to sell

