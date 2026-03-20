import logging
from fastapi import APIRouter, Request, HTTPException
from ..services.feishu_service import verify_signature, decrypt_event, send_card, send_text
from ..services.command_parser import parse_command
from ..core.config import get_settings
from ..core.database import AsyncSessionLocal
from ..models import Project
from sqlalchemy import select

router = APIRouter()
settings = get_settings()
logger = logging.getLogger(__name__)


@router.post("/callback")
async def feishu_callback(request: Request):
    body = await request.body()
    data = await request.json()

    # Decrypt if encrypted (challenge may also be encrypted)
    if "encrypt" in data:
        data = decrypt_event(data["encrypt"])

    # URL verification challenge
    if "challenge" in data:
        return {"challenge": data["challenge"]}

    header = data.get("header", {})
    event_type = header.get("event_type", "")
    event = data.get("event", {})

    if event_type == "im.message.receive_v1":
        await handle_message(event)

    return {"code": 0}


async def handle_message(event: dict):
    msg = event.get("message", {})
    sender = event.get("sender", {})

    if msg.get("message_type") != "text":
        return

    import json
    content = json.loads(msg.get("content", "{}")).get("text", "")
    chat_id = msg.get("chat_id", "")
    message_id = msg.get("message_id", "")
    user_id = sender.get("sender_id", {}).get("user_id", "")
    user_name = sender.get("sender_id", {}).get("user_id", "unknown")

    # Only respond to @mentions
    mentions = msg.get("mentions", [])
    if not mentions:
        return

    cmd = parse_command(content)
    if not cmd:
        return

    async with AsyncSessionLocal() as db:
        # Find project by chat_id
        result = await db.execute(select(Project).where(Project.group_id == chat_id))
        project = result.scalar_one_or_none()

        if cmd.command == "help":
            from ..utils.card_builder import build_help_card
            await send_card(chat_id, build_help_card())
            return

        if cmd.command == "init":
            if project:
                await send_text(chat_id, "项目已初始化，请勿重复操作。")
            else:
                new_project = Project(name="新项目", group_id=chat_id)
                db.add(new_project)
                await db.commit()
                await send_text(chat_id, "✅ 项目初始化成功！请前往 Web 管理界面完善项目信息。")
            return

        if not project:
            await send_text(chat_id, "当前群未关联项目，请先发送【初始化】命令。")
            return

        if cmd.command == "daily_report":
            from ..services.report_service import submit_daily_report
            from ..utils.card_builder import build_report_confirm_card
            result = await submit_daily_report(
                db, project.id, user_id, user_name, cmd.content, message_id
            )
            card = build_report_confirm_card(user_name, result.get("parsed_data", {}))
            await send_card(chat_id, card)

        elif cmd.command == "progress":
            from ..services.progress_service import get_project_progress
            from ..utils.card_builder import build_progress_card
            data = await get_project_progress(db, project.id, cmd.content or None)
            card = build_progress_card(project.name, data)
            await send_card(chat_id, card)

        elif cmd.command == "weekly_report":
            from ..services.weekly_report_service import generate_weekly_report
            from ..utils.card_builder import build_weekly_report_card
            data = await generate_weekly_report(db, project.id, cmd.target_user)
            card = build_weekly_report_card(project.name, data)
            await send_card(chat_id, card)

        elif cmd.command == "history":
            from ..services.report_service import get_reports
            data = await get_reports(
                db, project.id,
                user_name=cmd.target_user,
                date_str=cmd.date_str,
                days=cmd.extra.get("days"),
            )
            text = f"📋 查询到 {data['total']} 条记录\n"
            for item in data["items"][:5]:
                text += f"\n[{item['submit_time'][:10]}] {item['user_name']}: {item['content'][:80]}..."
            await send_text(chat_id, text)

        elif cmd.command == "statistics":
            from ..services.statistics_service import get_statistics
            from ..utils.card_builder import build_progress_card
            period = cmd.extra.get("period", "week")
            data = await get_statistics(db, project.id, period)
            text = (
                f"📊 项目统计（{period}）\n"
                f"总任务：{data['total_tasks']} | 已完成：{data['completed_tasks']} | 完成率：{data['completion_rate']}%\n"
                f"成员活跃度：" + ", ".join(f"{m['user_name']}({m['report_count']})" for m in data["member_activity"][:5])
            )
            await send_text(chat_id, text)
