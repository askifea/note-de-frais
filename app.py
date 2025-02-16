import streamlit as st
import pandas as pd
import os

# Set Page Config
st.set_page_config(page_title="Note de Frais", page_icon="💼", layout="wide")
st.title("📝 Note de Frais - Gestion des Dépenses")

# Sidebar for User Information
st.sidebar.header("Informations Utilisateur")
user_name = st.sidebar.text_input("👤 Nom")
user_company = st.sidebar.text_input("🏢 Entreprise")

# Initialize Session State for Expense Data
if "expense_data" not in st.session_state:
    st.session_state.expense_data = []

# Initialize Session State for Uploaded Files
if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = {}

# Define Expense Categories
expense_categories = [
    "Restaurant Bill", "Gas Bill", "Transportation Bill",
    "Ticket", "Indemnité Kilométrique", "Miscellaneous"
]

st.markdown("## 📅 Ajoutez vos Dépenses")

# Expense Entry Form
with st.form(key="expense_form"):
    col1, col2, col3 = st.columns(3)

    with col1:
        expense_date = st.date_input("📆 Date de Dépense")
        supplier = st.text_input("🏪 Fournisseur")

    with col2:
        object_desc = st.text_input("📝 Objet (Description)")
        expense_type = st.selectbox("📌 Type de Dépense", expense_categories)

    with col3:
        amount = st.number_input("💰 Montant (€)", min_value=0.0, format="%.2f")
        uploaded_file = st.file_uploader("📄 Joindre un Justificatif", type=["pdf", "jpg", "png"])

    submitted = st.form_submit_button("✅ Ajouter Dépense")

# Process Submission
if submitted:
    if not user_name or not user_company:
        st.warning("⚠️ Veuillez entrer votre nom et votre entreprise avant d'ajouter une dépense.")
    elif not expense_date or not supplier or not object_desc or not amount or not uploaded_file:
        st.warning("⚠️ Veuillez remplir tous les champs et téléverser un justificatif.")
    else:
        # Save File
        file_path = f"uploads/{uploaded_file.name}"
        os.makedirs("uploads", exist_ok=True)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Save Expense Entry
        new_expense = {
            "Date": expense_date.strftime("%Y-%m-%d"),
            "Fournisseur": supplier,
            "Objet": object_desc,
            "Type": expense_type,
            "Montant (€)": amount,
            "Justificatif": uploaded_file.name
        }

        st.session_state.expense_data.append(new_expense)
        st.session_state.uploaded_files[uploaded_file.name] = file_path

        st.success("🎉 Dépense ajoutée avec succès!")

# Display Expenses Table
if st.session_state.expense_data:
    st.markdown("## 📋 Liste des Dépenses")

    df_expenses = pd.DataFrame(st.session_state.expense_data)
    edited_df = st.data_editor(df_expenses, num_rows="dynamic")

    # Save Updates
    if st.button("💾 Sauvegarder Modifications"):
        st.session_state.expense_data = edited_df.to_dict(orient="records")
        st.success("✅ Modifications enregistrées!")

    # Download Excel
    st.markdown("### 📥 Télécharger le Fichier Excel")
    output_file = "Note_de_Frais.xlsx"
    df_expenses.to_excel(output_file, index=False)

    with open(output_file, "rb") as file:
        st.download_button(
            label="💾 Télécharger Note de Frais",
            data=file,
            file_name="Note_de_Frais.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
