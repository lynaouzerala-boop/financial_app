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

st.set_page_config(page_title="توليد القوائم المالية", page_icon="📊")
st.title("📊 نظام توليد القوائم المالية التلقائي")

# بيانات الشركة والعملة
col1, col2 = st.columns(2)
with col1:
    company_name = st.text_input("اسم الشركة / المؤسسة", "شركة الأمل للتجارة")
with col2:
    currency = st.selectbox("العملة", ["DZD", "USD ($)", "EUR (€)"])

st.divider()

# اختيار طريقة إدخال البيانات
mode = st.radio(
    "اختر طريقة إدخال البيانات:",
    ["📝 جدول تفاعلي مباشر (مناسب للهاتف)", "📂 رفع ملف Excel أو CSV", "✍️ إدخال الإجمالي يدوياً"]
)

revenue = 0.0
expenses = 0.0

if mode == "📝 جدول تفاعلي مباشر (مناسب للهاتف)":
    st.info("يمكنك تعديل الأرقام أو إضافة معاملات جديدة مباشرة في الجدول أدناه:")
    default_data = pd.DataFrame([
        {"البيان": "مبيعات بضائع", "النوع": "إيراد", "المبلغ": 150000.0},
        {"البيان": "خدمات استشارية", "النوع": "إيراد", "المبلغ": 80000.0},
        {"البيان": "إيجار المحل", "النوع": "مصروف", "المبلغ": 35000.0},
        {"البيان": "رواتب الموظفين", "النوع": "مصروف", "المبلغ": 65000.0},
    ])
    edited_df = st.data_editor(default_data, num_rows="dynamic", use_container_width=True)
    
    revenue = edited_df[edited_df["النوع"].astype(str).str.contains("إيراد|ايراد", na=False)]["المبلغ"].sum()
    expenses = edited_df[edited_df["النوع"].astype(str).str.contains("مصروف|نفقات", na=False)]["المبلغ"].sum()

elif mode == "📂 رفع ملف Excel أو CSV":
    st.info("يجب أن يحتوي الملف على عمود **النوع** (إيراد / مصروف) وعمود **المبلغ**.")
    uploaded_file = st.file_uploader("ارفع ملف المعاملات المالية", type=["xlsx", "xls", "csv"])
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith(".csv") else pd.read_excel(uploaded_file)
        st.dataframe(df, use_container_width=True)
        if "النوع" in df.columns and "المبلغ" in df.columns:
            revenue = df[df["النوع"].astype(str).str.contains("إيراد|ايراد|Revenue|Income", case=False, na=False)]["المبلغ"].sum()
            expenses = df[df["النوع"].astype(str).str.contains("مصروف|نفقات|Expense", case=False, na=False)]["المبلغ"].sum()

else:
    revenue = st.number_input(f"إجمالي الإيرادات ({currency})", min_value=0.0, value=230000.0)
    expenses = st.number_input(f"إجمالي المصروفات ({currency})", min_value=0.0, value=100000.0)

st.divider()

# حساب وعرض النتائج وتوليد الـ PDF
if st.button("⚙️ حساب وتوليد قائمة الدخل (PDF)", type="primary"):
    net_income = revenue - expenses
    
    m1, m2, m3 = st.columns(3)
    m1.metric("إجمالي الإيرادات", f"{revenue:,.2f} {currency}")
    m2.metric("إجمالي المصروفات", f"{expenses:,.2f} {currency}")
    m3.metric("صافي الربح / الخسارة", f"{net_income:,.2f} {currency}")

    # إنشاء ملف PDF احترافي بجدول منسق
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
    
    pdf.set_fill_color(220, 235, 220) if net_income >= 0 else pdf.set_fill_color(245, 220, 220)
    pdf.cell(95, 14, format_arabic(f"{net_income:,.2f} {currency}"), border=1, align="C", fill=True)
    pdf.cell(95, 14, format_arabic("صافي الربح" if net_income >= 0 else "صافي الخسارة"), border=1, align="R", fill=True, new_x="LMARGIN", new_y="NEXT")

    pdf_bytes = bytes(pdf.output())

    st.download_button(
        label="📥 تحميل قائمة الدخل الجاهزة (PDF)",
        data=pdf_bytes,
        file_name="Income_Statement.pdf",
        mime="application/pdf"
    )

