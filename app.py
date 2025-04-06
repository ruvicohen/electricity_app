import streamlit as st
import pandas as pd
import os

FILE_NAME = "electricity_log.xlsx"

def load_previous_data():
    if os.path.exists(FILE_NAME):
        df = pd.read_excel(FILE_NAME)
        return df.iloc[-1]
    return None

def save_new_data(total_meter, unit1_meter):
    df_new = pd.DataFrame([{
        'total_meter': total_meter,
        'unit1_meter': unit1_meter
    }])
    if os.path.exists(FILE_NAME):
        df_old = pd.read_excel(FILE_NAME)
        df_all = pd.concat([df_old, df_new], ignore_index=True)
    else:
        df_all = df_new
    df_all.to_excel(FILE_NAME, index=False)

st.set_page_config(page_title="מחשבון חשמל לשוכרים", layout="centered")
st.title("🔌 מחשבון חשמל לשוכרים")

total_meter = st.number_input("קריאת מונה כללי", step=0.01)
unit1_meter = st.number_input("קריאת מונה יחידה 1", step=0.01)
total_payment = st.number_input("סכום חשבון אחרון (ש\"ח)", step=0.01)

if st.button("חשב"):
    previous = load_previous_data()
    if previous is None:
        save_new_data(total_meter, unit1_meter)
        st.info("אין נתונים קודמים. הנתונים נשמרו כהתחלה.")
    else:
        prev_total = previous['total_meter']
        prev_unit1 = previous['unit1_meter']
        delta_total = total_meter - prev_total
        delta_unit1 = unit1_meter - prev_unit1
        delta_unit2 = delta_total - delta_unit1

        if delta_total == 0:
            st.warning("לא הייתה צריכה מאז הפעם הקודמת.")
        else:
            share_unit1 = (delta_unit1 / delta_total) * total_payment
            share_unit2 = (delta_unit2 / delta_total) * total_payment

            st.success(f"""✅ סיכום:
- סה"כ צריכה: {delta_total:.2f} קוט"ש  
- יחידה 1 צרכה: {delta_unit1:.2f} קוט"ש → תשלום: {share_unit1:.2f} ש"ח  
- יחידה 2 צרכה: {delta_unit2:.2f} קוט"ש → תשלום: {share_unit2:.2f} ש"ח  
""")

            save_new_data(total_meter, unit1_meter)
