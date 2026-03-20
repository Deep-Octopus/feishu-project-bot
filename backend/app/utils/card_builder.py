from datetime import datetime


def build_report_confirm_card(user_name: str, parsed_data: dict) -> dict:
    summary = parsed_data.get("summary", "已记录")
    completed = parsed_data.get("completed_tasks", [])
    issues = parsed_data.get("issues", [])

    elements = [
        {"tag": "div", "text": {"tag": "lark_md", "content": f"**提交人：** {user_name}"}},
        {"tag": "div", "text": {"tag": "lark_md", "content": f"**提交时间：** {datetime.now().strftime('%Y-%m-%d %H:%M')}"}},
        {"tag": "div", "text": {"tag": "lark_md", "content": f"**AI摘要：** {summary}"}},
    ]
    if completed:
        elements.append({"tag": "div", "text": {"tag": "lark_md", "content": f"**完成任务：** {', '.join(completed[:3])}"}})
    if issues:
        elements.append({"tag": "div", "text": {"tag": "lark_md", "content": f"**遇到问题：** {', '.join(issues[:2])}"}})

    elements.append({"tag": "action", "actions": [
        {"tag": "button", "text": {"tag": "plain_text", "content": "查看进度"}, "type": "primary", "value": {"action": "view_progress"}},
        {"tag": "button", "text": {"tag": "plain_text", "content": "查看历史"}, "type": "default", "value": {"action": "view_history"}},
    ]})

    return {
        "config": {"wide_screen_mode": True},
        "header": {"title": {"tag": "plain_text", "content": "✅ 日报已记录"}, "template": "green"},
        "elements": elements,
    }


def build_progress_card(project_name: str, progress_data: dict) -> dict:
    overall = progress_data.get("overall_progress", 0)
    tasks = progress_data.get("tasks", [])
    risk_count = progress_data.get("risk_count", 0)

    elements = [
        {"tag": "div", "text": {"tag": "lark_md", "content": f"**整体完成度：** {overall}%"}},
        {"tag": "div", "text": {"tag": "lark_md", "content": f"**风险任务：** {risk_count} 项"}},
        {"tag": "hr"},
    ]

    for task in tasks[:8]:
        status_icon = "✅" if task["status"] == "completed" else ("⚠️" if task["risk_flag"] else "🔄")
        elements.append({
            "tag": "div",
            "text": {"tag": "lark_md", "content": f"{status_icon} **{task['name']}** - {task['progress']}% ({task.get('assignee', '未指定')})"},
        })

    return {
        "config": {"wide_screen_mode": True},
        "header": {"title": {"tag": "plain_text", "content": f"📊 {project_name} 项目进度"}, "template": "blue"},
        "elements": elements,
    }


def build_weekly_report_card(project_name: str, data: dict) -> dict:
    elements = [
        {"tag": "div", "text": {"tag": "lark_md", "content": f"**时间范围：** {data['week_start']} 至 {data['week_end']}"}},
        {"tag": "div", "text": {"tag": "lark_md", "content": f"**日报提交：** {data['report_count']} 条"}},
        {"tag": "div", "text": {"tag": "lark_md", "content": f"**参与成员：** {', '.join(str(m) for m in data['members'][:5] if m)}"}},
        {"tag": "div", "text": {"tag": "lark_md", "content": f"**完成任务：** {data['completed_tasks']} 项"}},
    ]
    if data.get("issues"):
        issues_text = "\n".join(f"- {i}" for i in data["issues"][:5])
        elements.append({"tag": "div", "text": {"tag": "lark_md", "content": f"**本周问题：**\n{issues_text}"}})

    return {
        "config": {"wide_screen_mode": True},
        "header": {"title": {"tag": "plain_text", "content": f"📋 {project_name} 周报"}, "template": "purple"},
        "elements": elements,
    }


def build_reminder_card(task, project, days_left: int, overdue: bool = False) -> dict:
    if overdue:
        title = f"⏰ 任务逾期提醒"
        content = f"任务「**{task.name}**」已逾期 {abs(days_left)} 天，请及时处理！"
        template = "red"
    else:
        title = f"⏰ 任务截止提醒"
        content = f"任务「**{task.name}**」还有 {days_left} 天截止，请注意进度！"
        template = "yellow"

    return {
        "config": {"wide_screen_mode": False},
        "header": {"title": {"tag": "plain_text", "content": title}, "template": template},
        "elements": [
            {"tag": "div", "text": {"tag": "lark_md", "content": content}},
            {"tag": "div", "text": {"tag": "lark_md", "content": f"**负责人：** {task.assignee or '未指定'}"}},
            {"tag": "div", "text": {"tag": "lark_md", "content": f"**当前进度：** {task.progress}%"}},
        ],
    }


def build_risk_card(project, message: str) -> dict:
    return {
        "config": {"wide_screen_mode": False},
        "header": {"title": {"tag": "plain_text", "content": "⚠️ 项目风险预警"}, "template": "red"},
        "elements": [
            {"tag": "div", "text": {"tag": "lark_md", "content": f"**项目：** {project.name}"}},
            {"tag": "div", "text": {"tag": "lark_md", "content": f"**预警信息：** {message}"}},
        ],
    }


def build_help_card() -> dict:
    commands = [
        ("【日报】", "提交当日工作日报"),
        ("【周报】", "生成本周项目周报"),
        ("【进度】", "查询项目整体进度"),
        ("【历史】", "查询历史日报记录"),
        ("【统计】", "查看项目数据统计"),
        ("【提醒设置】", "配置任务提醒"),
        ("【会议】", "记录会议决议"),
        ("【问答】", "智能问答"),
        ("【初始化】", "初始化项目配置"),
        ("【帮助】", "查看命令列表"),
    ]
    content = "\n".join(f"- `{cmd}` {desc}" for cmd, desc in commands)
    return {
        "config": {"wide_screen_mode": True},
        "header": {"title": {"tag": "plain_text", "content": "🤖 机器人命令列表"}, "template": "blue"},
        "elements": [{"tag": "div", "text": {"tag": "lark_md", "content": content}}],
    }
