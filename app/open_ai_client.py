from openai import OpenAI
from pydantic import BaseModel

client = OpenAI()

# Define output schema
class PdfExtraction(BaseModel):
    patients_eligible_for_coverage: str
    conditions_for_reimbursement: str

def extract_pdf_content(pdf_url, pdf_config):
    # Map headings to output fields dynamically
    heading_to_field = {
        pdf_config["extract_rules"][0]["heading"]: "patients_eligible_for_coverage",
        pdf_config["extract_rules"][1]["heading"]: "conditions_for_reimbursement"
    }

    headings_list = [rule["heading"] for rule in pdf_config["extract_rules"]]
    headings_text = ", ".join([f"'{h}'" for h in headings_list])

    system_message = f"Extract the sections {headings_text} from the given PDF and return them in a structured JSON format."
    user_message = f"Please extract the content of the sections {headings_text} from this PDF: {pdf_url}"

    response = client.responses.parse(
        model="gpt-4o-2024-08-06",
        input=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message},
        ],
        text_format=PdfExtraction,
    )

    return response.output_parsed

