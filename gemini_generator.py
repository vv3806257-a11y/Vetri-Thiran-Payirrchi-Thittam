import os
from typing import Tuple

from dotenv import load_dotenv

load_dotenv()


class GeminiDocumentGenerator:
    """Generate structured legal-document drafts through Google's GenAI SDK."""

    def __init__(self) -> None:
        self.api_key = os.getenv("GEMINI_API_KEY", "").strip()
        self.model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()
        self.require_gemini = (
            os.getenv("REQUIRE_GEMINI", "false").strip().lower() == "true"
        )

    def generate_document(
        self,
        document_type: str,
        parties: str,
        terms: str,
        dates: str,
    ) -> Tuple[str, bool]:
        if not self.api_key:
            if self.require_gemini:
                raise RuntimeError(
                    "GEMINI_API_KEY is not configured. Add it to your .env file."
                )
            return self._demo_document(document_type, parties, terms, dates), True

        try:
            from google import genai
            from google.genai import types
        except ImportError as exc:
            raise RuntimeError(
                "The google-genai package is missing. Run: pip install -r requirements.txt"
            ) from exc

        client = genai.Client(api_key=self.api_key)

        prompt = self._build_prompt(
            document_type=document_type,
            parties=parties,
            terms=terms,
            dates=dates,
        )

        response = client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.25,
                max_output_tokens=6000,
            ),
        )

        text = getattr(response, "text", None)
        if not text or not text.strip():
            raise RuntimeError("Gemini returned an empty response.")

        return text.strip(), False

    @staticmethod
    def _build_prompt(
        document_type: str,
        parties: str,
        terms: str,
        dates: str,
    ) -> str:
        return f"""
You are a legal-document drafting assistant.

Create a professional LEGAL DOCUMENT DRAFT based only on the user-provided facts.
Do not invent names, addresses, monetary values, dates, laws, jurisdictions, or obligations.

Document type:
{document_type}

Parties:
{parties}

Effective date:
{dates}

Terms and conditions:
{terms}

Requirements:
1. Use a clear formal title.
2. Identify the parties and effective date.
3. Organize the document with numbered headings.
4. Include the supplied terms as appropriate clauses.
5. Add standard boilerplate only when it is generic and does not invent factual details.
6. If an important fact is missing, use a bracketed placeholder such as [JURISDICTION].
7. End with signature blocks for the relevant parties.
8. Keep the wording editable and professional.
9. Do not claim that the document is legally valid in a particular jurisdiction.
10. Add this final note: "Draft for review — consult a qualified legal professional before signing or relying on this document."

Return plain text only. Do not use Markdown tables.
""".strip()

    @staticmethod
    def _demo_document(
        document_type: str,
        parties: str,
        terms: str,
        dates: str,
    ) -> str:
        clauses = [
            item.strip()
            for item in terms.replace("\n", ";").split(";")
            if item.strip()
        ]

        terms_block = "\n".join(
            f"{index}. {clause}" for index, clause in enumerate(clauses, start=1)
        )

        return f"""DRAFT {document_type.upper()}

EFFECTIVE DATE
{dates}

PARTIES
{parties}

1. PURPOSE
This draft records the principal understanding between the parties identified above
for the purpose described by the document type.

2. TERMS AND CONDITIONS
{terms_block or "1. [Insert agreed terms.]"}

3. GENERAL PROVISIONS
The parties should review applicable definitions, responsibilities, confidentiality,
termination, dispute resolution, governing law, notices, and other provisions before
signing.

4. SIGNATURES

Party 1: ______________________________
Name: __________________________________
Date: ___________________________________

Party 2: ______________________________
Name: __________________________________
Date: ___________________________________

Draft for review — consult a qualified legal professional before signing or relying
on this document.
"""
