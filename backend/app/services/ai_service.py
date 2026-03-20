import json
import logging
import httpx
from ..core.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


class SiliconFlowService:
    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {settings.siliconflow_api_key}",
            "Content-Type": "application/json",
        }

    async def _chat(self, prompt: str) -> str:
        payload = {
            "model": settings.siliconflow_model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": settings.siliconflow_temperature,
            "max_tokens": settings.siliconflow_max_tokens,
        }
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                f"{settings.siliconflow_base_url}/chat/completions",
                headers=self.headers,
                json=payload,
            )
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"]

    async def parse_daily_report(self, content: str) -> dict:
        """Parse daily report content, extract tasks/status/issues."""
        prompt = f"""请解析以下日报内容，提取关键信息，以JSON格式返回。

日报内容：
{content}

请返回如下JSON格式（只返回JSON，不要其他文字）：
{{
  "completed_tasks": ["已完成的任务1", "已完成的任务2"],
  "in_progress_tasks": ["进行中的任务1"],
  "issues": ["遇到的问题1"],
  "risk_keywords": ["风险关键词"],
  "summary": "一句话总结"
}}"""
        try:
            result = await self._chat(prompt)
            # Extract JSON from response
            start = result.find("{")
            end = result.rfind("}") + 1
            if start >= 0 and end > start:
                return json.loads(result[start:end])
        except Exception as e:
            logger.error(f"AI parse failed: {e}")
        return {"completed_tasks": [], "in_progress_tasks": [], "issues": [], "risk_keywords": [], "summary": ""}

    async def match_tasks(self, parsed_data: dict, task_names: list[str]) -> list[dict]:
        """Match parsed report data to existing project tasks."""
        if not task_names:
            return []

        all_mentioned = parsed_data.get("completed_tasks", []) + parsed_data.get("in_progress_tasks", [])
        if not all_mentioned:
            return []

        prompt = f"""请将以下日报中提到的工作内容与项目任务列表进行匹配。

日报提到的工作：
{json.dumps(all_mentioned, ensure_ascii=False)}

项目任务列表：
{json.dumps(task_names, ensure_ascii=False)}

请返回JSON数组（只返回JSON，不要其他文字）：
[
  {{
    "task_name": "匹配到的任务名称",
    "status": "completed或in_progress",
    "confidence": 0.9
  }}
]"""
        try:
            result = await self._chat(prompt)
            start = result.find("[")
            end = result.rfind("]") + 1
            if start >= 0 and end > start:
                return json.loads(result[start:end])
        except Exception as e:
            logger.error(f"AI task match failed: {e}")
        return []

    async def answer_question(self, question: str, context: str) -> str:
        """Answer a question based on project context."""
        prompt = f"""基于以下项目信息回答问题。

项目信息：
{context}

问题：{question}

请简洁地回答："""
        try:
            return await self._chat(prompt)
        except Exception as e:
            logger.error(f"AI QA failed: {e}")
            return "抱歉，暂时无法回答该问题。"
