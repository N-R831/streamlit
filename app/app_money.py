import streamlit as st
from streamlit_gsheets import GSheetsConnection
import datetime
import pandas as pd
import os

# データベース(GoogleSpreadSheet)に接続

selected_data = st.sidebar.selectbox('メニュー', ['master', 'money'])
conn = st.connection("gsheets", type=GSheetsConnection)
if selected_data == 'master':
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
elif selected_data == 'money':
    df = conn.query('SELECT date, inout, kind, amount, memo FROM "money" WHERE date is NOT NULL ORDER BY date DESC')

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
    
    if not df.empty:
        st.dataframe(df)

#conn.close()