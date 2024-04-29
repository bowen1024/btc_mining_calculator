import pandas as pd
import streamlit as st
from datetime import datetime, timedelta

from utils import get_btc_price, get_block_difficulty, get_avg_block_fee_24h

def update_value(key, update_function, interval):
    if key not in st.session_state or 'last_update_' + key not in st.session_state:
        st.session_state[key] = update_function()
        st.session_state['last_update_' + key] = datetime.utcnow()
    elif datetime.utcnow() - st.session_state['last_update_' + key] > interval:
        st.session_state[key] = update_function()
        st.session_state['last_update_' + key] = datetime.utcnow()

# Update each value using the update_value function with corresponding intervals
update_value('btc_price', get_btc_price, timedelta(hours=1))
update_value('avg_block_fee_24h', get_avg_block_fee_24h, timedelta(days=1))
update_value('block_difficulty', get_block_difficulty, timedelta(days=1))

st.header('挖矿收益计算', divider='rainbow')

# User inputs
btc_price = st.number_input('比特币价格（$）', value=st.session_state['btc_price'])
block_fee = st.number_input('平均矿工费24h（BTC）', value=st.session_state['avg_block_fee_24h'])
block_difficulty = st.number_input('区块难度 (T)', value=st.session_state['block_difficulty'])

# Number of block per day, 1 day is of 86400 seconds, 10 minutes per block
Blocks_Per_Day = 86400 / 600

# Network hash rate, in TH/s
Network_Hash_Rate = block_difficulty * (2**32) / 600

# Revenue for 1 TH/s per day, in BTC
revenue_per_day_btc = (3.125 + block_fee) * Blocks_Per_Day / Network_Hash_Rate

# Revenue for 1 TH/s per day, in USD
revenue_per_day_usd = revenue_per_day_btc * btc_price

st.markdown('---')
col1, col2, col3 = st.columns(3)
col1.metric(label='__每T收益/天(BTC)__', value=f'{revenue_per_day_btc:.8f}')
col2.metric(label='__每T收益/天($)__', value=f'{revenue_per_day_usd:.4f}')
st.markdown('---')

# Mining model selection
mining_model = st.selectbox('矿机型号', options=['S19', 'T21', '自定义'])

# Hash rate and power based on the model or custom input
if mining_model == 'S19':
    hash_rate = 100
    power = 3250
elif mining_model == 'T21':
    hash_rate = 190
    power = 3610
else:
    hash_rate = 0
    power = 0

hash_rate = st.number_input('哈希率 (T)', value=hash_rate)
power = st.number_input('功率 (W)', value=power)

# hosting unit price, in usd
hosting_unit_price = st.number_input('电费/度 ($)', value=0.07)

# Actual electricity cost factor
electricity_cost_factor = st.number_input('实际电费系数', value=1.05)

# Revenue for machine per day, in USD
revenue_machine_per_day_usd = revenue_per_day_usd * hash_rate

# Hosting fee for machine per day, in USD
hosting_fee_per_day = power / 1000 * 24 * hosting_unit_price * electricity_cost_factor

# Hosting Fee Ratio
if revenue_machine_per_day_usd != 0:
    hosting_fee_ratio = hosting_fee_per_day / revenue_machine_per_day_usd
else:
    hosting_fee_ratio = 0

st.markdown('---')
col1, col2, col3 = st.columns(3)
col1.metric(label="__机器收益/天($)__", value=f"{revenue_machine_per_day_usd:.4f}")
col2.metric(label="__机器电费/天($)__", value=f"{hosting_fee_per_day:.4f}")
col3.metric(label="__收益电费比__", value=f"{hosting_fee_ratio:.2f}")
st.markdown('---')
