import streamlit as st
from streamlit_gsheets import GSheetsConnection
import datetime
import pandas as pd
from app import app_master as ap
from app import app_money as am

# データベース(GoogleSpreadSheet)に接続

selected_data = st.sidebar.selectbox('メニュー', ['master', 'money'])
if selected_data == 'master':
    ap.app_master()
elif selected_data == 'money':
    am.app_money()

#conn.close()