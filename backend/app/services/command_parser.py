import re
from dataclasses import dataclass, field
from typing import Optional


COMMAND_PATTERNS = {
    "daily_report": r"【日报】",
    "weekly_report": r"【周报】",
    "progress": r"【进度】",
    "history": r"【历史】",
    "statistics": r"【统计】",
    "reminder_config": r"【提醒设置】",
    "meeting": r"【会议】",
    "qa": r"【问答】",
    "help": r"【帮助】",
    "init": r"【初始化】",
}


@dataclass
class ParsedCommand:
    command: str
    content: str = ""
    target_user: Optional[str] = None
    date_str: Optional[str] = None
    extra: dict = field(default_factory=dict)


def parse_command(text: str) -> Optional[ParsedCommand]:
    """Parse feishu message text into a structured command."""
    # Remove @bot mention prefix
    text = re.sub(r"@\S+\s*", "", text, count=1).strip()

    for cmd_name, pattern in COMMAND_PATTERNS.items():
        match = re.search(pattern, text)
        if not match:
            continue

        # Content after the command keyword
        content = text[match.end():].strip()

        # Extract @user mention
        user_match = re.search(r"@(\S+)", content)
        target_user = user_match.group(1) if user_match else None

        # Extract date (YYYY-MM-DD)
        date_match = re.search(r"\d{4}-\d{2}-\d{2}", content)
        date_str = date_match.group(0) if date_match else None

        # Extract time range keywords
        extra = {}
        if "最近" in content:
            days_match = re.search(r"最近(\d+)天", content)
            if days_match:
                extra["days"] = int(days_match.group(1))
        if "本月" in content:
            extra["period"] = "month"
        if "本周" in content:
            extra["period"] = "week"

        return ParsedCommand(
            command=cmd_name,
            content=content,
            target_user=target_user,
            date_str=date_str,
            extra=extra,
        )

    return None
