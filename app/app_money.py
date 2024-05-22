import streamlit as st
from streamlit_gsheets import GSheetsConnection
import datetime
import pandas as pd
import os
import jpholiday
from dateutil.relativedelta import relativedelta

def app_money():
    # データベース(GoogleSpreadSheet)に接続
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.query('SELECT date, inout, kind, amount, memo FROM "money" WHERE date is NOT NULL ORDER BY date DESC')
    
    # 給料日計算
    df_conf = conn.query('SELECT salary_day FROM "config" WHERE salary_day is NOT NULL')
    salary_day = df_conf['salary_day'][0]
    # 今月の給料支給日
    now = datetime.datetime.now()
    date_salary_day = datetime.datetime(now.year, now.month, int(salary_day-1))
    temp_str_salary_day = date_salary_day.strftime('%Y%m%d')
    str_salary_day = returnBizDay(temp_str_salary_day)
    # 来月の給料支給日
    date_salary_day_next = (now + relativedelta(months=1)).replace(day=int(salary_day-1))
    temp_str_salary_day_next = date_salary_day_next.strftime('%Y%m%d')
    str_salary_day_next = returnBizDay(temp_str_salary_day_next)
    
    tab_home, tab_input, tab_data, tab_hist, tab_conf = st.tabs(["HOME", "入力", "データ", "履歴", "設定"] )
    with tab_home:
        st.title("今月の収入")
        str_query = "SELECT SUM(amount) FROM ""money"" WHERE inout = \'in\' and (CAST(date AS DATE) BETWEEN CAST('" + str_salary_day + "' AS DATE) AND CAST('" + str_salary_day_next + "' AS DATE))"
        print(str_query)
        df_in = conn.query(str_query)
        income = df_in['sum(amount)'][0]
        st.write(income)
        
        str_query = "SELECT SUM(amount) FROM ""money"" WHERE inout = \'out\' and (CAST(date AS DATE) BETWEEN CAST('" + str_salary_day + "' AS DATE) AND CAST('" + str_salary_day_next + "' AS DATE))"
        df_out = conn.query(str_query)
        outgo = df_out['sum(amount)'][0]
        total = income - outgo
        st.write(f'トータル{total}の収支')
    
    with tab_input:
        date = st.date_input('日付を入力してください。', datetime.date.today())
        inout = st.selectbox("収入/支出(in/out)", options=["in","out"])
        if inout == "in":
            df_kind = conn.query('SELECT kind_in FROM "kind" WHERE kind_in is NOT NULL')
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
        salary_day = st.number_input("給料日", min_value=1, max_value=28, value=int(salary_day),step=1)
        if st.button('save'):
            if (salary_day != None):
                df_conf['salary_day'][0] = salary_day
                df = conn.update(
                    worksheet="config",
                    data=df_conf,
                )
                
"""
 給料日取得
"""
def returnBizDay(DATE):
    Date = datetime.date(int(DATE[0:4]), int(DATE[4:6]), int(DATE[6:8]))
    while Date.weekday() >= 5 or jpholiday.is_holiday(Date):
        Date = datetime.date(Date.year, Date.month, Date.day - 1)
    return Date.strftime("%Y-%m-%d")