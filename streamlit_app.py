import streamlit as st
from streamlit_gsheets import GSheetsConnection
import datetime
import pandas as pd
import os

# データベース(GoogleSpreadSheet)に接続
conn = st.experimental_connection("gsheets", type=GSheetsConnection)
df = conn.query('SELECT date, master_num FROM "master" WHERE date is NOT NULL ORDER BY date DESC')
print(df)

selected_data = st.sidebar.selectbox('メニュー', ['Edit', 'Record'])

if selected_data == 'Edit':
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
            print(df_update)
            df = conn.update(
                data=df_update,
            )
            st.cache_data.clear()
            st.rerun()
            print('追加')
        else:
            df.loc[df['date']==date_str] = result
            df = conn.update(
                data=df,
            )
            st.cache_data.clear()
            st.rerun()
            print('更新')
elif selected_data == 'Record':
    # 統計データの表示
    # df = pd.read_sql(f'''
    # SELECT date, master_num
    # FROM master_dt
    # ORDER BY date DESC
    # ''', conn)


    if not df.empty:
        st.header('平均')
        avg_num = df['master_num'].mean()
        st.write(f'{avg_num:.3f}')
        st.dataframe(df)

#conn.close()