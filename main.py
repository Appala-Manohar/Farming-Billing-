import streamlit as st
from fpdf import FPDF
import base64

# --- PDF Generation Function ---
def create_pdf(f_name, bags, extra_kgs, input_cost, adj_rate, cost_per_kg, bags_amt, extra_amt, gross, cc, hamali, net, cc_enabled):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, "PADDY PURCHASE RECEIPT", ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_font("Arial", '', 12)
    pdf.cell(200, 10, f"Farmer Name: {f_name}", ln=True)
    pdf.cell(200, 10, f"Total Bags: {bags}", ln=True)
    pdf.cell(200, 10, f"Extra KGs: {extra_kgs} kg", ln=True)
    pdf.cell(200, 10, f"Input Rate: Rs. {input_cost:.2f}", ln=True)
    pdf.ln(5)
    
    pdf.cell(200, 10, f"Adjusted Rate (68/75): Rs. {adj_rate:.2f}", ln=True)
    pdf.cell(200, 10, f"Rate per KG (Rate/70): Rs. {cost_per_kg:.4f}", ln=True)
    pdf.ln(5)
    
    pdf.cell(200, 10, f"Bags Total Amount: Rs. {bags_amt:.2f}", ln=True)
    pdf.cell(200, 10, f"Extra KG Amount: Rs. {extra_amt:.2f}", ln=True)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, f"GROSS TOTAL: Rs. {gross:.2f}", ln=True)
    
    pdf.set_font("Arial", '', 12)
    if cc_enabled:
        pdf.cell(200, 10, f"(-) 1% CC Charge: Rs. {cc:.2f}", ln=True)
    pdf.cell(200, 10, f"(-) Hamali (Rs. 5 per bag): Rs. {hamali:.2f}", ln=True)
    
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, f"NET PAYABLE: Rs. {net:,.2f}", ln=True)
    
    # PDF generation as bytes
    return pdf.output(dest='S').encode('latin-1')

# --- Streamlit UI ---
st.set_page_config(page_title="Rice Mill Billing", page_icon="🌾")

# Custom Styling
st.markdown("""
    <style>
    .main {
        background-image: url("https://www.transparenttextures.com/patterns/rice-paper.png");
        background-color: #f0f4f7;
    }
    .bill-box {
        background-color: white;
        padding: 25px;
        border-radius: 15px;
        border: 2px solid #2e7d32;
        box-shadow: 5px 5px 20px rgba(0,0,0,0.1);
        color: black;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🌾 Rice Mill Digital Billing")

# Inputs
f_name = st.text_input("Farmer Name (రైతు పేరు):")

col1, col2 = st.columns(2)
with col1:
    bags = st.number_input("Total Bags (బస్తాలు):", min_value=0, step=1)
    extra_kgs = st.number_input("Extra KGs (కేజీలు):", min_value=0.0, step=0.1)
with col2:
    input_cost = st.number_input("Input Cost (ధర):", min_value=0.0, value=1855.0)
    # IDI NEE KOTHA OPTION:
    apply_cc = st.checkbox("Apply 1% CC Deduction?", value=True)

# Calculation Logic
adj_rate = input_cost * (68/75)
cost_per_kg = adj_rate / 70
bags_amt = adj_rate * bags
extra_amt = cost_per_kg * extra_kgs
gross = bags_amt + extra_amt

cc_val = gross * 0.01 if apply_cc else 0.0
hamali = bags * 5
net = gross - cc_val - hamali

# Final Bill Preview
if st.button("Generate & Download PDF"):
    if f_name:
        st.markdown("---")
        st.markdown(f"""
        <div class="bill-box">
            <h2 style="text-align:center; color:#2e7d32;">PURCHASE RECEIPT</h2>
            <p><b>Farmer:</b> {f_name}</p>
            <hr>
            <p>Bags Amount: ₹{bags_amt:.2f}</p>
            <p>Extra KG Amount: ₹{extra_amt:.2f}</p>
            <p><b>Gross Total: ₹{gross:.2f}</b></p>
            <p style="color:red;">(-) CC Charge: ₹{cc_val:.2f}</p>
            <p style="color:red;">(-) Hamali: ₹{hamali:.2f}</p>
            <hr>
            <h3 style="text-align:center; color:#1b5e20;">Final Pay: ₹{net:,.2f}</h3>
        </div>
        """, unsafe_allow_html=True)

        # PDF Data
        pdf_bytes = create_pdf(f_name, bags, extra_kgs, input_cost, adj_rate, cost_per_kg, bags_amt, extra_amt, gross, cc_val, hamali, net, apply_cc)
        
        st.download_button(
            label="Click here to Download PDF Bill",
            data=pdf_bytes,
            file_name=f"{f_name}_bill.pdf",
            mime="application/pdf"
        )
    else:
        st.error("Farmer Name enter cheyyi ra!")