import streamlit as st
from fpdf import FPDF
from datetime import datetime
import pandas as pd
import csv
import os

# --- Database File ---
DB_FILE = 'billing_history.csv'

# --- Logic to get the NEXT Serial Number from CSV ---
def get_next_sl_no():
    if os.path.exists(DB_FILE):
        try:
            df = pd.read_csv(DB_FILE)
            if not df.empty:
                return int(df['SL_No'].max()) + 1
        except:
            return 1
    return 1

# --- PDF Generation (Professional Receipt) ---
def create_pdf(f_name, bags, extra_kgs, input_cost, adj_rate, cost_per_kg, bags_amt, extra_amt, gross, cc, hamali, net, calc_type, sl_no):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, "PADDY PURCHASE RECEIPT", ln=True, align='C')
    pdf.set_font("Arial", '', 11)
    pdf.cell(200, 10, f"Bill No: {sl_no} | Date: {datetime.now().strftime('%d/%m/%Y')}", ln=True, align='R')
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, f"Farmer Name: {f_name.upper()}", ln=True)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)
    
    pdf.set_font("Arial", '', 11)
    if calc_type == "75kg Sum":
        pdf.cell(100, 8, f"Adjusted Rate/70: Rs. {adj_rate:.2f}")
        pdf.cell(100, 8, f"Rate per KG: Rs. {cost_per_kg:.4f}", ln=True, align='R')
    else:
        pdf.cell(100, 8, f"Total Weight: {(bags*68)+extra_kgs} kg")
        pdf.cell(100, 8, f"Rate per KG (Cost/100): Rs. {cost_per_kg:.2f}", ln=True, align='R')
    
    pdf.ln(5)
    pdf.cell(150, 8, f"Bags Amount ({bags}):")
    pdf.cell(30, 8, f"Rs. {bags_amt:.2f}", ln=True, align='R')
    pdf.cell(150, 8, f"Extra KG Amount ({extra_kgs} kg):")
    pdf.cell(30, 8, f"Rs. {extra_amt:.2f}", ln=True, align='R')
    
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(150, 8, "GROSS TOTAL:")
    pdf.cell(30, 8, f"Rs. {gross:.2f}", ln=True, align='R')
    pdf.ln(5)
    
    pdf.set_font("Arial", '', 11)
    pdf.cell(150, 8, "(-) CC Charge (1%):")
    pdf.cell(30, 8, f"Rs. {cc:.2f}", ln=True, align='R')
    pdf.cell(150, 8, f"(-) Hamali (Rs. 5 x {bags}):")
    pdf.cell(30, 8, f"Rs. {hamali:.2f}", ln=True, align='R')
    
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(150, 10, "Final Payment:")
    pdf.cell(30, 10, f"Rs. {net:,.2f}", ln=True, align='R')
    return pdf.output(dest='S').encode('latin-1')

# --- DB Initialization ---
if not os.path.exists(DB_FILE):
    with open(DB_FILE, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['SL_No', 'Date', 'Farmer_Name', 'Calc_Type', 'Bags', 'Extra_KGs', 'Input_Rate', 'Gross_Total', 'Net_Payable'])

# --- UI Setup ---
st.set_page_config(page_title="Rice Mill Digital Billing", layout="wide")

# Custom Styles to match your screenshot
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .receipt-card {
        background-color: white; padding: 25px; border-radius: 10px;
        border: 1px solid #2e7d32; box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        color: black; font-family: sans-serif;
    }
    .stButton>button { background-color: #2e7d32; color: white; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

# Main Dashboard Layout (Split Screen)
col_entry, col_preview = st.columns([1, 1.2], gap="large")

with col_entry:
    st.markdown("<h2 style='color: #2e7d32;'>Billing Entry</h2>", unsafe_allow_html=True)
    current_sl = get_next_sl_no()
    
    calc_type = st.selectbox("Select Procurement Logic (పద్ధతి):", ("75kg Calculation", "100kg Quintal Calculation"))
    f_name = st.text_input("Farmer Name (రైతు పేరు):")
    f_phone = st.text_input("Phone Number (WhatsApp - ఐచ్ఛికం):")
    
    c1, c2 = st.columns(2)
    with c1:
        bags = st.number_input("Total Bags (బస్తాలు):", min_value=0, step=1)
        extra_kgs = st.number_input("Extra KGs (కేజీలు):", min_value=0.0)
    with c2:
        input_cost = st.number_input("Input Cost (ధర):", min_value=0.0, value=1855.0 if calc_type=="75kg Sum" else 2480.0)
        apply_cc = st.checkbox("Apply 1% CC Deduction?", value=True)
    
    st.write("---")
    generate_btn = st.button("Calculate & Preview Bill")

# --- Calculations ---
if calc_type == "75kg Sum":
    adj_rate = input_cost * (68/75)
    cost_per_kg = adj_rate / 70
    bags_amt = adj_rate * bags
    extra_amt = cost_per_kg * extra_kgs
else:
    total_wt = (bags * 68) + extra_kgs
    cost_per_kg = input_cost / 100
    bags_amt = (bags * 68) * cost_per_kg
    extra_amt = extra_kgs * cost_per_kg
    adj_rate = 0

gross = bags_amt + extra_amt
cc_val = gross * 0.01 if apply_cc else 0.0
hamali = bags * 5
net = gross - cc_val - hamali

with col_preview:
    st.markdown("<h2 style='color: #2e7d32; text-align: center;'>Receipt Preview</h2>", unsafe_allow_html=True)
    
    if generate_btn and f_name:
        # Save to CSV immediately on generation
        with open(DB_FILE, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([current_sl, datetime.now().strftime('%d/%m/%Y'), f_name.upper(), calc_type, bags, extra_kgs, input_cost, round(gross, 2), round(net, 2)])
        
        # Display Receipt Card (Matching your screenshot)
        st.markdown(f"""
        <div class="receipt-card">
            <h2 style="text-align:center; color:#2e7d32; margin-bottom:20px;">PADDY PURCHASE RECEIPT</h2>
            <p><b>Farmer Name:</b> {f_name.upper()}</p>
            <p><b>Bill No:</b> {current_sl} | <b>Date:</b> {datetime.now().strftime('%d/%m/%Y')}</p>
            <hr>
            <table style="width:100%; border-collapse: collapse; line-height: 1.8;">
                <tr style="border-bottom: 1px solid #eee;"><td>Adjusted Rate/70:</td><td style="text-align:right">₹{adj_rate:.2f}</td></tr>
                <tr style="border-bottom: 1px solid #eee;"><td>Rate per KG:</td><td style="text-align:right">₹{cost_per_kg:.4f}</td></tr>
                <tr><td colspan="2"><br></td></tr>
                <tr><td>Bags Amount ({bags}):</td><td style="text-align:right">₹{bags_amt:.2f}</td></tr>
                <tr><td>Extra KG Amount ({extra_kgs} kg):</td><td style="text-align:right">₹{extra_amt:.2f}</td></tr>
                <tr style="color:#2e7d32; font-weight:bold;"><td>GROSS TOTAL:</td><td style="text-align:right">₹{gross:.2f}</td></tr>
                <tr><td colspan="2"><hr></td></tr>
                <tr style="color:#d32f2f;"><td>(-) CC Charge (1%):</td><td style="text-align:right">₹{cc_val:.2f}</td></tr>
                <tr style="color:#d32f2f;"><td>(-) Hamali (₹5 x {bags}):</td><td style="text-align:right">₹{hamali:.2f}</td></tr>
                <tr><td colspan="2"><hr></td></tr>
                <tr style="font-size:1.8em; color:#1b5e20; font-weight:bold;"><td>Final Payment:</td><td style="text-align:right">₹{net:,.2f}</td></tr>
            </table>
        </div>
        """, unsafe_allow_html=True)
        
        st.write("---")
        # Action Buttons
        cp1, cp2 = st.columns(2)
        with cp1:
            pdf_bytes = create_pdf(f_name, bags, extra_kgs, input_cost, adj_rate, cost_per_kg, bags_amt, extra_amt, gross, cc_val, hamali, net, calc_type, current_sl)
            st.download_button("⬇️ Download PDF Bill", pdf_bytes, f"Bill_{current_sl}.pdf", "application/pdf")
        with cp2:
            if f_phone:
                msg = f"*PADDY BILL*\nBill No: {current_sl}\nFarmer: {f_name.upper()}\nNet Pay: ₹{net:,.2f}"
                wa_url = f"https://wa.me/{f_phone}?text={msg.replace(' ', '%20').replace('\n', '%0A')}"
                st.markdown(f'<a href="{wa_url}" target="_blank" style="text-decoration:none;"><button style="width:100%; background-color:#25d366; color:white; border:none; padding:10px; border-radius:5px; font-weight:bold; cursor:pointer;">Share on WhatsApp 📲</button></a>', unsafe_allow_html=True)

# --- HISTORY SECTION (ALWAYS BELOW) ---
st.markdown("---")
st.markdown("<h2 style='color: #2e7d32;'>📊 Billing History (Stored in CSV)</h2>", unsafe_allow_html=True)

if os.path.exists(DB_FILE):
    df = pd.read_csv(DB_FILE)
    st.dataframe(df.sort_values(by='SL_No', ascending=False), use_container_width=True)
    st.download_button("Download Full CSV Data", df.to_csv(index=False), "Full_Report.csv", "text/csv")
else:
    st.info("Bill Not Generated.")
