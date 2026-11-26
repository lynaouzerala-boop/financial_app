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
col1, col2 = st.columns([2, 1])
with col1:
    company_name = st.text_input("اسم الشركة / المؤسسة", "شركة الأمل للتجارة")
with col2:
    currency = st.selectbox("العملة", ["DZD", "USD ($)", "EUR (€)"])

st.divider()

# اختيار طريقة إدخال البيانات
mode = st.radio("اختر طريقة إدخال البيانات:", ["📂 رفع ملف Excel أو CSV (تلقائي)", "✍️ إدخال الإجمالي يدوياً"])

revenue = 0.0
expenses = 0.0

if mode == "📂 رفع ملف Excel أو CSV (تلقائي)":
    st.info("يجب أن يحتوي الملف على عمود **النوع** (إيراد / مصروف) وعمود **المبلغ**.")
    
    # زر لتحميل ملف CSV تجريبي لاختبار التطبيق فوراً
    sample_csv = "التاريخ,البيان,النوع,المبلغ\n2026-01-05,مبيعات بضائع,إيراد,150000\n2026-01-10,إيجار المحل,مصروف,35000\n2026-01-15,خدمات استشارية,إيراد,80000\n2026-01-25,رواتب الموظفين,مصروف,65000"
    st.download_button("📥 تحميل ملف تجريبي (CSV) لاختبار التطبيق", data=sample_csv.encode("utf-8-sig"), file_name="sample_transactions.csv", mime="text/csv")

    uploaded_file = st.file_uploader("ارفع ملف المعاملات المالية (Excel أو CSV)", type=["xlsx", "xls", "csv"])
    
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            st.write("### معاينة البيانات المرفوعة:")
            st.dataframe(df, use_container_width=True)
            
            # البحث التلقائي عن أعمدة النوع والمبلغ
            if "النوع" in df.columns and "المبلغ" in df.columns:
                revenue = df[df["النوع"].astype(str).str.contains("إيراد|ايراد|Revenue|Income", case=False, na=False)]["المبلغ"].sum()
                expenses = df[df["النوع"].astype(str).str.contains("مصروف|نفقات|Expense", case=False, na=False)]["المبلغ"].sum()
            else:
                st.warning("⚠️ تأكد من وجود عمودين باسم 'النوع' و 'المبلغ' في الملف.")
        except Exception as e:
            st.error(f"حدث خطأ أثناء قراءة الملف: {e}")
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
    
    # العنوان
    pdf.set_font("ArabicFont", size=18)
    pdf.cell(0, 14, format_arabic(f"قائمة الدخل - {company_name}"), new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(8)
    
    # جدول البيانات
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
        file_name=f"Income_Statement_{company_name}.pdf",
        mime="application/pdf"
    )
