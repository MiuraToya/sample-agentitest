"""
AgentiTest設定 — AIエージェント（browser_use + Gemini）によるE2Eテスト

LLMエージェントが自然言語の指示でブラウザを操作し、
UIの振る舞いを検証する。従来のPlaywrightテストとの比較用。
"""

from __future__ import annotations

import asyncio
import base64
import binascii
import logging
import os
import sys
from importlib.metadata import version
from typing import TYPE_CHECKING, Any

import allure
import pytest
from browser_use import (
    Agent,
    BrowserProfile,
    BrowserSession,
    ChatGoogle,
)
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

load_dotenv()
logger = logging.getLogger(__name__)

BASE_URL = os.environ.get(
    "E2E_BASE_URL", "https://d214my39l3yw2c.cloudfront.net"
)
LLM_TEMPERATURE = 0.2


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def browser_version_info(browser_profile: BrowserProfile) -> dict[str, str]:
    """Playwrightとブラウザのバージョンを取得する"""
    try:
        with sync_playwright() as p:
            playwright_version: str = version("playwright")
            browser_type_name: str = (
                browser_profile.channel if browser_profile.channel else "chromium"
            )
            browser = p[browser_type_name].launch()
            browser_version: str = browser.version
            browser.close()
            return {
                "playwright_version": playwright_version,
                "browser_version": f"{browser_type_name} {browser_version}",
            }
    except Exception as e:
        logger.warning(f"Could not determine Playwright/browser version: {e}")
        return {
            "playwright_version": "N/A",
            "browser_version": "N/A",
        }


@pytest.fixture(scope="session", autouse=True)
def allure_environment(
    request: pytest.FixtureRequest,
    browser_version_info: dict[str, str],
) -> None:
    """Allureレポート用の環境情報を出力する"""
    allure_dir: str | None = request.config.getoption("--alluredir")
    if not allure_dir:
        return

    properties_file: str = os.path.join(allure_dir, "environment.properties")

    try:
        os.makedirs(allure_dir, exist_ok=True)
    except OSError:
        return

    env_props: dict[str, str] = {
        "OS": os.name,
        "Python": f"{sys.version_info.major}.{sys.version_info.minor}",
        "Playwright": browser_version_info["playwright_version"],
        "Browser": browser_version_info["browser_version"],
        "Run URL": os.getenv("GITHUB_SERVER_URL", "")
        + "/"
        + os.getenv("GITHUB_REPOSITORY", "")
        + "/actions/runs/"
        + os.getenv("GITHUB_RUN_ID", ""),
    }
    with open(properties_file, "w") as f:
        f.writelines(f"{key}={value}\n" for key, value in env_props.items())


@pytest.fixture
async def llm() -> ChatGoogle:
    """LLMを初期化する（Gemini）"""
    model_name: str = os.getenv("GEMINI_MODEL", "gemini-2.5-pro")
    return ChatGoogle(
        model=model_name,
        temperature=LLM_TEMPERATURE,
        api_key=os.getenv("GEMINI_API_KEY"),
    )


@pytest.fixture(scope="session")
def browser_profile() -> BrowserProfile:
    """ブラウザプロファイルを設定する"""
    headless_mode: bool = os.getenv("HEADLESS", "True").lower() in ("true", "1", "t")
    return BrowserProfile(headless=headless_mode, keep_alive=True)


@pytest.fixture
async def browser_session(
    browser_profile: BrowserProfile,
) -> AsyncGenerator[BrowserSession, None]:
    """ブラウザセッションのライフサイクルを管理する"""
    session: BrowserSession = BrowserSession(browser_profile=browser_profile)
    await session.start()
    try:
        yield session
    finally:
        await session.stop()


# ---------------------------------------------------------------------------
# エージェント実行ヘルパー
# ---------------------------------------------------------------------------


class BaseAgentTest:
    """AIエージェントテストの基底クラス"""

    async def validate_task(
        self,
        llm: ChatGoogle,
        browser_session: BrowserSession,
        task_instruction: str,
        expected_substring: str,
        ignore_case: bool = False,
    ) -> str:
        """エージェントにタスクを実行させ、結果を検証する"""
        full_task: str = f"Go to {BASE_URL}, then {task_instruction}"
        result_text: str = await run_agent_task(full_task, llm, browser_session)
        assert result_text is not None and result_text.strip() != "", (
            "Agent did not return a result."
        )

        if expected_substring:
            result_to_check = result_text.lower()
            possible_confirmations = {
                expected_substring.lower() if ignore_case else expected_substring,
                "visible",
                "found",
                "confirmed",
                "i see it",
            }
            assert any(
                phrase in result_to_check for phrase in possible_confirmations
            ), (
                f"Expected a confirmation like '{expected_substring}', but got: '{result_text}'"
            )

        return result_text


async def record_step(agent: Agent) -> None:
    """各ステップのアクティビティをAllureに記録するフック"""
    history = agent.history

    last_action: dict[str, Any] = (
        history.model_actions()[-1] if history.model_actions() else {}
    )
    action_name: str = next(iter(last_action)) if last_action else "No action"
    action_params: dict[str, Any] = last_action.get(action_name, {})
    step_title: str = f"Action: {action_name}"
    param_str: str = ", ".join(f"{k}={v}" for k, v in action_params.items())
    if param_str:
        step_title += f"({param_str})"

    with allure.step(step_title):
        thoughts = history.model_thoughts()
        if thoughts:
            allure.attach(
                str(thoughts[-1]),
                name="Agent Thoughts",
                attachment_type=allure.attachment_type.TEXT,
            )

        url: str | None = history.urls()[-1] if history.urls() else "N/A"
        allure.attach(url, name="URL", attachment_type=allure.attachment_type.TEXT)

        last_history_item = history.history[-1] if history.history else None
        if last_history_item and last_history_item.metadata:
            duration: float = last_history_item.metadata.duration_seconds
            allure.attach(
                f"{duration:.2f}s",
                name="Step Duration",
                attachment_type=allure.attachment_type.TEXT,
            )

        try:
            screenshot_b64 = await agent.browser_session.take_screenshot()
            if screenshot_b64:
                if isinstance(screenshot_b64, bytes):
                    screenshot_bytes: bytes | None = screenshot_b64
                elif _is_valid_base64(screenshot_b64):
                    screenshot_bytes = base64.b64decode(screenshot_b64)
                else:
                    logger.warning("Invalid base64 padding in screenshot data")
                    screenshot_bytes = None

                if screenshot_bytes:
                    allure.attach(
                        screenshot_bytes,
                        name="Screenshot",
                        attachment_type=allure.attachment_type.PNG,
                    )
        except Exception as e:
            logger.warning(f"Failed to take or attach screenshot: {e}")


async def run_agent_task(
    full_task: str,
    llm: ChatGoogle,
    browser_session: BrowserSession,
) -> str:
    """エージェントを初期化してタスクを実行する"""
    logger.info(f"Running task: {full_task}")

    agent: Agent = Agent(
        task=full_task,
        llm=llm,
        browser_session=browser_session,
    )

    result = await asyncio.wait_for(agent.run(on_step_end=record_step), timeout=90)
    final_text: str | None = result.final_result()

    if final_text is not None:
        allure.attach(
            final_text,
            name="Final Result",
            attachment_type=allure.attachment_type.TEXT,
        )

    return final_text if final_text else ""


def _is_valid_base64(s: Any) -> bool:
    """Base64エンコードされたデータかどうかを検証する"""
    try:
        if isinstance(s, bytes):
            base64.b64decode(s, validate=True)
            return True
        if isinstance(s, str):
            if len(s) % 4 != 0:
                return False
            base64.b64decode(s, validate=True)
            return True
        return False
    except binascii.Error:
        return False
