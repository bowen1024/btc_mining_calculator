import pandas as pd
import streamlit as st
from datetime import datetime, timedelta

from utils import get_btc_price, get_block_difficulty, get_avg_block_fee_24h, get_usd_rmb

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
update_value('usd_rmb', get_usd_rmb, timedelta(days=1))

st.header('挖矿收益计算', divider='rainbow')

# User inputs
btc_price = st.number_input('比特币价格 ($)',value=st.session_state['btc_price'], min_value=0, step=1_000)
block_fee = st.number_input('24h平均矿工费 (BTC)', value=st.session_state['avg_block_fee_24h'],
                            min_value=0., format='%0.3f', step=0.1)
block_difficulty = st.number_input('区块难度 (T)', value=st.session_state['block_difficulty'],
                                   min_value=0., step=1.)

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
col2.metric(label='__每T收益/天($)__', value=f'{revenue_per_day_usd:.3f}')
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

hash_rate = st.number_input('哈希率 (T)', value=hash_rate, step=10)
power = st.number_input('功率 (W)', value=power, step=50)

# hosting unit price, in usd
hosting_unit_price = st.number_input('电费/度 ($)', value=0.068, min_value=0., step=0.001, format='%0.3f')

# Actual electricity cost factor
electricity_cost_factor = st.number_input('实际电费系数', value=1.05)

# Revenue for machine per day, in USD
machine_revenue_per_day_usd = revenue_per_day_usd * hash_rate

# power consumption per day, in KWh
power_consumption_per_day = power / 1000 * 24 * electricity_cost_factor

# Hosting fee for machine per day, in USD
hosting_fee_per_day = power_consumption_per_day * hosting_unit_price

# Hosting Fee Ratio
if machine_revenue_per_day_usd != 0:
    hosting_fee_ratio = hosting_fee_per_day / machine_revenue_per_day_usd
else:
    hosting_fee_ratio = 0

st.markdown('---')
col1, col2, col3 = st.columns(3)
col1.metric(label="__收益电费比__", value=f"{hosting_fee_ratio:.2f}")
col2.metric(label="__机器收益/天($)__", value=f"{machine_revenue_per_day_usd:.3f}")
col3.metric(label="__机器电费/天($)__", value=f"{hosting_fee_per_day:.3f}")

# Break-even hosting price calculation
chgs = (-0.2, -0.1, 0, 0.1, 0.2)
chgs_str = [f'({v:.0%})'if v != 0 else '' for v in chgs]
list_revenue_per_day_usd = [revenue_per_day_usd * (1+f) for f in chgs]
list_breakeven_hosting_unit_price = [rev * hash_rate / power_consumption_per_day if power_consumption_per_day!=0 else 0 for rev in list_revenue_per_day_usd]

st.markdown('---')
st.subheader('关机电价')
st.markdown('\n')
fx_usd_rmb = st.number_input('美元人民币汇率', value=st.session_state['usd_rmb'], min_value=0., step=0.1, format='%0.2f')
st.markdown('\n')
col1 = [f"{v * fx_usd_rmb:.3f} {suffix}"for v, suffix in zip(list_revenue_per_day_usd,chgs_str)]
col2 = [f"{v:.3f} {suffix}"for v, suffix in zip(list_revenue_per_day_usd,chgs_str)]
col3 = [f"{v:.3f}" for v in list_breakeven_hosting_unit_price]
df = pd.DataFrame([col1, col2, col3], index=['每T收益(RMB)','每T收益($)','关机电价($)']).T

st.dataframe(df, use_container_width=True, hide_index=True)