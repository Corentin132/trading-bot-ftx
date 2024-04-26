from curses import window
from tracemalloc import start
import pandas as pd 
from binance.client import Client
import ta 
import numpy as np

# VMC setup


class VMC():
    """ VuManChu Cipher B + Divergences 
        Args:
            high(pandas.Series): dataset 'High' column.
            low(pandas.Series): dataset 'Low' column.
            close(pandas.Series): dataset 'Close' column.
            wtChannelLen(int): n period.
            wtAverageLen(int): n period.
            wtMALen(int): n period.
            rsiMFIperiod(int): n period.
            rsiMFIMultiplier(int): n period.
            rsiMFIPosY(int): n period.
    """
    def __init__(
        self: pd.Series,
        high: pd.Series,
        low: pd.Series,
        close: pd.Series,
        open: pd.Series,
        wtChannelLen: int = 9,
        wtAverageLen: int = 12,
        wtMALen: int = 3,
        rsiMFIperiod: int = 60,
        rsiMFIMultiplier: int = 150,
        rsiMFIPosY: int = 2.5
    ) -> None:
        self._high = high
        self._low = low
        self._close = close
        self._open = open
        self._wtChannelLen = wtChannelLen
        self._wtAverageLen = wtAverageLen
        self._wtMALen = wtMALen
        self._rsiMFIperiod = rsiMFIperiod
        self._rsiMFIMultiplier = rsiMFIMultiplier
        self._rsiMFIPosY = rsiMFIPosY
        self._run()
        self.wave_1()

    def _run(self) -> None:
        try:
            self._esa = ta.trend.ema_indicator(
                close=self._close, window=self._wtChannelLen)
        except Exception as e:
            print(e)
            raise

        self._esa = ta.trend.ema_indicator(
            close=self._close, window=self._wtChannelLen)
        self._de = ta.trend.ema_indicator(
            close=abs(self._close - self._esa), window=self._wtChannelLen)
        self._rsi = ta.trend.sma_indicator(self._close, self._rsiMFIperiod)
        self._ci = (self._close - self._esa) / (0.015 * self._de)

    def wave_1(self) -> pd.Series:
        """VMC Wave 1 
        Returns:
            pandas.Series: New feature generated.
        """
        wt1 = ta.trend.ema_indicator(self._ci, self._wtAverageLen)
        return pd.Series(wt1, name="wt1")

    def wave_2(self) -> pd.Series:
        """VMC Wave 2
        Returns:
            pandas.Series: New feature generated.
        """
        wt2 = ta.trend.sma_indicator(self.wave_1(), self._wtMALen)
        return pd.Series(wt2, name="wt2")

    def money_flow(self) -> pd.Series:
        """VMC Money Flow
            Returns:
            pandas.Series: New feature generated.
        """
        mfi = ((self._close - self._open) /
                (self._high - self._low)) * self._rsiMFIMultiplier
        rsi = ta.trend.sma_indicator(mfi, self._rsiMFIperiod)
        money_flow = rsi - self._rsiMFIPosY
        return pd.Series(money_flow, name="money_flow")
 
def chop(high, low, close, window=14):
        """ Chopiness index
            Args:
                high(pd.Series): dataframe 'high' columns,
                low(pd.Series): dataframe 'low' columns,
                close(pd.Series): dataframe 'close' columns,
                window(int): the window length for the chopiness index,
            Returns:
                pd.Series: Chopiness index
        """
        tr1 = pd.DataFrame(high - low).rename(columns = {0:'tr1'})
        tr2 = pd.DataFrame(abs(high - close.shift(1))).rename(columns = {0:'tr2'})
        tr3 = pd.DataFrame(abs(low - close.shift(1))).rename(columns = {0:'tr3'})
        frames = [tr1, tr2, tr3]
        tr = pd.concat(frames, axis = 1, join = 'inner').dropna().max(axis = 1)
        atr = tr.rolling(1).mean()
        highh = high.rolling(window).max()
        lowl = low.rolling(window).min()
        chop = 100 * np.log10((atr.rolling(window).sum()) / (highh - lowl)) / np.log10(window)
        return pd.Series(chop, name="CHOP")
def buy_condition(row, previous_row): 
    if row['EMA200']>row['EMA600'] and row['TRIX_HISTO'] >=0  and row['STOCH_RSI'] <0.80 :
    # if row['EMA200'] > row['EMA600']  and row['STOCH_RSI'] <0.80:
    # if  row['EMA20']> row['EMA40'] and row['CHOP']<50 and row['VMC_WAVE1']<0 and row['VMC_WAVE2']<0 and row['VMC_WAVE2'] -row['VMC_WAVE1'] >0  and previous_row['VMC_WAVE2'] - previous_row['VMC_WAVE1'] < 0  and row['STOCH_RSI'] <0.80 and row['MONEY_FLOW']>0 :
    # if row['EMA100']>row['EMA200'] and row['AO'] >= 0 and previous_row['AO'] > row['AO'] and row['WillR'] < -85 :
    # if row['super_trend_direction1'] + row['super_trend_direction2']+row['super_trend_direction3'] ==3  and row['STOCH_RSI']<0.80 and row['close']>row['EMA200'] :
        return True
    else: 
        return False

def sell_condition(row, previous_row): 
    if row['TRIX_HISTO']<0 and row['STOCH_RSI']>0.20:
    # if row['EMA200'] < row['EMA600'] and row['STOCH_RSI']>0.20:         
    # if row['VMC_WAVE1'] >0 and row['VMC_WAVE2'] >0 and row['VMC_WAVE2'] -row['VMC_WAVE1'] < 0  and previous_row['VMC_WAVE2'] - previous_row['VMC_WAVE1'] > 0  and row['STOCH_RSI'] >0.20  :
    # if ((row['AO'] < 0 and row['STOCH_RSI'] > 0.20) or (row['WillR'] > -10)):
    # if row['super_trend_direction1'] + row['super_trend_direction2']+row['super_trend_direction3'] <3 and row['STOCH_RSI']>0.25:
        return True

    else: 
        return False

    
klinesT = Client().get_historical_klines("ETHUSDT",Client.KLINE_INTERVAL_1HOUR,"01 january 2007")
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
print(df)

# #  Define my indicator 


# # EMA indicator 
# df['EMA20'] = ta.trend.ema_indicator(df['close'],window = 20)

# df['EMA40'] = ta.trend.ema_indicator(df['close'],window = 40)

# df['EMA100'] = ta.trend.ema_indicator(df['close'],window = 100)

# df['EMA200'] = ta.trend.ema_indicator(df['close'],window = 200)
# df['EMA400'] = ta.trend.ema_indicator(df['close'],window = 400)

# df['EMA600'] = ta.trend.ema_indicator(df['close'], window =600)


# # SMA Indicator 
# df['SMA200'] = ta.trend.sma_indicator(df['close'],window = 200)
# df['SMA600'] = ta.trend.sma_indicator(df['close'], window =600)

# # -- Trix Indicator --
# trixLength = 9
# trixSignal = 21
# df['TRIX'] = ta.trend.ema_indicator(ta.trend.ema_indicator(ta.trend.ema_indicator(close=df['close'], window=trixLength), window=trixLength), window=trixLength)
# df['TRIX_PCT'] = df["TRIX"].pct_change()*100
# df['TRIX_SIGNAL'] = ta.trend.sma_indicator(df['TRIX_PCT'],trixSignal)
# df['TRIX_HISTO'] = df['TRIX_PCT'] - df['TRIX_SIGNAL']

# # -- Stochasitc RSI --


# # -- VMC --
# df['HLC3'] = (df['high'] +df['close'] + df['low'])/3
# vmc = VMC(high =df['high'],low = df['low'],close=df['HLC3'],open=df['open'])
# df['VMC_WAVE1'] = vmc.wave_1()
# df['VMC_WAVE2'] = vmc.wave_2()
# vmc = VMC(high =df['high'],low = df['low'],close=df['close'],open=df['open'])
# df['MONEY_FLOW'] = vmc.money_flow()

# #------  CHOP  ------------
# chop_window = 14
# df["CHOP"] = chop(df['high'],df['low'],df['close'],window=chop_window)


# # ----------------------------------- BIG WILL STRAT ----------------------------------------------------------------

# aoParam1 = 6
# aoParam2 = 22
# stochWindow = 14
# willWindow = 14
#  # -- Indicators, you can edit every value --
# df['AO'] = ta.momentum.awesome_oscillator(df['high'],df['low'],window1=aoParam1,window2=aoParam2)
# df['EMA100'] =ta.trend.ema_indicator(close=df['close'], window=100) 
# df['EMA200'] =ta.trend.ema_indicator(close=df['close'], window=200)
# df['STOCH_RSI'] = ta.momentum.stochrsi(close=df['close'], window=stochWindow)   
# df['WillR'] = ta.momentum.williams_r(high=df['high'], low=df['low'], close=df['close'], lbp=willWindow)

# # ----------------------------------- BIG WILL STRAT ----------------------------------------------------------------


# #-------------------------- SUPER TREND ----------------------------------------------------------------
# class SuperTrend():
#     def __init__(
#         self,
#         high,
#         low,
#         close,
#         atr_window=10,
#         atr_multi=3
#     ):
#         self.high = high
#         self.low = low
#         self.close = close
#         self.atr_window = atr_window
#         self.atr_multi = atr_multi
#         self._run()
        
#     def _run(self):
#         # calculate ATR
#         price_diffs = [self.high - self.low, 
#                     self.high - self.close.shift(), 
#                     self.close.shift() - self.low]
#         true_range = pd.concat(price_diffs, axis=1)
#         true_range = true_range.abs().max(axis=1)
#         # default ATR calculation in supertrend indicator
#         atr = true_range.ewm(alpha=1/self.atr_window,min_periods=self.atr_window).mean() 
#         # atr = ta.volatility.average_true_range(high, low, close, atr_period)
#         # df['atr'] = df['tr'].rolling(atr_period).mean()
        
#         # HL2 is simply the average of high and low prices
#         hl2 = (self.high + self.low) / 2
#         # upperband and lowerband calculation
#         # notice that final bands are set to be equal to the respective bands
#         final_upperband = upperband = hl2 + (self.atr_multi * atr)
#         final_lowerband = lowerband = hl2 - (self.atr_multi * atr)
        
#         # initialize Supertrend column to True
#         supertrend = [True] * len(self.close)
        
#         for i in range(1, len(self.close)):
#             curr, prev = i, i-1
            
#             # if current close price crosses above upperband
#             if self.close[curr] > final_upperband[prev]:
#                 supertrend[curr] = True
#             # if current close price crosses below lowerband
#             elif self.close[curr] < final_lowerband[prev]:
#                 supertrend[curr] = False
#             # else, the trend continues
#             else:
#                 supertrend[curr] = supertrend[prev]
                
#                 # adjustment to the final bands
#                 if supertrend[curr] == True and final_lowerband[curr] < final_lowerband[prev]:
#                     final_lowerband[curr] = final_lowerband[prev]
#                 if supertrend[curr] == False and final_upperband[curr] > final_upperband[prev]:
#                     final_upperband[curr] = final_upperband[prev]

#             # to remove bands according to the trend direction
#             if supertrend[curr] == True:
#                 final_upperband[curr] = np.nan
#             else:
#                 final_lowerband[curr] = np.nan
                
#         self.st = pd.DataFrame({
#             'Supertrend': supertrend,
#             'Final Lowerband': final_lowerband,
#             'Final Upperband': final_upperband
#         })
        
#     def super_trend_upper(self):
#         return self.st['Final Upperband']
        
#     def super_trend_lower(self):
#         return self.st['Final Lowerband']
        
#     def super_trend_direction(self):
#         return self.st['Supertrend']

# super_trend = SuperTrend(df['high'],df['low'], df['close'], 20, 3)
# df['super_trend_direction1'] = super_trend.super_trend_direction()

# super_trend = SuperTrend(df['high'],df['low'], df['close'], 20, 4)
# df['super_trend_direction2'] = super_trend.super_trend_direction()

# super_trend = SuperTrend(df['high'],df['low'], df['close'], 15, 5)
# df['super_trend_direction3'] = super_trend.super_trend_direction()
# #-------------------------- SUPER TREND ----------------------------------------------------------------


# # simulation pour voir si c'est worth 

# usdt = 100
# starter = usdt
# eth = 0

# buy_price =0
# sell_price = 0
# positif_trade=0
# worst_trade = 0
# lastIndex = df.first_valid_index()
# previous_row = previous_row = df.iloc[0].copy()
# frais = 0 
# for index, row  in df.iterrows():

#     if (buy_condition(row, previous_row) and usdt > 1 ):
#         eth = usdt/ row['close']

#         eth = eth - (0.07/100)*eth 
#         usdt =0
#         buy_price = row['close']
#         # print( "BUY ETH at",row['close'] ,'$ the ',index )
#     elif (sell_condition(row, previous_row) and eth > 0.0001):
#         usdt = eth * row['close']
#         frais += (0.07/100) * usdt
#         usdt = usdt - (0.07/100)* usdt
        
#         eth = 0
#         sell_price = row['close']
#         # print("Sell ETH at ", row['close'] ,'$ the ',index)
       
#         if sell_price - buy_price > 0:
#             positif_trade += 1;
#         else: 
#             worst_trade +=1;

#     lastIndex = index
#     previous_row = row


# # iloc -1 à l'origine 

# print("---------------- RESULT ------------------------")
# final_result = usdt + eth *row['close']
# print("Final result : ", final_result, ' $')
# print(" ETH in the wallet : ", eth)
# pct_result = (final_result* starter)/100 -100
# print(" Gain ou perte de de : ",pct_result , " %")

# print("BUY and Hold result : ", 100 /df['close'].iloc[0] * df['close'].iloc[-1], "$ " )

# print(" Good trade : ", positif_trade)
# print(" Bad trade : ", worst_trade)
# pct_good_trade = (positif_trade/(worst_trade+positif_trade))*100
# print(" Pourcentage de la stratégie : ", pct_good_trade)

# print(" FTX MA VOLER : ", frais, " $ ")
# # Conditions to buy 

# # Conditions to sell

