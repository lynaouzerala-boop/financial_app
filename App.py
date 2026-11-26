import streamlit as st
from fpdf import FPDF
import arabic_reshaper
from bidi.algorithm import get_display
import urllib.request
import os

# تحميل الخط العربي تلقائياً إذا لم يكن موجوداً
font_file = "Amiri-Regular.ttf"
if not os.path.exists(font_file):
    url = "https://github.com"
    urllib.request.urlretrieve(url, font_file)

# دالة لمعالجة النص العربي (ربط الحروف وعكس الاتجاه)
def format_arabic(text):
    reshaped_text = arabic_reshaper.reshape(str(text))
    return get_display(reshaped_text)

st.title("📊 توليد القوائم المالية التلقائي")

company_name = st.text_input("اسم الشركة", "شركة الأمل للتجارة")
revenue = st.number_input("إجمالي الإيرادات ($)", min_value=0.0, value=50000.0)
expenses = st.number_input("إجمالي المصروفات ($)", min_value=0.0, value=32000.0)

if st.button("حساب وتوليد قائمة الدخل (PDF)"):
    net_income = revenue - expenses
    st.success(f"صافي الربح: ${net_income:,.2f}")

    # إنشاء ملف PDF مع الخط العربي
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font("ArabicFont", "", font_file)
    pdf.set_font("ArabicFont", size=16)

    # كتابة البيانات بالعربية
    pdf.cell(0, 12, format_arabic(f"قائمة الدخل - {company_name}"), ln=True, align="C")
    pdf.ln(10)
    
    pdf.set_font("ArabicFont", size=12)
    pdf.cell(0, 10, format_arabic(f"إجمالي الإيرادات: {revenue:,.2f} $"), ln=True, align="R")
    pdf.cell(0, 10, format_arabic(f"إجمالي المصروفات: {expenses:,.2f} $"), ln=True, align="R")
    pdf.ln(5)
    pdf.cell(0, 10, format_arabic(f"صافي الربح: {net_income:,.2f} $"), ln=True, align="R")

    pdf_bytes = bytes(pdf.output())

    st.download_button(
        label="📥 تحميل القائمة المالية (PDF)",
        data=pdf_bytes,
        file_name="income_statement.pdf",
        mime="application/pdf"
    )

