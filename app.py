import os
from datetime import date

import requests
import streamlit as st
from dotenv import load_dotenv

from utils.exporters import format_docx, format_pdf, format_txt, get_download_name
from utils.text_utils import format_html_preview

load_dotenv()

APP_NAME = os.getenv("APP_NAME", "LegalEase")
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")

st.set_page_config(
    page_title=APP_NAME,
    page_icon="⚖️",
    layout="wide",
)

st.markdown(
    """
    <style>
    .main-title {
        text-align: center;
        font-size: 2.4rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }
    .subtitle {
        text-align: center;
        color: #9aa4b2;
        margin-bottom: 2rem;
    }
    .preview-card {
        background: #111827;
        border: 1px solid #263244;
        border-radius: 12px;
        padding: 24px;
        max-height: 650px;
        overflow-y: auto;
        color: #f3f4f6;
        line-height: 1.7;
    }
    .notice {
        padding: 12px 16px;
        border-radius: 8px;
        background: #172033;
        border: 1px solid #334155;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(f'<div class="main-title">⚖️ {APP_NAME}</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">AI-powered legal document draft generator</div>',
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("Document Details")

    document_type = st.text_input(
        "Document Type",
        value="Non-Disclosure Agreement",
        help="Example: NDA, Lease Agreement, Employment Contract.",
    )

    parties = st.text_area(
        "Parties Involved",
        value="Alice Smith (Disclosing Party), ABC Ltd (Receiving Party)",
        height=120,
    )

    terms = st.text_area(
        "Terms & Conditions",
        value=(
            "Confidential information must be protected; "
            "Confidentiality applies for 2 years; "
            "Either party may terminate with 15 days notice"
        ),
        height=180,
        help="Separate clauses with semicolons.",
    )

    effective_date = st.date_input(
        "Effective Date",
        value=date.today(),
    )

    generate = st.button(
        "Generate Document",
        type="primary",
        use_container_width=True,
    )

if "document_text" not in st.session_state:
    st.session_state.document_text = ""

if "document_type" not in st.session_state:
    st.session_state.document_type = document_type

if generate:
    if not all(
        value.strip()
        for value in [document_type, parties, terms, str(effective_date)]
    ):
        st.error("Please complete all fields.")
    else:
        payload = {
            "document_type": document_type,
            "parties": parties,
            "terms": terms,
            "dates": effective_date.strftime("%B %d, %Y"),
        }

        with st.spinner("Generating document..."):
            try:
                response = requests.post(
                    f"{API_BASE_URL}/generate",
                    json=payload,
                    timeout=120,
                )
                response.raise_for_status()
                result = response.json()

                st.session_state.document_text = result["content"]
                st.session_state.document_type = result["document_type"]

                if result.get("demo_mode"):
                    st.info(
                        "Demo mode is active because GEMINI_API_KEY is not configured. "
                        "Add a Gemini key to .env for AI generation."
                    )
                else:
                    st.success("Document generated successfully.")
            except requests.exceptions.ConnectionError:
                st.error(
                    "Could not connect to FastAPI. Start the backend with: "
                    "uvicorn backend.main:app --reload"
                )
            except requests.exceptions.RequestException as exc:
                st.error(f"Backend request failed: {exc}")
            except Exception as exc:
                st.error(f"Unexpected error: {exc}")

st.subheader("Document Preview")

if st.session_state.document_text:
    tab_preview, tab_edit = st.tabs(["Preview", "Edit Document"])

    with tab_preview:
        html = format_html_preview(st.session_state.document_text)
        st.markdown(
            f'<div class="preview-card">{html}</div>',
            unsafe_allow_html=True,
        )

    with tab_edit:
        edited = st.text_area(
            "Edit the generated document",
            value=st.session_state.document_text,
            height=600,
            key="editor",
        )
        st.session_state.document_text = edited

    st.subheader("Download")

    text_bytes = format_txt(st.session_state.document_text)
    docx_bytes = format_docx(
        st.session_state.document_text,
        st.session_state.document_type,
    )
    pdf_bytes = format_pdf(
        st.session_state.document_text,
        st.session_state.document_type,
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.download_button(
            "Download TXT",
            data=text_bytes,
            file_name=get_download_name(st.session_state.document_type, "txt"),
            mime="text/plain",
            use_container_width=True,
        )

    with col2:
        st.download_button(
            "Download DOCX",
            data=docx_bytes,
            file_name=get_download_name(st.session_state.document_type, "docx"),
            mime=(
                "application/vnd.openxmlformats-officedocument."
                "wordprocessingml.document"
            ),
            use_container_width=True,
        )

    with col3:
        st.download_button(
            "Download PDF",
            data=pdf_bytes,
            file_name=get_download_name(st.session_state.document_type, "pdf"),
            mime="application/pdf",
            use_container_width=True,
        )
else:
    st.markdown(
        '<div class="notice">Enter the document details in the sidebar and click '
        '<b>Generate Document</b>.</div>',
        unsafe_allow_html=True,
    )

st.divider()
st.caption(
    "LegalEase produces drafts for review. Consult a qualified legal professional "
    "before signing or relying on a document."
)
