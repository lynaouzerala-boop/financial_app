import streamlit as st
import pandas as pd
from fpdf import FPDF
import arabic_reshaper
from bidi.algorithm import get_display
import matplotlib
import os

# إعداد الخط العربي المدمج
font_file = os.path.join(os.path.dirname(matplotlib.__file__), "mpl-data", "fonts", "ttf", "DejaVuSans.ttf")

def format_arabic(text):
    reshaped_text = arabic_reshaper.reshape(str(text))
    return get_display(reshaped_text)

st.set_page_config(page_title="توليد القوائم المالية", page_icon="📊", layout="centered")
st.title("📊 نظام توليد القوائم المالية التلقائي")

# بيانات الشركة والعملة (مشتركة لكل القوائم)
col1, col2 = st.columns(2)
with col1:
    company_name = st.text_input("اسم الشركة / المؤسسة", "شركة الأمل للتجارة")
with col2:
    currency = st.selectbox("العملة", ["DZD", "USD ($)", "EUR (€)"])

st.divider()

# تقسيم التطبيق إلى تبويبين: قائمة الدخل والميزانية العمومية
tab1, tab2 = st.tabs(["📈 قائمة الدخل (Income Statement)", "⚖️ الميزانية العمومية (Balance Sheet)"])

# ==================== التبويب الأول: قائمة الدخل ====================
with tab1:
    mode = st.radio(
        "طريقة إدخال بيانات قائمة الدخل:",
        ["📝 جدول تفاعلي مباشر", "📂 رفع ملف Excel أو CSV", "✍️ إدخال الإجمالي يدوياً"],
        key="inc_mode"
    )

    revenue = 0.0
    expenses = 0.0

    if mode == "📝 جدول تفاعلي مباشر":
        default_data = pd.DataFrame([
            {"البيان": "مبيعات بضائع", "النوع": "إيراد", "المبلغ": 150000.0},
            {"البيان": "خدمات استشارية", "النوع": "إيراد", "المبلغ": 80000.0},
            {"البيان": "إيجار المحل", "النوع": "مصروف", "المبلغ": 35000.0},
            {"البيان": "رواتب الموظفين", "النوع": "مصروف", "المبلغ": 65000.0},
        ])
        edited_df = st.data_editor(default_data, num_rows="dynamic", use_container_width=True, key="inc_table")
        revenue = edited_df[edited_df["النوع"].astype(str).str.contains("إيراد|ايراد", na=False)]["المبلغ"].sum()
        expenses = edited_df[edited_df["النوع"].astype(str).str.contains("مصروف|نفقات", na=False)]["المبلغ"].sum()

    elif mode == "📂 رفع ملف Excel أو CSV":
        uploaded_file = st.file_uploader("ارفع ملف المعاملات (يحتوي عمود النوع والمبلغ)", type=["xlsx", "xls", "csv"])
        if uploaded_file is not None:
            df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith(".csv") else pd.read_excel(uploaded_file)
            st.dataframe(df, use_container_width=True)
            if "النوع" in df.columns and "المبلغ" in df.columns:
                revenue = df[df["النوع"].astype(str).str.contains("إيراد|ايراد|Revenue|Income", case=False, na=False)]["المبلغ"].sum()
                expenses = df[df["النوع"].astype(str).str.contains("مصروف|نفقات|Expense", case=False, na=False)]["المبلغ"].sum()
    else:
        revenue = st.number_input(f"إجمالي الإيرادات ({currency})", min_value=0.0, value=230000.0)
        expenses = st.number_input(f"إجمالي المصروفات ({currency})", min_value=0.0, value=100000.0)

    if st.button("⚙️ حساب وتوليد قائمة الدخل (PDF)", type="primary"):
        net_income = revenue - expenses
        
        m1, m2, m3 = st.columns(3)
        m1.metric("إجمالي الإيرادات", f"{revenue:,.2f} {currency}")
        m2.metric("إجمالي المصروفات", f"{expenses:,.2f} {currency}")
        m3.metric("صافي الربح / الخسارة", f"{net_income:,.2f} {currency}")

        # رسم بياني للمقارنة
        st.write("### الرسم البياني للأداء المالي:")
        chart_df = pd.DataFrame({
            "البند": ["الإيرادات", "المصروفات", "صافي النتيجة"],
            "القيمة": [revenue, expenses, net_income]
        }).set_index("البند")
        st.bar_chart(chart_df)

        # توليد PDF قائمة الدخل
        pdf = FPDF()
        pdf.add_page()
        pdf.add_font("ArabicFont", "", font_file)
        pdf.set_font("ArabicFont", size=18)
        pdf.cell(0, 14, format_arabic(f"قائمة الدخل - {company_name}"), new_x="LMARGIN", new_y="NEXT", align="C")
        pdf.ln(8)
        
        pdf.set_font("ArabicFont", size=12)
        pdf.set_fill_color(240, 240, 240)
        pdf.cell(95, 12, format_arabic(f"{revenue:,.2f} {currency}"), border=1, align="C")
        pdf.cell(95, 12, format_arabic("إجمالي الإيرادات"), border=1, align="R", fill=True, new_x="LMARGIN", new_y="NEXT")
        
        pdf.cell(95, 12, format_arabic(f"{expenses:,.2f} {currency}"), border=1, align="C")
        pdf.cell(95, 12, format_arabic("إجمالي المصروفات"), border=1, align="R", fill=True, new_x="LMARGIN", new_y="NEXT")
        
        if net_income >= 0:
            pdf.set_fill_color(220, 235, 220)
        else:
            pdf.set_fill_color(245, 220, 220)
            
        pdf.cell(95, 14, format_arabic(f"{net_income:,.2f} {currency}"), border=1, align="C", fill=True)
        pdf.cell(95, 14, format_arabic("صافي الربح" if net_income >= 0 else "صافي الخسارة"), border=1, align="R", fill=True, new_x="LMARGIN", new_y="NEXT")

        st.download_button(
            label="📥 تحميل قائمة الدخل (PDF)",
            data=bytes(pdf.output()),
            file_name="Income_Statement.pdf",
            mime="application/pdf"
        )

# ==================== التبويب الثاني: الميزانية العمومية ====================
with tab2:
    st.info("أدخل بنود الأصول والخصوم وحقوق الملكية للتحقق من توازن الميزانية تلقائياً:")
    bs_data = pd.DataFrame([
        {"البند": "النقدية في الصندوق والبنك", "التصنيف": "أصول", "المبلغ": 180000.0},
        {"البند": "المخزون والمعدات", "التصنيف": "أصول", "المبلغ": 120000.0},
        {"البند": "الديون والموردون", "التصنيف": "خصوم", "المبلغ": 70000.0},
        {"البند": "رأس المال والأرباح المحتجزة", "التصنيف": "حقوق ملكية", "المبلغ": 230000.0},
    ])
    edited_bs = st.data_editor(bs_data, num_rows="dynamic", use_container_width=True, key="bs_table")

    assets = edited_bs[edited_bs["التصنيف"].astype(str).str.contains("أصول|اصول", na=False)]["المبلغ"].sum()
    liabilities = edited_bs[edited_bs["التصنيف"].astype(str).str.contains("خصوم|التزامات", na=False)]["المبلغ"].sum()
    equity = edited_bs[edited_bs["التصنيف"].astype(str).str.contains("حقوق|رأس", na=False)]["المبلغ"].sum()
    liab_and_eq = liabilities + equity

    if st.button("⚖️ فحص وتوليد الميزانية العمومية (PDF)", type="primary"):
        b1, b2, b3 = st.columns(3)
        b1.metric("إجمالي الأصول", f"{assets:,.2f} {currency}")
        b2.metric("الخصوم + حقوق الملكية", f"{liab_and_eq:,.2f} {currency}")
        
        if assets == liab_and_eq:
            st.success("✅ الميزانية العمومية متوازنة تماماً (الأصول = الخصوم + حقوق الملكية)")
        else:
            diff = abs(assets - liab_and_eq)
            st.warning(f"⚠️ يوجد فرق في توازن الميزانية قدره: {diff:,.2f} {currency}")

        # توليد PDF الميزانية العمومية
        pdf_bs = FPDF()
        pdf_bs.add_page()
        pdf_bs.add_font("ArabicFont", "", font_file)
        pdf_bs.set_font("ArabicFont", size=18)
        pdf_bs.cell(0, 14, format_arabic(f"الميزانية العمومية - {company_name}"), new_x="LMARGIN", new_y="NEXT", align="C")
        pdf_bs.ln(8)

        pdf_bs.set_font("ArabicFont", size=12)
        pdf_bs.set_fill_color(240, 240, 240)
        
        pdf_bs.cell(95, 12, format_arabic(f"{assets:,.2f} {currency}"), border=1, align="C")
        pdf_bs.cell(95, 12, format_arabic("إجمالي الأصول"), border=1, align="R", fill=True, new_x="LMARGIN", new_y="NEXT")
        
        pdf_bs.cell(95, 12, format_arabic(f"{liabilities:,.2f} {currency}"), border=1, align="C")
        pdf_bs.cell(95, 12, format_arabic("إجمالي الخصوم"), border=1, align="R", fill=True, new_x="LMARGIN", new_y="NEXT")
        
        pdf_bs.cell(95, 12, format_arabic(f"{equity:,.2f} {currency}"), border=1, align="C")
        pdf_bs.cell(95, 12, format_arabic("إجمالي حقوق الملكية"), border=1, align="R", fill=True, new_x="LMARGIN", new_y="NEXT")
        
        pdf_bs.set_fill_color(220, 235, 220)
        pdf_bs.cell(95, 14, format_arabic(f"{liab_and_eq:,.2f} {currency}"), border=1, align="C", fill=True)
        pdf_bs.cell(95, 14, format_arabic("إجمالي الخصوم وحقوق الملكية"), border=1, align="R", fill=True, new_x="LMARGIN", new_y="NEXT")

        st.download_button(
            label="📥 تحميل الميزانية العمومية (PDF)",
            data=bytes(pdf_bs.output()),
            file_name="Balance_Sheet.pdf",
            mime="application/pdf"
        )


