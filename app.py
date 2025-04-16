import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.set_page_config(page_title="Stock Market Scanner", layout="wide")
st.title("Stock Market Pattern Scanner with Candlestick & Signals")

ticker = st.text_input("Enter Stock Ticker (e.g., AAPL, RELIANCE.NS)", "AAPL")
period = st.selectbox("Select Period", ["7d", "1mo", "3mo", "6mo", "1y"], index=0)

if st.button("Scan"):
    try:
        data = yf.download(ticker, period=period, interval="1d")
        if data.empty:
            st.error("No data found. Check the ticker symbol.")
        else:
            data.dropna(inplace=True)
            data['RSI'] = ta.rsi(data['Close'], length=14)
            data['MACD_Line'], data['MACD_Signal'] = ta.macd(data['Close'])[['MACD_12_26_9', 'MACDs_12_26_9']].T.values

            buy_signals = []
            sell_signals = []
            position = False

            for i in range(1, len(data)):
                if data['RSI'][i] < 30 and data['MACD_Line'][i] > data['MACD_Signal'][i] and not position:
                    buy_signals.append(data['Close'][i])
                    sell_signals.append(None)
                    position = True
                elif data['RSI'][i] > 70 and data['MACD_Line'][i] < data['MACD_Signal'][i] and position:
                    sell_signals.append(data['Close'][i])
                    buy_signals.append(None)
                    position = False
                else:
                    buy_signals.append(None)
                    sell_signals.append(None)

            data['Buy'] = buy_signals
            data['Sell'] = sell_signals

            # Candlestick chart with signals
            fig = go.Figure(data=[go.Candlestick(x=data.index,
                                                 open=data['Open'],
                                                 high=data['High'],
                                                 low=data['Low'],
                                                 close=data['Close'],
                                                 name='Candles')])

            fig.add_trace(go.Scatter(x=data.index, y=data['Buy'],
                                     mode='markers', name='Buy Signal',
                                     marker=dict(color='green', size=10, symbol='triangle-up')))

            fig.add_trace(go.Scatter(x=data.index, y=data['Sell'],
                                     mode='markers', name='Sell Signal',
                                     marker=dict(color='red', size=10, symbol='triangle-down')))

            fig.update_layout(title=f"{ticker} - Candlestick with Buy/Sell Signals",
                              xaxis_title="Date", yaxis_title="Price",
                              xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Error occurred: {str(e)}")