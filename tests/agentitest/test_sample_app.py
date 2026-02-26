"""
AIエージェントによるE2Eテスト

browser_use + Gemini を使い、自然言語指示でブラウザを操作する。
従来のPlaywright E2Eテストとの比較用。
"""

import allure
import pytest

from .conftest import BaseAgentTest, BrowserSession, ChatGoogle


@allure.feature("ホームページ")
class TestHomePage(BaseAgentTest):
    """ホームページのテスト"""

    @allure.story("ページタイトル")
    @allure.title("ホームページのタイトルが表示される")
    async def test_home_page_title(
        self,
        llm: ChatGoogle,
        browser_session: BrowserSession,
    ) -> None:
        """ホームページのタイトルが表示されることを確認する"""
        task = "confirm that the 'Sample App' heading is visible on the page. Return 'title_visible' if it is."
        await self.validate_task(llm, browser_session, task, "title_visible", ignore_case=True)


@allure.feature("ナビゲーション")
class TestNavigation(BaseAgentTest):
    """ページ間遷移のテスト"""

    @allure.story("Aboutページへ遷移")
    @allure.title("Aboutページへ遷移できる")
    async def test_navigate_to_about(
        self,
        llm: ChatGoogle,
        browser_session: BrowserSession,
    ) -> None:
        """Aboutページへ遷移できることを確認する"""
        task = "click the 'About' link in the navigation, then confirm that the 'About' heading is visible. Return 'about_visible' if it is."
        await self.validate_task(llm, browser_session, task, "about_visible", ignore_case=True)

    @allure.story("Todoページへ遷移")
    @allure.title("Todoページへ遷移できる")
    async def test_navigate_to_todo(
        self,
        llm: ChatGoogle,
        browser_session: BrowserSession,
    ) -> None:
        """Todoページへ遷移できることを確認する"""
        task = "click the 'Todo' link in the navigation, then confirm that the 'Todo List' heading is visible. Return 'todo_visible' if it is."
        await self.validate_task(llm, browser_session, task, "todo_visible", ignore_case=True)


@allure.feature("Todo機能")
class TestTodo(BaseAgentTest):
    """Todo機能のテスト"""

    @allure.story("Todo追加")
    @allure.title("新しいTodoを追加できる")
    async def test_add_todo(
        self,
        llm: ChatGoogle,
        browser_session: BrowserSession,
    ) -> None:
        """新しいTodoを追加してリストに表示されることを確認する"""
        task = (
            "click the 'Todo' link in the navigation. "
            "Then type 'Buy groceries' into the input field and click the 'Add' button. "
            "Confirm that 'Buy groceries' appears in the list. Return 'todo_added' if it does."
        )
        await self.validate_task(llm, browser_session, task, "todo_added", ignore_case=True)
