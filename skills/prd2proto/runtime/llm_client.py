"""LLM Client for prd2proto pipeline.

封装真实LLM调用，专为pipeline stage execution优化：
1. 异步streaming（支持长输出，避免10分钟超时）
2. JSON输出解析（容错markdown包裹/前后杂字）
3. 凭证适配（ANTHROPIC_AUTH_TOKEN / ANTHROPIC_API_KEY）
4. 配置统一（model/max_tokens/temperature/timeout）

设计原则：
- 单一职责：只做LLM调用，不解析业务语义
- 默认真实：禁止静默mock，mock必须显式启用
- 错误显式：失败抛出异常，不假装成功
- 可测试：支持mock_response注入
"""

from __future__ import annotations

import json
import os
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class LLMResponse:
    """LLM调用返回值。"""

    text: str
    """完整文本响应"""

    input_tokens: int = 0
    output_tokens: int = 0
    elapsed_ms: int = 0
    model: str = ""
    stop_reason: str = ""
    """停止原因：end_turn / max_tokens / stop_sequence / tool_use"""

    was_truncated: bool = False
    """是否因 max_tokens 截断（stop_reason == 'max_tokens'）"""

    continuation_count: int = 0
    """续写次数（原始调用=0，每次续写+1）"""

    raw: dict[str, Any] = field(default_factory=dict)
    """原始响应（用于调试）"""

    def to_dict(self) -> dict[str, Any]:
        return {
            "text": self.text,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "elapsed_ms": self.elapsed_ms,
            "model": self.model,
            "stop_reason": self.stop_reason,
            "was_truncated": self.was_truncated,
            "continuation_count": self.continuation_count,
        }


class LLMClientError(Exception):
    """LLM调用失败"""

    pass


class JSONExtractionError(Exception):
    """从LLM输出中提取JSON失败"""

    pass


class LLMClient:
    """异步Anthropic LLM Client，专为pipeline stage execution设计。"""

    def __init__(
        self,
        model: str = "claude-opus-4-8",
        max_tokens: int = 24576,
        temperature: float = 0.3,
        api_key: str | None = None,
        base_url: str | None = None,
        mock: bool = False,
    ):
        """
        Args:
            model: 模型ID（默认claude-opus-4-8）
            max_tokens: 最大输出tokens（设计推理产出长，需≥16k）
            temperature: 温度（推理类任务0.3较好）
            api_key: API key（默认从env读）
            base_url: API base URL（如需内部代理则指定）
            mock: 是否启用mock模式（必须显式True，默认False = 真实调用）
        """
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.mock = mock

        # 凭证解析（兼容Claude Code的AUTH_TOKEN和官方SDK的API_KEY）
        self._api_key = api_key or self._resolve_api_key()
        self._base_url = base_url or os.getenv("ANTHROPIC_BASE_URL")

    @staticmethod
    def _resolve_api_key() -> str | None:
        """优先AUTH_TOKEN（Claude Code），fallback到API_KEY（官方SDK）"""
        return os.getenv("ANTHROPIC_AUTH_TOKEN") or os.getenv("ANTHROPIC_API_KEY")

    def _ensure_credentials(self) -> None:
        """运行前检查凭证。Mock模式不检查。"""
        if self.mock:
            return
        if not self._api_key:
            raise LLMClientError(
                "未找到 LLM 凭证。请设置 ANTHROPIC_AUTH_TOKEN 或 ANTHROPIC_API_KEY。"
                "（默认运行需要真实 LLM；如需 mock 请显式 mock=True）"
            )

    async def call(
        self,
        prompt: str,
        max_tokens: int | None = None,
    ) -> LLMResponse:
        """异步调用LLM（streaming），返回LLMResponse（含stop_reason）。

        Args:
            prompt: 完整prompt字符串
            max_tokens: 覆盖默认max_tokens

        Returns:
            LLMResponse（包含text/usage/timing/stop_reason）

        Raises:
            LLMClientError: 凭证缺失或API调用失败
        """
        if self.mock:
            return self._mock_response(prompt)

        self._ensure_credentials()

        from anthropic import AsyncAnthropic

        client = AsyncAnthropic(
            api_key=self._api_key,
            base_url=self._base_url,
        )

        effective_max_tokens = max_tokens or self.max_tokens

        # 网络瞬时错误重试（指数退避）。
        # 注意：重试的是网络/连接错误，不是篡改 LLM 输出，不违反"不静默修正"红线。
        import asyncio as _asyncio
        max_retries = 3
        last_exc = None
        for attempt in range(max_retries):
            t0 = time.time()
            full_text = ""
            try:
                async with client.messages.stream(
                    model=self.model,
                    max_tokens=effective_max_tokens,
                    temperature=self.temperature,
                    messages=[{"role": "user", "content": prompt}],
                ) as stream:
                    async for text_chunk in stream.text_stream:
                        full_text += text_chunk
                    final_msg = await stream.get_final_message()
                break  # 成功，跳出重试
            except Exception as exc:
                last_exc = exc
                err_repr = repr(str(exc)) or type(exc).__name__
                if attempt < max_retries - 1:
                    wait = 2 ** attempt * 5  # 5s, 10s
                    print(
                        f"      ⚠️  LLM 调用失败（attempt {attempt+1}/{max_retries}）: "
                        f"{err_repr}，{wait}s 后重试..."
                    )
                    await _asyncio.sleep(wait)
                else:
                    raise LLMClientError(
                        f"LLM API 调用失败（重试{max_retries}次后）: "
                        f"{type(exc).__name__}: {exc}"
                    ) from exc

        elapsed_ms = int((time.time() - t0) * 1000)
        stop_reason = getattr(final_msg, "stop_reason", "") or ""
        was_truncated = stop_reason == "max_tokens"

        return LLMResponse(
            text=full_text,
            input_tokens=final_msg.usage.input_tokens,
            output_tokens=final_msg.usage.output_tokens,
            elapsed_ms=elapsed_ms,
            model=self.model,
            stop_reason=stop_reason,
            was_truncated=was_truncated,
            raw={"usage": dict(final_msg.usage.__dict__)} if hasattr(
                final_msg.usage, "__dict__"
            ) else {},
        )

    async def call_with_continuation(
        self,
        prompt: str,
        max_tokens: int | None = None,
        max_continuations: int = 2,
    ) -> LLMResponse:
        """异步调用LLM，自动检测截断并续写。

        实现策略：
        1. 首次调用 call()
        2. 检测 was_truncated == True
        3. 触发续写：构造continuation prompt，让LLM从截断位置继续输出
        4. 智能拼接：去除续写响应可能的重复前缀
        5. 重复直到完整或达到 max_continuations

        Args:
            prompt: 原始prompt
            max_tokens: 单次调用的max_tokens
            max_continuations: 最多续写次数（默认2，即总共最多调用3次）

        Returns:
            LLMResponse（text是拼接后的完整文本，token/elapsed累计）
        """
        # 首次调用
        response = await self.call(prompt, max_tokens=max_tokens)

        # 未截断直接返回
        if not response.was_truncated:
            return response

        # 截断处理
        full_text = response.text
        total_input = response.input_tokens
        total_output = response.output_tokens
        total_elapsed = response.elapsed_ms
        continuation_count = 0
        last_stop_reason = response.stop_reason

        for attempt in range(max_continuations):
            print(
                f"      ⚠️  Output truncated (stop_reason=max_tokens), "
                f"continuation {attempt + 1}/{max_continuations}..."
            )

            # 构造续写prompt：明确告知LLM从哪里续写
            continuation_prompt = self._build_continuation_prompt(
                original_prompt=prompt,
                partial_output=full_text,
            )

            # 续写调用
            cont_response = await self.call(
                continuation_prompt,
                max_tokens=max_tokens,
            )

            # 智能拼接（去除续写可能的重复前缀）
            merged_text = self._smart_merge_continuation(
                existing=full_text,
                continuation=cont_response.text,
            )
            full_text = merged_text

            # 累计指标
            total_input += cont_response.input_tokens
            total_output += cont_response.output_tokens
            total_elapsed += cont_response.elapsed_ms
            continuation_count += 1
            last_stop_reason = cont_response.stop_reason

            # 续写结果未截断 = 成功
            if not cont_response.was_truncated:
                print(f"      ✅ Continuation completed (total {continuation_count} calls)")
                break
        else:
            print(
                f"      ⚠️  Still truncated after {max_continuations} continuations. "
                f"Output may be incomplete."
            )

        return LLMResponse(
            text=full_text,
            input_tokens=total_input,
            output_tokens=total_output,
            elapsed_ms=total_elapsed,
            model=self.model,
            stop_reason=last_stop_reason,
            was_truncated=(last_stop_reason == "max_tokens"),
            continuation_count=continuation_count,
        )

    @staticmethod
    def _build_continuation_prompt(
        original_prompt: str,
        partial_output: str,
    ) -> str:
        """构造续写prompt，让LLM从截断位置继续输出。

        关键：不要让LLM重新开始整个JSON，而是从截断字符开始续写。
        """
        # 取已输出的最后200字符作为定位锚点
        anchor = partial_output[-200:]

        return (
            original_prompt
            + "\n\n---\n\n"
            + "# 你之前的部分输出（被max_tokens截断在此）\n\n"
            + "```\n"
            + partial_output
            + "\n```\n\n"
            + "# 续写指令\n\n"
            + "你之前的输出**被max_tokens截断**，现在请你**继续输出剩余部分**。\n\n"
            + "**严格规则**:\n"
            + "1. ❌ 不要重复任何已输出的内容\n"
            + "2. ❌ 不要重新开始整个JSON\n"
            + "3. ❌ 不要输出任何前言/解释/markdown标记\n"
            + "4. ✅ 直接从截断位置的下一个字符开始续写\n"
            + "5. ✅ 保证最终拼接（已输出 + 你的续写）是完整合法的JSON\n"
            + "6. ✅ 续写应该闭合所有未闭合的字符串/对象/数组\n\n"
            + f"**截断位置参考**（已输出末尾200字）:\n```\n{anchor}\n```\n\n"
            + "请直接续写："
        )

    @staticmethod
    def _smart_merge_continuation(existing: str, continuation: str) -> str:
        """智能拼接已输出和续写部分。

        策略：
        1. 续写如果带markdown代码块包裹，去除
        2. 续写如果意外重复了existing的尾部，检测并去重
        3. 直接拼接
        """
        # 去除续写可能带的markdown包裹
        cont = continuation.strip()
        if cont.startswith("```"):
            # ``` 或 ```json 起始
            first_newline = cont.find("\n")
            if first_newline != -1:
                cont = cont[first_newline + 1:]
        if cont.endswith("```"):
            cont = cont[:-3].rstrip()

        # 检测续写开头是否重复了existing的尾部
        # 取existing的最后50字符，看是否在续写开头出现
        tail = existing[-50:].strip() if len(existing) > 50 else existing.strip()
        if tail and len(tail) > 10:
            # 在续写的前200字符内查找
            search_window = cont[:200]
            idx = search_window.find(tail)
            if idx != -1:
                # 续写从重复部分之后开始
                cont = cont[idx + len(tail):]

        return existing + cont

    def _mock_response(self, prompt: str) -> LLMResponse:
        """显式mock响应（仅测试用）。"""
        mock_json = {
            "artifact_type": "mock",
            "_mock_warning": "这是 mock 响应，不是真实 LLM 输出",
            "_prompt_length": len(prompt),
        }
        return LLMResponse(
            text=json.dumps(mock_json, ensure_ascii=False),
            input_tokens=0,
            output_tokens=0,
            elapsed_ms=0,
            model="mock",
        )

    @staticmethod
    def extract_json(text: str) -> dict[str, Any]:
        """从LLM输出中提取JSON对象（容忍markdown包裹+自动修复截断）。

        处理策略：
        1. 优先匹配 ```json ... ``` 包裹
        2. fallback到匹配第一个 { 到最后一个 }
        3. 直接解析失败时，尝试修复截断的JSON（补全未闭合括号）
        4. 全部失败抛 JSONExtractionError

        Args:
            text: LLM返回的原始文本

        Returns:
            解析后的dict

        Raises:
            JSONExtractionError: 未找到或修复后仍解析失败
        """
        # 去除markdown包裹
        cleaned = text.strip()
        fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", cleaned, re.DOTALL)
        if fenced:
            raw = fenced.group(1)
        else:
            # 去除可能的 ```json 开头但无闭合的情况
            if cleaned.startswith("```"):
                nl = cleaned.find("\n")
                if nl != -1:
                    cleaned = cleaned[nl + 1:]
            # 找第一个 { 到最后一个 }
            start = cleaned.find("{")
            end = cleaned.rfind("}")
            if start == -1:
                raise JSONExtractionError(
                    f"LLM 输出中未找到 JSON 起始 {{（前100字: {text[:100]!r}）"
                )
            if end <= start:
                # 没有闭合 } —— 说明被截断，取从 { 到结尾
                raw = cleaned[start:]
            else:
                raw = cleaned[start : end + 1]

        # 尝试1: 直接解析
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            pass

        # 尝试2: 修复截断的JSON（补全未闭合括号）
        repaired = LLMClient._repair_truncated_json(raw)
        if repaired is not None:
            try:
                result = json.loads(repaired)
                return result
            except json.JSONDecodeError:
                pass

        # 全部失败
        try:
            json.loads(raw)
        except json.JSONDecodeError as exc:
            raise JSONExtractionError(
                f"JSON 解析失败（修复后仍失败）: {exc}。"
                f"长度{len(raw)}字符，末尾100字: {raw[-100:]!r}"
            ) from exc

    @staticmethod
    def _repair_truncated_json(raw: str) -> str | None:
        """修复被截断的JSON（补全未闭合的括号/引号）。

        策略：
        1. 用栈追踪 { [ 的嵌套（正确跳过字符串内的括号）
        2. 移除末尾不完整的部分（trailing comma / 半个token）
        3. 按栈顺序补全 ] }

        注意：这是兜底修复，可能丢失末尾未输出完的字段，
        但保证产出可解析的合法JSON（核心字段通常在前面已完整）。

        Returns:
            修复后的JSON字符串；无法修复返回None
        """
        stack: list[str] = []
        in_string = False
        escape = False
        last_safe_pos = -1  # 最后一个"安全截断点"（完整value结束处）

        for i, ch in enumerate(raw):
            if escape:
                escape = False
                continue
            if ch == "\\":
                escape = True
                continue
            if ch == '"':
                in_string = not in_string
                if not in_string:
                    # 字符串刚结束，是潜在安全点
                    last_safe_pos = i
                continue
            if in_string:
                continue
            # 非字符串内
            if ch in "{[":
                stack.append(ch)
            elif ch in "}]":
                if stack:
                    stack.pop()
                last_safe_pos = i
            elif ch in "0123456789truefalsenull":
                # 数字/布尔/null结尾也是潜在安全点
                last_safe_pos = i

        # 如果还在字符串中，说明字符串被截断 → 回退到上个安全点
        if in_string and last_safe_pos > 0:
            truncated = raw[: last_safe_pos + 1]
            # 重新计算栈
            return LLMClient._close_brackets(truncated)

        # 不在字符串中：去除末尾的trailing comma和空白
        trimmed = raw.rstrip()
        # 去除末尾残缺的 "key": 或 "key": "incomplet 之类
        # 回退到最后一个完整结构点（} ] " 或数字）
        while trimmed and trimmed[-1] not in '}]"0123456789truenul':
            if trimmed[-1] == ",":
                trimmed = trimmed[:-1].rstrip()
                break
            trimmed = trimmed[:-1].rstrip()

        # 去除可能的trailing comma
        if trimmed.endswith(","):
            trimmed = trimmed[:-1].rstrip()

        return LLMClient._close_brackets(trimmed)

    @staticmethod
    def _close_brackets(s: str) -> str | None:
        """根据未闭合的括号栈，补全闭合符号。"""
        stack: list[str] = []
        in_string = False
        escape = False

        for ch in s:
            if escape:
                escape = False
                continue
            if ch == "\\":
                escape = True
                continue
            if ch == '"':
                in_string = not in_string
                continue
            if in_string:
                continue
            if ch in "{[":
                stack.append(ch)
            elif ch == "}":
                if stack and stack[-1] == "{":
                    stack.pop()
            elif ch == "]":
                if stack and stack[-1] == "[":
                    stack.pop()

        # 如果仍在字符串中，无法安全修复
        if in_string:
            return None

        # 去除trailing comma
        s = s.rstrip()
        if s.endswith(","):
            s = s[:-1].rstrip()

        # 按栈逆序补全
        closing = ""
        for opener in reversed(stack):
            closing += "}" if opener == "{" else "]"

        return s + closing


def main():
    """CLI测试入口（连通性验证）"""
    import argparse
    import asyncio

    parser = argparse.ArgumentParser(description="测试 LLMClient")
    parser.add_argument("--mock", action="store_true", help="使用mock模式")
    parser.add_argument(
        "--model",
        default="claude-opus-4-8",
        help="模型ID",
    )
    args = parser.parse_args()

    client = LLMClient(model=args.model, max_tokens=128, mock=args.mock)

    async def run():
        prompt = "Reply with exactly this JSON: {\"status\": \"ok\", \"test\": true}"
        print(f"=== 调用 LLM ({args.model}, mock={args.mock}) ===")
        try:
            resp = await client.call(prompt)
            print(f"✅ 响应: {resp.text[:200]}")
            print(f"   tokens: {resp.input_tokens} in / {resp.output_tokens} out")
            print(f"   时间: {resp.elapsed_ms}ms")

            # 测试JSON提取
            extracted = LLMClient.extract_json(resp.text)
            print(f"✅ 提取JSON: {extracted}")
        except (LLMClientError, JSONExtractionError) as exc:
            print(f"❌ 失败: {exc}")
            raise

    asyncio.run(run())


if __name__ == "__main__":
    main()
