import streamlit as st
import fitz  # PyMuPDF
from io import BytesIO

# Set up page config
st.set_page_config(page_title="Samagra Interiors - PDF Merger", page_icon="📄", layout="centered")

# Custom CSS
st.markdown(
    """
    <style>
    .stApp {
        background-color: #9BD24B !important;
    }

    h1 {
        color: #fff;
        text-align: center;
        font-weight: 900;
        font-size: 3rem;
        margin: 0.5em 0;
    }

    /* File uploader container */
    .stFileUploader {
        border-radius: 14px;
        background: #1f3a8a !important;
        color: #fff;
        padding: 1rem;
    }
    .stFileUploader > div { color: #fff; }

    /* Blue buttons for Generate & Download */
    .stButton > button,
    .stDownloadButton > button {
        background-color: #003366 !important;
        color: #fff !important;
        border-radius: 8px !important;
        border: none !important;
        font-size: 1.05rem !important;
        padding: 0.5em 1.0em !important;
    }

    /* Dark blue success message */
    .dark-blue-success {
        color: #003366;
        font-weight: bold;
        font-size: 1.1rem;
    }

    /* Blue caption text */
    .blue-caption {
        color: #003366;
        text-align: center;
        font-size: 1.05rem;
        font-weight: 600;
        margin-bottom: 1em;
    }

    /* Custom blue error message */
    .blue-error {
        color: #003366 !important;
        font-weight: bold;
        font-size: 1.1rem !important;
        text-align: center;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Title
st.markdown("<h1>Samagra Interiors - PDF Merger Tool</h1>", unsafe_allow_html=True)
st.markdown(
    "<p class='blue-caption'>Merge Header, Quotation, Template Background, and Footer PDFs into one final file.</p>",
    unsafe_allow_html=True
)

# 2x2 grid for uploads
col1, col2 = st.columns(2)
with col1:
    header_pdf = st.file_uploader("Header PDF", type="pdf", key="header")
with col2:
    quotation_pdf = st.file_uploader("Quotation PDF (required)", type="pdf", key="quote")
col3, col4 = st.columns(2)
with col3:
    background_pdf = st.file_uploader("Background Template", type="pdf", key="bg")
with col4:
    footer_pdf = st.file_uploader("Footer PDF", type="pdf", key="foot")

# Helpers for PDF merging
def check_size(file_obj):
    return not file_obj or file_obj.size <= 200 * 1024 * 1024

def overlay_with_background(main_pdf_bytes, background_pdf_bytes):
    main_doc = fitz.open(stream=main_pdf_bytes, filetype="pdf")
    bg_doc = fitz.open(stream=background_pdf_bytes, filetype="pdf")
    result = fitz.open()
    for page_index in range(len(main_doc)):
        new_page = result.new_page(width=595.28, height=841.89)
        new_page.show_pdf_page(new_page.rect, bg_doc, 0)
        new_page.show_pdf_page(new_page.rect, main_doc, page_index)
    output = BytesIO()
    result.save(output)
    result.close()
    return output.getvalue()

def merge_pdfs(header, main, footer, background=None):
    merged = fitz.open()
    if header:
        head_doc = fitz.open(stream=header.read(), filetype="pdf")
        for p in head_doc:
            merged.insert_pdf(head_doc, from_page=p.number, to_page=p.number)
        head_doc.close()
    main_data = main.read()
    if background:
        bg_data = background.read()
        main_data = overlay_with_background(main_data, bg_data)
    main_doc = fitz.open(stream=main_data, filetype="pdf")
    merged.insert_pdf(main_doc)
    main_doc.close()
    if footer:
        foot_doc = fitz.open(stream=footer.read(), filetype="pdf")
        for p in foot_doc:
            merged.insert_pdf(foot_doc, from_page=p.number, to_page=p.number)
        foot_doc.close()
    output = BytesIO()
    merged.save(output)
    merged.close()
    output.seek(0)
    return output

# Generate PDF button
if st.button("Generate Final PDF"):
    if not quotation_pdf:
        st.markdown("<p class='blue-error'>⚠️ Please upload at least the Quotation PDF.</p>", unsafe_allow_html=True)
    elif not all([
        check_size(header_pdf),
        check_size(quotation_pdf),
        check_size(background_pdf),
        check_size(footer_pdf)
    ]):
        st.error("One or more files exceed the 200MB size limit.")
    else:
        try:
            final_pdf = merge_pdfs(header_pdf, quotation_pdf, footer_pdf, background_pdf)
            st.markdown("<p class='dark-blue-success'>✅ PDF merged successfully!</p>", unsafe_allow_html=True)
            st.download_button(
                label="⬇️ Download Final PDF",
                data=final_pdf.getvalue(),
                file_name="final_with_background.pdf",
                mime="application/pdf",
            )
        except Exception as e:
            st.error(f"❌ Error while merging PDFs: {e}")
