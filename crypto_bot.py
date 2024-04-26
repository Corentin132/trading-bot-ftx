import pandas as pd 
import ta 
import ftx
import time
from math import *
from datetime import date


account_name = "name"
pair_symbol = "ETH/USD"
fiat_symbol = "USD"
crypto_symbol = "ETH"
my_truncate = 4

client = ftx.FtxClient(api_key="", api_secret="", subaccount_name=account_name)

data = client.get_historical_data(market_name=pair_symbol,resolution=3600, limit=650, start_time=float(round(time.time())-3600*650), end_time=float(round(time.time())))

df = pd.DataFrame(data)

def buy_condition(row): 
    print("test 1 =",row['TRIX_HISTO'].iloc[0])
    print("test 2 =",row['TRIX_HISTO'].iloc[-1])
    if row['EMA200'].iloc[-1]>row['EMA600'].iloc[-1] and row['TRIX_HISTO'].iloc[-1] >0  and row['STOCH_RSI'].iloc[-1] <0.80 :
    # if row['EMA200'] > row['EMA600']  and row['STOCH_RSI'] <0.80:
    # if  row['EMA20']> row['EMA40'] and row['CHOP']<50 and row['VMC_WAVE1']<0 and row['VMC_WAVE2']<0 and row['VMC_WAVE2'] -row['VMC_WAVE1'] >0  and previous_row['VMC_WAVE2'] - previous_row['VMC_WAVE1'] < 0  and row['STOCH_RSI'] <0.80 and row['MONEY_FLOW']>0 :
    # if row['EMA100']>row['EMA200'] and row['AO'] >= 0 and previous_row['AO'] > row['AO'] and row['WillR'] < -85 :
    # if row['super_trend_direction1'] + row['super_trend_direction2']+row['super_trend_direction3'] ==3  and row['STOCH_RSI']<0.80 and row['close']>row['EMA200'] :
        return True
    else: 
        return False

def sell_condition(row): 
 

    if row['TRIX_HISTO'].iloc[-1]<0 and row['STOCH_RSI'].iloc[-1]>0.20:
    # if row['EMA200'] < row['EMA600'] and row['STOCH_RSI']>0.20:         
    # if row['VMC_WAVE1'] >0 and row['VMC_WAVE2'] >0 and row['VMC_WAVE2'] -row['VMC_WAVE1'] < 0  and previous_row['VMC_WAVE2'] - previous_row['VMC_WAVE1'] > 0  and row['STOCH_RSI'] >0.20  :
    # if ((row['AO'] < 0 and row['STOCH_RSI'] > 0.20) or (row['WillR'] > -10)):
    # if row['super_trend_direction1'] + row['super_trend_direction2']+row['super_trend_direction3'] <3 and row['STOCH_RSI']>0.25:
        return True

    else: 
        return False

def get_balance(myclient, coin):
    jsonBalance = myclient.get_balances()
    if jsonBalance == []: 
        return 0
    pandaBalance = pd.DataFrame(jsonBalance)
    if pandaBalance.loc[pandaBalance['coin'] == coin].empty: 
        return 0
    else: 
        return float(pandaBalance.loc[pandaBalance['coin'] == coin]['total'])

def truncate(n, decimal = 0):
    r = floor(float(n)*10**decimal)/10**decimal
    return str(r) 

actual_price = df['close'].iloc[-1]
fiat_amount = get_balance(client, fiat_symbol)
crypto_amount = get_balance(client, crypto_symbol)

#  Define my indicator 

# EMA indicator 
df['EMA200'] = ta.trend.ema_indicator(df['close'],window = 200)
df['EMA600'] = ta.trend.ema_indicator(df['close'], window =600)
# -- Trix Indicator --
trixLength = 9
trixSignal = 21
df['TRIX'] = ta.trend.ema_indicator(ta.trend.ema_indicator(ta.trend.ema_indicator(close=df['close'], window=trixLength), window=trixLength), window=trixLength)
df['TRIX_PCT'] = df['TRIX'].pct_change()*100
df['TRIX_SIGNAL'] = ta.trend.sma_indicator(df['TRIX_PCT'],trixSignal)
df['TRIX_HISTO'] = df['TRIX_PCT'] - df['TRIX_SIGNAL']
# -- Stochasitc RSI --
stochWindow = 14
df['STOCH_RSI'] = ta.momentum.stochrsi(close=df['close'], window=stochWindow)

# buy order or sell order
usdt = fiat_amount
starter = usdt
eth = crypto_amount

buy_price =0
sell_price = 0
positif_trade=0
worst_trade = 0

previous_row = previous_row = df.iloc[0].copy()
frais = 0 

checkeur =0
if (buy_condition(df) and usdt > 5 ):
    quantity_buy = truncate(float(fiat_amount)/actual_price,my_truncate)
    buy_order = client.place_order(
        market=pair_symbol,
        side= 'buy',price= None,
        size= quantity_buy, 
        type='market'
        )
    print("BUY Order passed ==> ", buy_order)

elif (sell_condition(df) and eth > 0.0001):        
    sellOrder = client.place_order(
        market=pair_symbol,side="sell",price=None,size=truncate(eth,my_truncate),type="market"
    )
    print("SELL Order passed ==> ", sellOrder)
   
else: 
    print(" PAS DE SIGNAL D'ACHAT DETECTER :(")



# iloc -1 à l'origine 

if( checkeur ==1):
    print("---------------- RESULT ------------------------")
    final_result = usdt + eth *df['close']
    print("Final result : ", final_result, ' $')
    print(" ETH in the wallet : ", eth)
    pct_result = (final_result* starter)/100 -100
    print(" Gain ou perte de de : ",pct_result , " %")

    print("BUY and Hold result : ", 100 /df['close'].iloc[0] * df['close'].iloc[-1], "$ " )

    print(" Good trade : ", positif_trade)
    print(" Bad trade : ", worst_trade)
    if (positif_trade > 1 or worst_trade > 1):
        pct_good_trade = (positif_trade/(worst_trade+positif_trade))*100
        print(" Pourcentage de la stratégie : ", pct_good_trade)

    print(" FTX MA VOLER : ", frais, " $ ")
# Conditions to buy 

# Conditions to sell

