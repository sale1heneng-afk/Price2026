import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Price Management System", layout="wide")
st.title("📊 Industrial Hardware Price List")

# --- Google Sheets Connection ---
conn = st.connection("gsheets", type=GSheetsConnection)

# Data load karne ka function
def load_data():
    return conn.read(ttl=0)

df = load_data()

# --- Admin Section ---
st.sidebar.header("Admin Control")
admin_password = st.sidebar.text_input("Admin Password enter karein", type="password")

if admin_password == "admin123":
    st.subheader("Add or Update Prices")
    with st.form("entry_form", clear_on_submit=True):
        model = st.text_input("Model Number").strip().upper()
        price_input = st.text_input("Price (Sirf amount likhein, $ khud lag jayega)").strip()
        submit = st.form_submit_button("Add to Cloud List")

        if submit and model:
            if not price_input:
                st.error("⚠️ Model ke sath Price likhna zaroori hai!")
            else:
                # Dollar ($) Sign Logic
                price = price_input if price_input.startswith("$") else "$" + price_input
                today = datetime.now().strftime("%Y-%m-%d %H:%M")
                
                new_entry = pd.DataFrame([{"Model": model, "Price": price, "Date": today}])
                
                # Duplicate Check Logic
                if not df.empty and model in df["Model"].values:
                    st.warning(f"Model '{model}' pehle se maujood hai!")
                    choice = st.radio("Aap kya karna chahte hain?", ["Replace (Update Price)", "Duplicate (Nayi entry karein)"])
                    
                    if choice == "Replace (Update Price)":
                        df = df[df["Model"] != model] # Purana nikal dein
                        updated_df = pd.concat([df, new_entry], ignore_index=True)
                        conn.update(data=updated_df)
                        st.success(f"Price update ho kar {price} ho gayi!")
                    else:
                        updated_df = pd.concat([df, new_entry], ignore_index=True)
                        conn.update(data=updated_df)
                        st.success("Nayi entry (Duplicate) add ho gayi!")
                else:
                    updated_df = pd.concat([df, new_entry], ignore_index=True)
                    conn.update(data=updated_df)
                    st.success(f"Model {price} ke sath add ho gaya!")
                
                # Nayi list show karne ke liye page refresh karein
                st.rerun()

# --- View Section (Sab ke liye) ---
st.subheader("Current Price List")
search_query = st.text_input("Model search karein...", "")

if not df.empty:
    df["Model"] = df["Model"].astype(str)
    if search_query:
        filtered_df = df[df["Model"].str.contains(search_query.upper(), na=False)]
    else:
        filtered_df = df
    
    st.dataframe(filtered_df, use_container_width=True)
    
    # --- Download Section ---
    st.subheader("Download for Client")
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download List as CSV (Excel Compatible)",
        data=csv,
        file_name=f"Price_List_{datetime.now().strftime('%Y-%m-%d')}.csv",
        mime='text/csv',
    )
else:
    st.info("List abhi khali hai. Admin panel se models add karein.")
