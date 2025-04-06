from flask import Flask, request, render_template_string, redirect
import pandas as pd
import os

app = Flask(__name__)

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

HTML_FORM = '''
<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>מחשבון חשמל לשוכרים</title>
</head>
<body>
    <h2>מחשבון חשמל לשוכרים</h2>
    <form method="post">
        <label>קריאת מונה כללי:</label><br>
        <input type="number" step="0.01" name="total"><br><br>
        <label>קריאת מונה יחידה 1:</label><br>
        <input type="number" step="0.01" name="unit1"><br><br>
        <label>סכום חשבון אחרון (ש"ח):</label><br>
        <input type="number" step="0.01" name="payment"><br><br>
        <input type="submit" value="חשב">
    </form>
    <br>
    {% if result %}
    <div style="border:1px solid #ccc; padding:10px;">
        <strong>תוצאה:</strong><br>
        {{ result|safe }}
    </div>
    {% endif %}
</body>
</html>
'''

@app.route("/", methods=["GET", "POST"])
def index():
    result = ""
    if request.method == "POST":
        try:
            current_total = float(request.form["total"])
            current_unit1 = float(request.form["unit1"])
            total_payment = float(request.form["payment"])
        except:
            result = "אנא הזן ערכים חוקיים."
            return render_template_string(HTML_FORM, result=result)

        previous = load_previous_data()
        if previous is None:
            save_new_data(current_total, current_unit1)
            result = "אין נתונים קודמים. הנתונים נשמרו כהתחלה."
        else:
            prev_total = previous['total_meter']
            prev_unit1 = previous['unit1_meter']
            delta_total = current_total - prev_total
            delta_unit1 = current_unit1 - prev_unit1
            delta_unit2 = delta_total - delta_unit1

            if delta_total == 0:
                result = "לא הייתה צריכה מאז הפעם הקודמת."
            else:
                result = (
                    "סה&quot;כ צריכה: {:.2f} קוט&quot;ש<br>"
                    "יחידה 1 צרכה: {:.2f} קוט&quot;ש => תשלום: {:.2f} ש&quot;ח<br>"
                    "יחידה 2 צרכה: {:.2f} קוט&quot;ש => תשלום: {:.2f} ש&quot;ח"
                ).format(
                    delta_total, delta_unit1,
                    (delta_unit1 / delta_total) * total_payment,
                    delta_unit2,
                    (delta_unit2 / delta_total) * total_payment
                )
                save_new_data(current_total, current_unit1)

    return render_template_string(HTML_FORM, result=result)

if __name__ == "__main__":
    app.run(debug=True)
