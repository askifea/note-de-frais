import streamlit as st
import pandas as pd
import re
from pdfminer.high_level import extract_text

# Debugging Function to Print PDF Text
def debug_print_pdf(pdf_text):
    st.write("### Extracted PDF Text (First 500 Characters)")
    st.write(pdf_text[:500])

# Function to Extract Invoice Data
def extract_invoice_data(pdf_text, filename):
    pages = pdf_text.split('\x0c')  # Split text by pages
    data = []

    for page_number, page_text in enumerate(pages, start=1):
        # Debug: Show Extracted Text from Each Page
        debug_print_pdf(page_text)

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
st.set_page_config(page_title="Note de Frais", page_icon="📄", layout="wide")
st.title("Note de Frais - Gestion des Factures")

st.markdown("### Téléchargez des factures en PDF pour extraction et édition.")

# Initialize session state
if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = {}
if "extracted_data" not in st.session_state:
    st.session_state.extracted_data = pd.DataFrame()

# User Information Input
st.sidebar.header("Informations de l'Utilisateur")
user_name = st.sidebar.text_input("Votre Nom")
user_company = st.sidebar.text_input("Votre Entreprise")

# File uploader
uploaded_files = st.file_uploader("Téléchargez vos factures (PDF)", type="pdf", accept_multiple_files=True)

# Process uploaded files
if uploaded_files:
    for uploaded_file in uploaded_files:
        if uploaded_file.name not in st.session_state.uploaded_files:
            st.write(f"📂 **Processing file:** {uploaded_file.name}")  # Debugging line
            pdf_text = extract_text(uploaded_file)
            
            if not pdf_text.strip():
                st.error(f"🚨 Erreur : Impossible d'extraire du texte du fichier `{uploaded_file.name}`")
            else:
                invoice_data = extract_invoice_data(pdf_text, uploaded_file.name)
                st.session_state.uploaded_files[uploaded_file.name] = uploaded_file
                st.session_state.extracted_data = pd.concat(
                    [st.session_state.extracted_data, invoice_data], ignore_index=True
                )

# Display extracted invoice data and allow user to edit
if not st.session_state.extracted_data.empty:
    st.markdown("### Modifier les Données des Factures")
    edited_data = st.data_editor(st.session_state.extracted_data, num_rows="dynamic")

    # Save updated data
    if st.button("✅ Sauvegarder les Modifications"):
        st.session_state.extracted_data = edited_data
        st.success("✔️ Données mises à jour avec succès!")

    # Download updated data
    st.markdown("### 📥 Télécharger les Données des Factures")
    output_file = "Factures_Modifiées.xlsx"
    st.session_state.extracted_data.to_excel(output_file, index=False)
    
    with open(output_file, "rb") as file:
        st.download_button(
            label="💾 Télécharger les Factures Modifiées",
            data=file,
            file_name="Factures_Modifiées.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
else:
    st.info("📌 **Aucune donnée extraite.** Veuillez télécharger des fichiers PDF pour voir les résultats.")

