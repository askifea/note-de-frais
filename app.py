import streamlit as st
import pandas as pd
import re
from pdfminer.high_level import extract_text

# Function to extract invoice data
def extract_invoice_data(pdf_text, filename):
    pages = pdf_text.split('\x0c')  # Split text by pages
    data = []

    for page_number, page_text in enumerate(pages, start=1):
        # Extract fields using regex
        invoice_dates = re.findall(r"Date:\s*(\d{2}/\d{2}/\d{4})", page_text)
        amounts = re.findall(r"Total\s*:\s*([\d,.]+)", page_text)
        suppliers = re.findall(r"Supplier:\s*(.+)", page_text)
        descriptions = re.findall(r"Description:\s*(.+)", page_text)

        for i in range(max(len(invoice_dates), len(amounts), len(suppliers), len(descriptions))):
            data.append({
                "Numéro de page": page_number,
                "Date de la facture": invoice_dates[i] if i < len(invoice_dates) else None,
                "Montant": amounts[i] if i < len(amounts) else None,
                "Fournisseur": suppliers[i] if i < len(suppliers) else None,
                "Désignation": descriptions[i] if i < len(descriptions) else None,
                "Nom du fichier": filename
            })
    
    return pd.DataFrame(data)

# Streamlit App Setup
st.set_page_config(page_title="Invoice Extractor - Custom", page_icon="📄", layout="wide")
st.title("Invoice Extractor - Custom")

st.markdown("### Upload PDF invoices to extract and edit invoice details.")

# Initialize session state
if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = {}
if "extracted_data" not in st.session_state:
    st.session_state.extracted_data = pd.DataFrame()

# User Information Input
st.sidebar.header("User Information")
user_name = st.sidebar.text_input("Your Name")
user_company = st.sidebar.text_input("Your Company")

# File uploader
uploaded_files = st.file_uploader("Upload PDF invoices", type="pdf", accept_multiple_files=True)

# Process uploaded files
if uploaded_files:
    for uploaded_file in uploaded_files:
        if uploaded_file.name not in st.session_state.uploaded_files:
            pdf_text = extract_text(uploaded_file)
            invoice_data = extract_invoice_data(pdf_text, uploaded_file.name)
            st.session_state.uploaded_files[uploaded_file.name] = uploaded_file
            st.session_state.extracted_data = pd.concat(
                [st.session_state.extracted_data, invoice_data], ignore_index=True
            )

# Display extracted invoice data and allow user to edit
if not st.session_state.extracted_data.empty:
    st.markdown("### Edit Extracted Invoice Data")
    edited_data = st.data_editor(st.session_state.extracted_data, num_rows="dynamic")

    # Save updated data
    if st.button("Save Edited Data"):
        st.session_state.extracted_data = edited_data
        st.success("Data saved successfully!")

    # Download updated data
    st.markdown("### Download Updated Invoice Data")
    output_file = "Edited_Invoices.xlsx"
    st.session_state.extracted_data.to_excel(output_file, index=False)
    with open(output_file, "rb") as file:
        st.download_button(
            label="Download Edited Invoice Data",
            data=file,
            file_name="Edited_Invoices.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

