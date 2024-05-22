import streamlit as st
from streamlit_gsheets import GSheetsConnection
import datetime
import pandas as pd
import os


def app_money():
    # データベース(GoogleSpreadSheet)に接続
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.query('SELECT date, inout, kind, amount, memo FROM "money" WHERE date is NOT NULL ORDER BY date DESC')
    tab_home, tab_input, tab_data, tab_hist, tab_conf = st.tabs(["HOME", "入力", "データ", "履歴", "設定"] )
    with tab_home:
        st.title("HOME")
        df_in = conn.query('SELECT SUM(amount) FROM "money" WHERE inout = \'in\'')
        income = df_in['sum(amount)'][0]
        df_out = conn.query('SELECT SUM(amount) FROM "money" WHERE inout = \'out\'')
        outgo = df_out['sum(amount)'][0]
        total = income - outgo
        st.write(f'トータル{total}の収支')
    
    with tab_input:
        date = st.date_input('日付を入力してください。', datetime.date.today())
        inout = st.selectbox("収入/支出(in/out)", options=["in","out"])
        if inout == "in":
            df_kind = conn.query('SELECT kind_in FROM "kind" WHERE kind_in is NOT NULL ')
            option_list=df_kind['kind_in']
            kind = st.selectbox("分類", options=option_list)
        else:
            df_kind = conn.query('SELECT kind_out FROM "kind" WHERE kind_out is NOT NULL ')
            option_list=df_kind['kind_out']
            kind = st.selectbox("分類", options=option_list)
        amount = st.number_input("金額", min_value=0, max_value=None, value=1000, step=100, help="金額")
        """
        入力内容の登録
        """
        if st.button('submit'):
            if (date != None) and (inout != None) and  (kind != None) and amount != 0:
                date_str = date.strftime('%Y-%m-%d')
                df_append = pd.DataFrame({'date': [date_str], 'inout': [inout], 'kind': [kind], 'amount': [amount], })
                df_update = pd.concat([df, df_append])
                df = conn.update(
                    worksheet="money",
                    data=df_update,
                )
                st.cache_data.clear()
                st.rerun()
    with tab_hist:
        if not df.empty:
            st.dataframe(df)
    with tab_conf:
        df_conf = conn.query('SELECT salary_day FROM "config" WHERE salary_day is NOT NULL')
        salary_day = df_conf['salary_day'][0]
        salary_day = st.number_input("給料日", min_value=1, max_value=28, value=salary_day,step=1)
        if st.button('save'):
            if (salary_day != None):
                df_conf['salary_day'][0] = salary_day
                df = conn.update(
                    worksheet="config",
                    data=df_conf,
                )