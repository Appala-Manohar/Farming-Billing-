import streamlit as st
from fpdf import FPDF
from datetime import datetime
import pandas as pd
import csv
import os

# --- Security Configuration ---
USER_NAME = "admin"
PASSWORD = "Nageswara Rao"

# --- Database File Setup ---
DB_FILE = 'paddy_billing_history.csv'
HEADERS = ['SL_No', 'Date', 'Farmer_Name', 'Calc_Type', 'Bags', 'Extra_KGs', 'Input_Rate', 'Gross_Total', 'Advance_Paid', 'Net_Payable']

# --- Helper Functions ---
def get_next_sl_no():
    if os.path.exists(DB_FILE):
        try:
            df = pd.read_csv(DB_FILE)
            if not df.empty:
                if list(df.columns) != HEADERS:
                    os.remove(DB_FILE)
                    return 1
                return int(df['SL_No'].max()) + 1
        except:
            return 1
    return 1

def create_pdf(f_name, bags, extra_kgs, input_cost, adj_rate, cost_per_kg, bags_amt, extra_amt, gross, cc, hamali, advance, net, calc_type, sl_no):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, "SRI SAI LAKSHMI OFFICE", ln=True, align='C')
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, "PADDY PURCHASE RECEIPT", ln=True, align='C')
    pdf.set_font("Arial", '', 11)
    pdf.cell(200, 10, f"Bill No: {sl_no} | Date: {datetime.now().strftime('%d/%m/%Y')}", ln=True, align='R')
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, f"Farmer Name: {f_name.upper()}", ln=True)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)
    pdf.set_font("Arial", '', 11)
    pdf.cell(150, 8, f"Bags Amount ({bags} bags):")
    pdf.cell(30, 8, f"Rs. {bags_amt:.2f}", ln=True, align='R')
    pdf.cell(150, 8, f"Extra KG Amount ({extra_kgs} kg):")
    pdf.cell(30, 8, f"Rs. {extra_amt:.2f}", ln=True, align='R')
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(150, 8, "GROSS TOTAL:")
    pdf.cell(30, 8, f"Rs. {gross:.2f}", ln=True, align='R')
    pdf.ln(5)
    pdf.set_font("Arial", '', 11)
    pdf.cell(150, 8, f"(-) CC Charge (1%):")
    pdf.cell(30, 8, f"Rs. {cc:.2f}", ln=True, align='R')
    pdf.cell(150, 8, f"(-) Hamali (Rs. 5 per bag):")
    pdf.cell(30, 8, f"Rs. {hamali:.2f}", ln=True, align='R')
    pdf.cell(150, 8, "(-) Advance Paid:")
    pdf.cell(30, 8, f"Rs. {advance:.2f}", ln=True, align='R')
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(150, 10, "Net Payable:")
    pdf.cell(30, 10, f"Rs. {net:,.2f}", ln=True, align='R')
    return pdf.output(dest='S').encode('latin-1')

# ============================================================
# LOGIN PAGE
# ============================================================
def login():
    st.markdown("<h1 style='text-align:center; color:#1e4d2b;'>🏢 SRI SAI LAKSHMI OFFICE</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center;'>Private Access Login</h3>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            user = st.text_input("Username")
            password = st.text_input("Password", type="password")
            if st.form_submit_button("Login", use_container_width=True):
                if user == USER_NAME and password == PASSWORD:
                    st.session_state['logged_in'] = True
                    st.rerun()
                else:
                    st.error("Wrong Username or Password!")

# ============================================================
# MAIN APPLICATION
# ============================================================
def main_app():
    st.set_page_config(page_title="SRI SAI LAKSHMI OFFICE", page_icon="🌾", layout="wide")

    st.markdown("""
    <style>
        .stApp { background-color: #f4f7f6; }
        .hero-banner {
            background: linear-gradient(135deg, #1e4d2b 0%, #2d5a27 100%);
            border-radius: 20px; padding: 40px; color: white;
            display: flex; justify-content: space-between; align-items: center;
            margin-bottom: 30px; box-shadow: 0 10px 30px rgba(30, 77, 43, 0.2);
        }
        .stat-box {
            background: rgba(255, 255, 255, 0.15); padding: 15px 25px; 
            border-radius: 12px; text-align: center; border: 1px solid rgba(255, 255, 255, 0.2);
        }
        .stat-val { font-size: 1.8rem; font-weight: 700; color: #f5e6a3; }
        .receipt-card { background: white; padding: 30px; border-radius: 20px; border: 1px solid #e0e6ed; }
        .receipt-row { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #f0f4f8; }
        .final-row { background: #1e4d2b; color: #f5e6a3; padding: 15px; border-radius: 10px; margin-top: 15px; font-size: 1.4rem; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.markdown(f"### Logged in as: **{USER_NAME.upper()}**")
        if st.button("Logout", type="secondary"):
            st.session_state['logged_in'] = False
            st.rerun()

    # --- DASHBOARD STATS ---
    t_paid, t_bags, t_farmers = 0, 0, 0
    if os.path.exists(DB_FILE):
        df_m = pd.read_csv(DB_FILE)
        if not df_m.empty:
            t_paid = df_m['Net_Payable'].sum()
            t_bags = df_m['Bags'].sum()
            t_farmers = df_m['Farmer_Name'].nunique()

    st.markdown(f"""
    <div class="hero-banner">
        <div>
            <h1 style="margin:0; font-family:serif; font-size: 3rem; color: #f5e6a3;">SRI SAI LAKSHMI OFFICE 🌾</h1>
            <p style="opacity:0.9;">Professional Paddy Procurement System</p>
            <div style="display: flex; gap: 20px; margin-top: 20px;">
                <div class="stat-box"><div class="stat-val">₹{t_paid:,.0f}</div><div>Total Payout</div></div>
                <div class="stat-box"><div class="stat-val">{t_bags}</div><div>Total Bags</div></div>
                <div class="stat-box"><div class="stat-val">{t_farmers}</div><div>Total Farmers</div></div>
            </div>
        </div>
        <div style="font-size: 7rem; opacity: 0.8;">🏢</div>
    </div>
    """, unsafe_allow_html=True)

    # --- BILLING LOGIC ---
    col_in, col_out = st.columns([1, 1.2], gap="large")

    with col_in:
        st.markdown("### 📝 New Bill Entry")
        current_sl = get_next_sl_no()
        logic = st.selectbox("Procurement Logic", ("75kg Sum", "100kg Quintal Sum"))
        f_name = st.text_input("Farmer Name:", placeholder="Enter Farmer Name")
        f_phone = st.text_input("WhatsApp Number (91XXXXXXXXXX):")
        
        c1, c2 = st.columns(2)
        with c1:
            bags_v = st.number_input("Total Bags (బస్తాలు):", min_value=0, step=1)
            extra_v = st.number_input("Extra KGs:", min_value=0.0)
        with c2:
            rate_v = st.number_input("Input Rate:", value=1855.0 if logic=="75kg Sum" else 2480.0)
            advance_v = st.number_input("Advance Paid:", value=0.0)
        
        apply_cc = st.checkbox("Apply 1% CC Charge", value=True)
        
        if st.button("Generate Bill & Save", type="primary", use_container_width=True):
            if not f_name:
                st.error("Farmer Name required!")
            else:
                if logic == "75kg Sum":
                    adj_rate = rate_v * (68/75)
                    cost_per_kg = adj_rate / 70
                    bags_amt = adj_rate * bags_v
                    extra_amt = cost_per_kg * extra_v
                else:
                    cost_per_kg = rate_v / 100
                    bags_amt = (bags_v * 68) * cost_per_kg
                    extra_amt = extra_v * cost_per_kg
                    adj_rate = 0

                gross = bags_amt + extra_amt
                cc_v = gross * 0.01 if apply_cc else 0.0
                hamali = bags_v * 5
                net = gross - cc_v - hamali - advance_v

                if not os.path.exists(DB_FILE):
                    pd.DataFrame(columns=HEADERS).to_csv(DB_FILE, index=False)
                with open(DB_FILE, mode='a', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow([current_sl, datetime.now().strftime('%d/%m/%Y'), f_name.upper(), logic, bags_v, extra_v, rate_v, round(gross, 2), round(advance_v, 2), round(net, 2)])
                
                st.session_state['last_bill'] = {
                    'sl': current_sl, 'name': f_name, 'logic': logic, 'bags': bags_v, 'extra': extra_v,
                    'b_amt': bags_amt, 'e_amt': extra_amt, 'gross': gross, 'cc': cc_v, 'hamali': hamali,
                    'advance': advance_v, 'net': net, 'phone': f_phone, 'adj': adj_rate, 'cpk': cost_per_kg, 'rate': rate_v
                }
                st.rerun()

    with col_out:
        st.markdown("### 🖼️ Receipt Preview")
        if 'last_bill' in st.session_state:
            b = st.session_state['last_bill']
            st.markdown(f"""
            <div class="receipt-card">
                <div style="border-bottom: 2px solid #1e4d2b; padding-bottom: 10px; margin-bottom: 15px;">
                    <h2 style="margin:0; color:#1e4d2b;">SRI SAI LAKSHMI OFFICE</h2>
                    <span style="color:#666;">Bill No: #{b['sl']} | Date: {datetime.now().strftime('%d/%m/%Y')}</span>
                </div>
                <p><b>Farmer Name:</b> {b['name'].upper()}</p>
                <div class="receipt-row"><span>Bags Amt ({b['bags']} bags)</span><span>₹{b['b_amt']:,.2f}</span></div>
                <div class="receipt-row"><span>Extra KGs ({b['extra']}kg)</span><span>₹{b['e_amt']:,.2f}</span></div>
                <div class="receipt-row" style="font-weight:bold; border-bottom: 2px solid #eee;"><span>Gross Total</span><span>₹{b['gross']:,.2f}</span></div>
                <div class="receipt-row" style="color:#b94a2c;"><span>(-) CC Charge (1%)</span><span>₹{b['cc']:,.2f}</span></div>
                <div class="receipt-row" style="color:#b94a2c;"><span>(-) Hamali (₹5/bag)</span><span>₹{b['hamali']:,.2f}</span></div>
                <div class="receipt-row" style="color:#b94a2c; font-weight:bold;"><span>(-) Advance Paid</span><span>₹{b['advance']:,.2f}</span></div>
                <div class="final-row" style="display:flex; justify-content:space-between;">
                    <span>NET PAYMENT</span><span>₹{b['net']:,.2f}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.write("")
            bt1, bt2, bt3 = st.columns(3)
            with bt1:
                pdf = create_pdf(b['name'], b['bags'], b['extra'], b['rate'], b['adj'], b['cpk'], b['b_amt'], b['e_amt'], b['gross'], b['cc'], b['hamali'], b['advance'], b['net'], b['logic'], b['sl'])
                st.download_button("📥 Download PDF", pdf, f"Bill_{b['sl']}.pdf", use_container_width=True)
            with bt2:
                if b['phone']:
                    wa_msg = f"*SRI SAI LAKSHMI OFFICE*\n*Bill No:* {b['sl']}\n*Farmer:* {b['name'].upper()}\n*Net Payable: ₹{b['net']:,.2f}*"
                    wa_url = f"https://wa.me/{b['phone']}?text={wa_msg.replace(' ', '%20').replace('\n', '%0A')}"
                    st.markdown(f'<a href="{wa_url}" target="_blank"><button style="width:100%; background:#25d366; color:white; border:none; padding:10px; border-radius:10px; cursor:pointer; font-weight:bold;">📲 WhatsApp Share</button></a>', unsafe_allow_html=True)
            with bt3:
                if st.button("🔄 Next Bill", use_container_width=True):
                    del st.session_state['last_bill']
                    st.rerun()

    # --- HISTORY & DELETE SECTION ---
    st.write("---")
    st.markdown("### 📊 Transaction History & Search")
    if os.path.exists(DB_FILE):
        df_h = pd.read_csv(DB_FILE)
        
        search = st.text_input("🔍 Search Farmer/Bags:", "")
        if search:
            df_h = df_h[df_h['Farmer_Name'].str.contains(search.upper(), na=False) | (df_h['Bags'].astype(str) == search)]
        
        # Display table
        st.dataframe(df_h.sort_values(by='SL_No', ascending=False), use_container_width=True)
        
        # ROW DELETE OPTION (RE-ADDED)
        with st.expander("🗑️ Delete a Record"):
            del_id = st.number_input("Enter SL No (Bill No) to Delete:", min_value=1, step=1)
            if st.button("Confirm Delete Permanently", type="primary"):
                df_h_orig = pd.read_csv(DB_FILE)
                if del_id in df_h_orig['SL_No'].values:
                    df_h_orig = df_h_orig[df_h_orig['SL_No'] != del_id]
                    df_h_orig.to_csv(DB_FILE, index=False)
                    st.success(f"Bill No #{del_id} deleted successfully!")
                    st.rerun()
                else:
                    st.error("Their is no Bil Number!")

# --- APP START ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if st.session_state['logged_in']:
    main_app()
else:
    login()
