import json
import os
from datetime import datetime, timedelta
from pathlib import Path

import gspread
import requests
from dotenv import load_dotenv

DATE_FORMATS = ["%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"]


def load_templates(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def parse_date(value: str) -> datetime | None:
    value = value.strip()
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    return None


def build_message(template: str, name: str, event_date: str) -> str:
    return (
        template.replace("{{name}}", name)
        .replace("{{event_date}}", event_date)
    )


def send_whatsapp_message(
    base_url: str,
    token: str,
    sender_id: str,
    phone: str,
    message: str,
    dry_run: bool,
) -> None:
    if dry_run:
        print(f"[DRY RUN] To: {phone} | Message: {message}")
        return

    url = f"{base_url.rstrip('/')}/messages"
    payload = {
        "to": phone,
        "from": sender_id,
        "type": "text",
        "text": {"body": message},
    }
    response = requests.post(
        url,
        headers={"Authorization": f"Bearer {token}"},
        json=payload,
        timeout=30,
    )
    response.raise_for_status()


def main() -> None:
    load_dotenv()

    sheet_id = os.getenv("GOOGLE_SHEET_ID")
    sheet_tab = os.getenv("GOOGLE_SHEET_TAB", "Sheet1")
    service_account_json = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")

    base_url = os.getenv("WHATSAPP_API_BASE_URL")
    token = os.getenv("WHATSAPP_API_TOKEN")
    sender_id = os.getenv("WHATSAPP_SENDER_ID")

    reminder_days = int(os.getenv("REMINDER_DAYS_BEFORE", "1"))
    dry_run = os.getenv("DRY_RUN", "false").lower() in {"1", "true", "yes"}

    col_name = os.getenv("COL_NAME", "الاسم")
    col_phone = os.getenv("COL_PHONE", "رقم الواتساب")
    col_event_date = os.getenv("COL_EVENT_DATE", "تاريخ الإيفنت")
    col_status = os.getenv("COL_STATUS", "الحالة")
    col_sent = os.getenv("COL_SENT", "تم الإرسال؟")
    col_template = os.getenv("COL_TEMPLATE", "قالب الرسالة")

    if not all([sheet_id, service_account_json, base_url, token, sender_id]):
        raise ValueError("Missing required environment variables.")

    templates = load_templates(Path(__file__).parent / "templates.json")

    client = gspread.service_account(filename=service_account_json)
    worksheet = client.open_by_key(sheet_id).worksheet(sheet_tab)
    headers = worksheet.row_values(1)
    header_map = {header: idx + 1 for idx, header in enumerate(headers)}

    if col_sent not in header_map:
        raise ValueError(f"Missing column '{col_sent}' in sheet headers.")

    records = worksheet.get_all_records()

    target_date = (datetime.today() + timedelta(days=reminder_days)).date()

    updated_rows = 0

    for idx, row in enumerate(records, start=2):
        name = str(row.get(col_name, "")).strip()
        phone = str(row.get(col_phone, "")).strip()
        event_date_raw = str(row.get(col_event_date, "")).strip()
        status = str(row.get(col_status, "")).strip().lower()
        sent_flag = str(row.get(col_sent, "")).strip().lower()
        template_key = str(row.get(col_template, "Template_A")).strip()

        if not name or not phone or not event_date_raw:
            continue
        if sent_flag in {"yes", "true", "تم", "sent"}:
            continue
        if status and status not in {"confirmed", "مؤكد"}:
            continue

        parsed_date = parse_date(event_date_raw)
        if not parsed_date:
            continue

        if parsed_date.date() != target_date:
            continue

        template = templates.get(template_key, templates.get("Template_A", ""))
        message = build_message(template, name, parsed_date.strftime("%Y-%m-%d"))

        send_whatsapp_message(base_url, token, sender_id, phone, message, dry_run)
        if not dry_run:
            worksheet.update_cell(idx, header_map[col_sent], "Yes")
        updated_rows += 1

    print(f"Sent {updated_rows} reminders.")


if __name__ == "__main__":
    main()
