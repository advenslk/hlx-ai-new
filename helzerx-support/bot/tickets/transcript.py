"""
HELZERX AI Support - Transcript Generator
Generates enterprise-grade HTML and plaintext transcripts for ticket archives.
"""
from __future__ import annotations

import html
import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

TRANSCRIPTS_DIR = Path(__file__).resolve().parent.parent.parent / "transcripts"
TRANSCRIPTS_DIR.mkdir(parents=True, exist_ok=True)


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>HELZERX Support Transcript - {ticket_code}</title>
  <style>
    body {{
      background-color: #0b0f19;
      color: #e2e8f0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      margin: 0;
      padding: 32px 16px;
      display: flex;
      justify-content: center;
    }}
    .container {{
      max-width: 860px;
      width: 100%;
      background: #111827;
      border: 1px solid #1f2937;
      border-radius: 12px;
      overflow: hidden;
      box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5);
    }}
    .header {{
      background: #1e293b;
      padding: 24px;
      border-bottom: 1px solid #334155;
    }}
    .header h1 {{
      margin: 0 0 8px 0;
      font-size: 22px;
      color: #f8fafc;
      display: flex;
      align-items: center;
      gap: 12px;
    }}
    .badge {{
      display: inline-block;
      font-size: 11px;
      font-weight: 600;
      padding: 2px 8px;
      border-radius: 4px;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }}
    .badge-open {{ background: #065f46; color: #34d399; }}
    .badge-closed {{ background: #374151; color: #9ca3af; }}
    .meta-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 12px;
      margin-top: 16px;
      font-size: 13px;
      color: #94a3b8;
    }}
    .meta-item strong {{ color: #cbd5e1; }}
    .messages {{
      padding: 24px;
      display: flex;
      flex-direction: column;
      gap: 16px;
    }}
    .message {{
      display: flex;
      gap: 14px;
      padding: 12px 16px;
      border-radius: 8px;
      background: #172033;
      border-left: 3px solid transparent;
    }}
    .msg-ai {{ border-left-color: #5865f2; }}
    .msg-staff {{ border-left-color: #10b981; }}
    .msg-customer {{ border-left-color: #64748b; }}
    .avatar {{
      width: 38px;
      height: 38px;
      border-radius: 50%;
      background: #334155;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: bold;
      font-size: 14px;
      flex-shrink: 0;
    }}
    .msg-content {{ flex-grow: 1; }}
    .msg-top {{
      display: flex;
      align-items: center;
      gap: 8px;
      margin-bottom: 4px;
    }}
    .author-name {{ font-weight: 600; font-size: 14px; color: #f1f5f9; }}
    .author-badge {{
      font-size: 10px;
      font-weight: bold;
      padding: 1px 6px;
      border-radius: 4px;
    }}
    .badge-ai {{ background: #5865f2; color: #fff; }}
    .badge-staff {{ background: #10b981; color: #fff; }}
    .badge-user {{ background: #475569; color: #cbd5e1; }}
    .msg-time {{ font-size: 11px; color: #64748b; margin-left: auto; }}
    .msg-body {{ font-size: 14px; line-height: 1.5; color: #e2e8f0; white-space: pre-wrap; }}
    .footer {{
      padding: 16px 24px;
      background: #0f172a;
      border-top: 1px solid #1e293b;
      font-size: 12px;
      color: #64748b;
      text-align: center;
    }}
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>HELZERX Support Transcript: {ticket_code} <span class="badge {status_class}">{status}</span></h1>
      <div class="meta-grid">
        <div class="meta-item"><strong>Customer:</strong> {customer_name}</div>
        <div class="meta-item"><strong>Category:</strong> {category}</div>
        <div class="meta-item"><strong>Priority:</strong> {priority}</div>
        <div class="meta-item"><strong>Closed At:</strong> {closed_at}</div>
      </div>
    </div>
    <div class="messages">
      {messages_html}
    </div>
    <div class="footer">
      Generated automatically by HELZERX AI Support Engine • Confidential Transcript
    </div>
  </div>
</body>
</html>
"""


def generate_html_transcript(
    ticket_code: str,
    customer_name: str,
    category: str,
    priority: str,
    status: str,
    messages: List[Dict[str, Any]],
    closed_at: Optional[str] = None
) -> Tuple[str, Path]:
    """
    Renders an HTML transcript and writes it to disk.
    Returns:
        (html_content: str, file_path: Path)
    """
    closed_time_str = closed_at or datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    rendered_msgs = []
    for m in messages:
        role = m.get("author_role", "customer").lower()
        name = html.escape(m.get("author_name", "User"))
        content = html.escape(m.get("content", ""))
        time_str = m.get("created_at", "")
        if isinstance(time_str, datetime.datetime):
            time_str = time_str.strftime("%H:%M:%S UTC")

        initials = name[:2].upper()
        if role == "ai":
            cls = "msg-ai"
            badge = '<span class="author-badge badge-ai">HELZERX AI</span>'
        elif role == "staff":
            cls = "msg-staff"
            badge = '<span class="author-badge badge-staff">SUPPORT STAFF</span>'
        else:
            cls = "msg-customer"
            badge = '<span class="author-badge badge-user">CUSTOMER</span>'

        rendered_msgs.append(f"""
        <div class="message {cls}">
          <div class="avatar">{initials}</div>
          <div class="msg-content">
            <div class="msg-top">
              <span class="author-name">{name}</span>
              {badge}
              <span class="msg-time">{time_str}</span>
            </div>
            <div class="msg-body">{content}</div>
          </div>
        </div>
        """)

    final_html = HTML_TEMPLATE.format(
        ticket_code=html.escape(ticket_code),
        status_class="badge-closed" if status.upper() == "CLOSED" else "badge-open",
        status=html.escape(status),
        customer_name=html.escape(customer_name),
        category=html.escape(category),
        priority=html.escape(priority),
        closed_at=html.escape(closed_time_str),
        messages_html="".join(rendered_msgs)
    )

    file_name = f"transcript_{ticket_code}_{datetime.datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.html"
    file_path = TRANSCRIPTS_DIR / file_name
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(final_html)

    return final_html, file_path
