import streamlit as st
from fpdf import FPDF

st.set_page_config(page_title="مولد القوائم المالية", layout="centered")
st.title("📊 توليد القوائم المالية التلقائي")

company = st.text_input("اسم الشركة", "My Company")
revenue = st.number_input("إجمالي الإيرادات ($)", min_value=0.0, step=100.0)
expenses = st.number_input("إجمالي المصروفات ($)", min_value=0.0, step=100.0)

if st.button("حساب وتوليد قائمة الدخل (PDF)"):
    net_income = revenue - expenses
    if net_income >= 0:
        st.success(f"صافي الربح: {net_income:,.2f} $")
    else:
        st.error(f"صافي الخسارة: {abs(net_income):,.2f} $")

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(200, 10, text=f"Income Statement - {company}", new_x="LMARGIN", new_y="NEXT", align='C')
    pdf.ln(10)
    pdf.set_font("Helvetica", size=12)
    pdf.cell(200, 10, text=f"Total Revenue: ${revenue:,.2f}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(200, 10, text=f"Total Expenses: ${expenses:,.2f}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(200, 10, text=f"Net Income: ${net_income:,.2f}", new_x="LMARGIN", new_y="NEXT")
    
    pdf_bytes = bytes(pdf.output())
    st.download_button(
        label="📥 تحميل القائمة المالية (PDF)",
        data=pdf_bytes,
        file_name="Financial_Statement.pdf",
        mime="application/pdf"
    )

