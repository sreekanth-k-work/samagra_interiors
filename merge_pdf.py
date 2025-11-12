import streamlit as st
import fitz  # PyMuPDF
from io import BytesIO

st.set_page_config(page_title="Samagra Interiors - PDF Merger", page_icon="📄", layout="centered")

st.title("📄 Samagra Interiors - PDF Merger Tool")
st.caption("Merge Header, Quotation, Template Background, and Footer PDFs into one final file.")

# ------------------- File Uploads -------------------
header_pdf = st.file_uploader("Upload Header PDF (optional)", type="pdf")
quotation_pdf = st.file_uploader("Upload Quotation PDF (required)", type="pdf")
background_pdf = st.file_uploader("Upload Background Template (optional)", type="pdf")
footer_pdf = st.file_uploader("Upload Footer PDF (optional)", type="pdf")

# ------------------- Merge Function -------------------
def overlay_with_background(main_pdf_bytes, background_pdf_bytes):
    """
    Overlays each page of main_pdf on top of the background PDF page.
    Uses PyMuPDF (fitz) for compositing.
    """
    main_doc = fitz.open(stream=main_pdf_bytes, filetype="pdf")
    bg_doc = fitz.open(stream=background_pdf_bytes, filetype="pdf")
    result = fitz.open()

    for page_index in range(len(main_doc)):
        # create a new A4 page
        new_page = result.new_page(width=595.28, height=841.89)
        new_page.show_pdf_page(new_page.rect, bg_doc, 0)  # background first
        new_page.show_pdf_page(new_page.rect, main_doc, page_index)  # then main content
    output = BytesIO()
    result.save(output)
    result.close()
    return output.getvalue()

def merge_pdfs(header, main, footer, background=None):
    """
    Combines header, main, footer into one PDF.
    Optionally applies a background overlay using fitz.
    """
    merged = fitz.open()

    # Header pages
    if header:
        head_doc = fitz.open(stream=header.read(), filetype="pdf")
        for p in head_doc:
            merged.insert_pdf(head_doc, from_page=p.number, to_page=p.number)
        head_doc.close()

    # Main pages (apply background if available)
    main_data = main.read()
    if background:
        bg_data = background.read()
        main_data = overlay_with_background(main_data, bg_data)
    main_doc = fitz.open(stream=main_data, filetype="pdf")
    merged.insert_pdf(main_doc)
    main_doc.close()

    # Footer pages
    if footer:
        foot_doc = fitz.open(stream=footer.read(), filetype="pdf")
        for p in foot_doc:
            merged.insert_pdf(foot_doc, from_page=p.number, to_page=p.number)
        foot_doc.close()

    # Output final file
    output = BytesIO()
    merged.save(output)
    merged.close()
    output.seek(0)
    return output

# ------------------- Run Merge -------------------
if st.button("✨ Generate Final PDF"):
    if not quotation_pdf:
        st.error("Please upload at least the Quotation PDF.")
    else:
        try:
            final_pdf = merge_pdfs(header_pdf, quotation_pdf, footer_pdf, background_pdf)
            st.success("✅ PDF merged successfully!")
            st.download_button(
                label="⬇️ Download Final PDF",
                data=final_pdf.getvalue(),
                file_name="final_with_background.pdf",
                mime="application/pdf",
            )
        except Exception as e:
            st.error(f"❌ Error while merging PDFs: {e}")