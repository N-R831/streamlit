import streamlit as st
from streamlit_gsheets import GSheetsConnection
import datetime
import pandas as pd
import os

def app_master():
    # データベース(GoogleSpreadSheet)に接続
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.query('SELECT date, master_num FROM "master" WHERE date is NOT NULL ORDER BY date DESC')
    date = st.date_input('日付を入力してください。', datetime.date.today())
    input_num = st.number_input('回数を入力してください', value=0)

    if st.button('submit'):
        date_str = date.strftime('%Y-%m-%d')
        result = input_num
        # 存在チェック
        str_query = f"SELECT date, master_num FROM master WHERE date = '{date_str}'"
        df_check = conn.query(str_query)
        print(df_check)
        if df_check.empty:
            df_append = pd.DataFrame({'date': [date_str], 'master_num': [result]})
            df_update = pd.concat([df, df_append])
            df = conn.update(
                worksheet="master",
                data=df_update,
            )
            st.cache_data.clear()
            st.rerun()
        else:
            df.loc[df['date']==date_str, 'master_num'] =  result
            df = conn.update(
                worksheet="master",
                data=df,
            )
            st.cache_data.clear()
            st.rerun()
    if not df.empty:
        st.header('平均')
        avg_num = df['master_num'].mean()
        st.write(f'{avg_num:.3f}')
        st.dataframe(df)
