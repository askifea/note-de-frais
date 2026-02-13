"""
Note de Frais – Application Streamlit
Fonctionnalités :
  1. Sélecteur Société/École (liste déroulante)
  2. Choix de devise (€ par défaut) – montants TTC
  3. Champ obligatoire Imputation budgétaire
  4. Réinitialisation du formulaire après ajout (sauf Nom & Société)
  5. Export PDF fusionné (récapitulatif + pièces jointes)
  6. Catégories de dépenses conformes au template Excel
"""

import io
import streamlit as st
import pandas as pd
from datetime import date
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import mm
from pypdf import PdfWriter, PdfReader

# ─── Configuration ────────────────────────────────────────────────────────────
st.set_page_config(page_title="Note de Frais", page_icon="💼", layout="wide")
st.title("📝 Note de Frais - Gestion des Dépenses")

COMPANIES = [
    "IFEA SAS",
    "IFEA Bois Colombes",
    "Ecole Secondaire Suger",
    "MindEd Tech",
    "GIE IFEA",
]

EXPENSE_CATEGORIES = [
    "RECEPTION-INVITATIONS-REPAS",
    "HOTEL-HEBERGEMENT",
    "TRANSPORT - CARBURANT",
    "TELEPHONE",
    "AFFRANCHISSEMENT",
    "DIVERS",
]

# Display labels with accents for UI (mapped to storage keys above)
EXPENSE_LABELS = {
    "RECEPTION-INVITATIONS-REPAS": "RECEPTION-INVITATIONS-REPAS",
    "HOTEL-HEBERGEMENT":           "HÔTEL-HEBERGEMENT",
    "TRANSPORT - CARBURANT":       "TRANSPORT - CARBURANT",
    "TELEPHONE":                   "TÉLÉPHONE",
    "AFFRANCHISSEMENT":            "AFFRANCHISSEMENT",
    "DIVERS":                      "DIVERS",
}

CURRENCIES = {"€ (Euro)": "€", "$ (Dollar)": "$"}

MONTHS_FR = [
    "Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
    "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre",
]

# ─── Session State ─────────────────────────────────────────────────────────────
for key, default in [
    ("expense_data", []),
    ("uploaded_files_data", {}),
    ("form_key", 0),
    ("show_download", False),
    ("pdf_bytes", None),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ─── Sidebar ──────────────────────────────────────────────────────────────────
st.sidebar.header("Informations Utilisateur")
user_name = st.sidebar.text_input("👤 Nom")
user_company = st.sidebar.selectbox("🏢 Société/École", COMPANIES)
currency_label = st.sidebar.selectbox(
    "💱 Devise (montants TTC)", list(CURRENCIES.keys()), index=0
)
currency = CURRENCIES[currency_label]

# ─── ReportLab style objects ──────────────────────────────────────────────────
_base = getSampleStyleSheet()
_hdr = ParagraphStyle(
    "hdr", parent=_base["Normal"],
    fontName="Helvetica-Bold", fontSize=7, alignment=1, leading=9,
)
_cel = ParagraphStyle(
    "cel", parent=_base["Normal"],
    fontName="Helvetica", fontSize=7, alignment=1, leading=9,
)
_ttl = ParagraphStyle("ttl", parent=_base["Heading1"], fontSize=16, leading=20)
_nrm = ParagraphStyle("nrm", parent=_base["Normal"], fontSize=10, leading=13)


def _p(text, style=None):
    return Paragraph(str(text) if text else "", style or _cel)


# ─── PDF helpers ──────────────────────────────────────────────────────────────
def generate_expense_pdf(df: pd.DataFrame, name: str, company: str, cur: str) -> bytes:
    """Render the expense-summary page as a landscape A4 PDF."""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=landscape(A4),
        leftMargin=10*mm, rightMargin=10*mm,
        topMargin=10*mm, bottomMargin=10*mm,
    )
    story = []

    current_month = MONTHS_FR[date.today().month - 1]
    story.append(_p("NOTE DE FRAIS", _ttl))
    story.append(_p(f"<b>Société/École :</b> {company}", _nrm))
    story.append(_p(
        f"<b>Nom :</b> {name}   |   <b>Mois :</b> {current_month} {date.today().year}", _nrm,
    ))
    story.append(Spacer(1, 6*mm))

    headers = [
        _p("Date de\nDépense", _hdr),
        _p("Fournisseur", _hdr),
        _p("Objet\n(Description)", _hdr),
        _p("Imputation\nbudgétaire", _hdr),
        _p("RECEPTION-\nINVITATIONS-\nREPAS (TTC)", _hdr),
        _p("HÔTEL-\nHEBERGEMENT\n(TTC)", _hdr),
        _p("TRANSPORT -\nCARBURANT\n(TTC)", _hdr),
        _p("TÉLÉPHONE\n(TTC)", _hdr),
        _p("AFFRAN-\nCHISSEMENT\n(TTC)", _hdr),
        _p("DIVERS\n(TTC)", _hdr),
        _p(f"TOTAL\n({cur})", _hdr),
    ]
    rows = [headers]
    totals = {cat: 0.0 for cat in EXPENSE_CATEGORIES}
    amt_col = f"Montant TTC ({cur})"

    for _, row in df.iterrows():
        cat_vals = {cat: "" for cat in EXPENSE_CATEGORIES}
        rtype = row.get("Type", "")
        if rtype in EXPENSE_CATEGORIES:
            try:
                v = float(row.get(amt_col, 0))
                cat_vals[rtype] = f"{v:.2f}"
                totals[rtype] += v
            except (ValueError, TypeError):
                pass
        row_total = sum(float(x) for x in cat_vals.values() if x)
        rows.append(
            [
                _p(row.get("Date", "")),
                _p(row.get("Fournisseur", "")),
                _p(row.get("Objet", "")),
                _p(row.get("Imputation budgétaire", "")),
            ]
            + [_p(cat_vals[c]) for c in EXPENSE_CATEGORIES]
            + [_p(f"{row_total:.2f}")]
        )

    grand = sum(totals.values())
    rows.append(
        [_p("TOTAUX", _hdr), _p(""), _p(""), _p("")]
        + [_p(f"{totals[c]:.2f}", _hdr) for c in EXPENSE_CATEGORIES]
        + [_p(f"{grand:.2f}", _hdr)]
    )

    col_widths = [22*mm, 32*mm, 40*mm, 28*mm, 24*mm, 22*mm, 24*mm, 18*mm, 21*mm, 15*mm, 20*mm]
    tbl = Table(rows, colWidths=col_widths, repeatRows=1)
    tbl.setStyle(TableStyle([
        ("BACKGROUND",     (0, 0),  (-1, 0),  colors.HexColor("#757070")),
        ("TEXTCOLOR",      (0, 0),  (-1, 0),  colors.white),
        ("FONTNAME",       (0, 0),  (-1, 0),  "Helvetica-Bold"),
        ("BACKGROUND",     (0, -1), (-1, -1), colors.HexColor("#A5A5A5")),
        ("FONTNAME",       (0, -1), (-1, -1), "Helvetica-Bold"),
        ("GRID",           (0, 0),  (-1, -1), 0.5, colors.grey),
        ("VALIGN",         (0, 0),  (-1, -1), "MIDDLE"),
        ("TOPPADDING",     (0, 0),  (-1, -1), 3),
        ("BOTTOMPADDING",  (0, 0),  (-1, -1), 3),
        ("ROWBACKGROUNDS", (0, 1),  (-1, -2), [colors.white, colors.HexColor("#F2F2F2")]),
    ]))
    story.append(tbl)
    story.append(Spacer(1, 10*mm))

    sig_data = [
        [_p("Le bénéficiaire", _hdr), _p("La direction", _hdr), _p("La comptabilité", _hdr)],
        [_p(""), _p(""), _p("")],
        [_p("Date :"), _p("Date :"), _p("Date :")],
    ]
    sig = Table(sig_data, colWidths=[80*mm, 80*mm, 80*mm])
    sig.setStyle(TableStyle([
        ("ALIGN",      (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING", (0, 1), (-1, 1), 25),
        ("GRID",       (0, 0), (-1, -1), 0.3, colors.HexColor("#BBBBBB")),
    ]))
    story.append(sig)
    doc.build(story)
    buf.seek(0)
    return buf.read()


def image_to_pdf_bytes(img_bytes: bytes) -> bytes:
    """Wrap a JPG/PNG image into a single-page PDF."""
    from reportlab.pdfgen import canvas as rl_canvas
    from reportlab.lib.utils import ImageReader
    from PIL import Image as PILImage

    img = PILImage.open(io.BytesIO(img_bytes))
    pw, ph = A4
    margin = 15*mm
    max_w, max_h = pw - 2*margin, ph - 2*margin
    ratio = min(max_w / img.width, max_h / img.height)
    dw, dh = img.width * ratio, img.height * ratio
    x = margin + (max_w - dw) / 2
    y = margin + (max_h - dh) / 2

    buf = io.BytesIO()
    c = rl_canvas.Canvas(buf, pagesize=A4)
    tmp = io.BytesIO()
    img.save(tmp, format="PNG")
    tmp.seek(0)
    c.drawImage(ImageReader(tmp), x, y, width=dw, height=dh, preserveAspectRatio=True)
    c.save()
    buf.seek(0)
    return buf.read()


def generate_full_pdf(df, name, company, cur, uploaded_files):
    """Merge expense-summary PDF with all uploaded receipts."""
    writer = PdfWriter()
    summary = generate_expense_pdf(df, name, company, cur)
    for page in PdfReader(io.BytesIO(summary)).pages:
        writer.add_page(page)
    for _, fdata in uploaded_files.items():
        try:
            fbytes = fdata["bytes"]
            if fdata["is_pdf"]:
                for page in PdfReader(io.BytesIO(fbytes)).pages:
                    writer.add_page(page)
            elif fdata["is_image"]:
                for page in PdfReader(io.BytesIO(image_to_pdf_bytes(fbytes))).pages:
                    writer.add_page(page)
        except Exception:
            pass
    out = io.BytesIO()
    writer.write(out)
    out.seek(0)
    return out.read()


# ─── Expense Form ─────────────────────────────────────────────────────────────
st.markdown("## 📅 Ajoutez vos Dépenses")

with st.form(key=f"expense_form_{st.session_state.form_key}"):
    col1, col2, col3 = st.columns(3)

    with col1:
        expense_date = st.date_input("📆 Date de Dépense", value=date.today())
        supplier = st.text_input("🏪 Fournisseur")

    with col2:
        object_desc = st.text_input("📝 Objet (Description)")
        expense_type = st.selectbox(
            "📌 Type de Dépense",
            EXPENSE_CATEGORIES,
            format_func=lambda k: EXPENSE_LABELS[k],
        )

    with col3:
        amount = st.number_input(f"💰 Montant TTC ({currency})", min_value=0.0, format="%.2f")
        budget_input = st.text_input("📊 Imputation budgétaire *")
        uploaded_file = st.file_uploader(
            "📄 Joindre un Justificatif", type=["pdf", "jpg", "jpeg", "png"]
        )

    submitted = st.form_submit_button("✅ Ajouter Dépense")

# ─── Submission handling ──────────────────────────────────────────────────────
if submitted:
    errors = []
    if not user_name.strip():
        errors.append("Nom (barre latérale)")
    if not supplier.strip():
        errors.append("Fournisseur")
    if not object_desc.strip():
        errors.append("Objet")
    if amount <= 0:
        errors.append("Montant TTC (> 0)")
    if not budget_input.strip():
        errors.append("**Imputation budgétaire** ⚠️ champ obligatoire")
    if not uploaded_file:
        errors.append("Justificatif (pièce jointe)")

    if errors:
        st.warning("⚠️ Champs manquants / invalides : " + " | ".join(errors))
    else:
        file_bytes = uploaded_file.read()
        file_name = uploaded_file.name
        ext = file_name.lower().rsplit(".", 1)[-1]

        st.session_state.expense_data.append({
            "Date":                  expense_date.strftime("%d/%m/%Y"),
            "Fournisseur":           supplier.strip(),
            "Objet":                 object_desc.strip(),
            "Type":                  expense_type,
            f"Montant TTC ({currency})": amount,
            "Imputation budgétaire": budget_input.strip(),
            "Justificatif":          file_name,
        })
        st.session_state.uploaded_files_data[file_name] = {
            "bytes":    file_bytes,
            "name":     file_name,
            "is_pdf":   ext == "pdf",
            "is_image": ext in ("jpg", "jpeg", "png"),
        }
        # Reset form fields (sidebar Nom & Société unchanged)
        st.session_state.form_key += 1
        st.session_state.show_download = False
        st.session_state.pdf_bytes = None
        st.success(f"🎉 Dépense ajoutée ! Pièce jointe : **{file_name}**")
        st.rerun()

# ─── Expenses table & export ──────────────────────────────────────────────────
if st.session_state.expense_data:
    st.markdown("## 📋 Liste des Dépenses")
    df = pd.DataFrame(st.session_state.expense_data)
    edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)

    btn_col1, btn_col2, btn_col3 = st.columns([1, 2, 1])

    with btn_col1:
        if st.button("💾 Sauvegarder Modifications"):
            st.session_state.expense_data = edited_df.to_dict(orient="records")
            st.success("✅ Modifications enregistrées !")

    with btn_col2:
        if st.button("📄 Générer la Note de Frais PDF", type="primary"):
            if not user_name.strip():
                st.warning("⚠️ Veuillez saisir votre Nom dans la barre latérale.")
            else:
                with st.spinner("Génération du PDF fusionné (récapitulatif + pièces jointes)…"):
                    try:
                        df_export = pd.DataFrame(st.session_state.expense_data)
                        st.session_state.pdf_bytes = generate_full_pdf(
                            df_export, user_name, user_company, currency,
                            st.session_state.uploaded_files_data,
                        )
                        st.session_state.show_download = True
                    except Exception as e:
                        st.error(f"Erreur lors de la génération du PDF : {e}")

    with btn_col3:
        if st.button("🗑️ Tout effacer"):
            for k in ["expense_data", "uploaded_files_data", "pdf_bytes"]:
                st.session_state[k] = [] if k == "expense_data" else ({} if k == "uploaded_files_data" else None)
            st.session_state.show_download = False
            st.rerun()

    # Download button (shown after generation)
    if st.session_state.show_download and st.session_state.pdf_bytes:
        month_str = MONTHS_FR[date.today().month - 1]
        filename = f"NDF_{user_name.replace(' ', '_')}_{month_str}_{date.today().year}.pdf"
        st.download_button(
            label="⬇️ Télécharger la Note de Frais (PDF fusionné)",
            data=st.session_state.pdf_bytes,
            file_name=filename,
            mime="application/pdf",
            use_container_width=True,
        )

    # Summary totals
    st.markdown("### 📊 Récapitulatif par catégorie")
    amt_col = f"Montant TTC ({currency})"
    if amt_col in df.columns:
        summary = (
            df.groupby("Type")[amt_col]
            .sum()
            .reset_index()
            .rename(columns={amt_col: f"Total TTC ({currency})"})
        )
        summary["Type"] = summary["Type"].map(lambda k: EXPENSE_LABELS.get(k, k))
        summary[f"Total TTC ({currency})"] = summary[f"Total TTC ({currency})"].map(
            lambda x: f"{x:.2f} {currency}"
        )
        st.dataframe(summary, use_container_width=True, hide_index=True)
        st.metric("💰 Total général TTC", f"{df[amt_col].sum():.2f} {currency}")
