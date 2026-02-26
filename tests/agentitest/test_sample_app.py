"""
AIエージェントによるE2Eテスト

browser_use + Gemini を使い、自然言語指示でブラウザを操作する。
従来のPlaywright E2Eテスト（tests/e2e/）と同じ11ケースを検証する。
"""

import allure

from .conftest import BaseAgentTest, BrowserSession, ChatGoogle


# ---------------------------------------------------------------------------
# ホームページ (2ケース)
# ---------------------------------------------------------------------------


@allure.feature("ホーム")
class TestHome(BaseAgentTest):

    @allure.story("訪問者がウェルカムページを閲覧する")
    async def test_トップページにタイトルと説明文が表示される(
        self, llm: ChatGoogle, browser_session: BrowserSession
    ):
        """トップページに 'Welcome to SampleApp' と 'React + FastAPI' が表示される"""
        await self.run_task(
            llm,
            browser_session,
            "confirm that the heading says 'Welcome to SampleApp' "
            "and the page description mentions 'React + FastAPI'. "
            "Return 'welcome_confirmed' if both are visible.",
            "welcome_confirmed",
        )

    @allure.story("訪問者がAboutカードからAboutページへ遷移する")
    async def test_AboutカードからAboutページへ遷移できる(
        self, llm: ChatGoogle, browser_session: BrowserSession
    ):
        """Aboutカードをクリックし、URLに /about が含まれることを確認する"""
        await self.run_task(
            llm,
            browser_session,
            "find and click the 'About' card (not the nav link, but the card on the page). "
            "Confirm the URL now contains '/about'. "
            "Return 'about_navigated' if it does.",
            "about_navigated",
        )


# ---------------------------------------------------------------------------
# 認証 (3ケース)
# ---------------------------------------------------------------------------


@allure.feature("認証")
class TestAuth(BaseAgentTest):

    @allure.story("未認証ユーザーがログインページにリダイレクトされる")
    async def test_未認証でTodoページにアクセスするとログインに飛ぶ(
        self, llm: ChatGoogle, browser_session: BrowserSession
    ):
        """未認証で /todo にアクセスすると /login にリダイレクトされる"""
        await self.run_task(
            llm,
            browser_session,
            "click the 'Todo' link in the navigation. "
            "You should be redirected to a login page. "
            "Confirm that a 'Sign In' heading is visible and the URL contains '/login'. "
            "Return 'redirected_to_login' if both are true.",
            "redirected_to_login",
        )

    @allure.story("ユーザーがサインインしてTodoページに到達する")
    async def test_正しい認証情報でサインインするとTodoページが表示される(
        self, llm: ChatGoogle, browser_session: BrowserSession
    ):
        """メアド・パスワードでサインインし、Todo Listページが表示される"""
        await self.run_task(
            llm,
            browser_session,
            f"{self._sign_in_instruction()} "
            "After signing in, confirm that a 'Todo List' heading is visible. "
            "Return 'todo_page_visible' if it is.",
            "todo_page_visible",
        )

    @allure.story("ユーザーがサインアウトするとアクセスできなくなる")
    async def test_サインアウト後にTodoページへアクセスするとログインに戻る(
        self, llm: ChatGoogle, browser_session: BrowserSession
    ):
        """サインアウト後、/todo にアクセスするとログインに戻る"""
        await self.run_task(
            llm,
            browser_session,
            f"{self._sign_in_instruction()} "
            "After reaching the Todo page, click the 'Sign Out' button. "
            "Then click the 'Todo' link in the navigation again. "
            "Confirm that you are redirected to the login page with a 'Sign In' heading. "
            "Return 'signed_out_redirected' if the login page is shown.",
            "signed_out_redirected",
        )


# ---------------------------------------------------------------------------
# ナビゲーション (3ケース)
# ---------------------------------------------------------------------------


@allure.feature("ナビゲーション")
class TestNavigation(BaseAgentTest):

    @allure.story("訪問者がナビでページ間を移動する")
    async def test_ナビでHomeとAboutを行き来できる(
        self, llm: ChatGoogle, browser_session: BrowserSession
    ):
        """ナビバーでHomeとAboutを行き来できる"""
        await self.run_task(
            llm,
            browser_session,
            "click the 'About' link in the navigation bar. "
            "Confirm the URL contains '/about'. "
            "Then click the 'Home' link in the navigation bar. "
            "Confirm you are back on the home page with the 'Welcome to SampleApp' heading. "
            "Return 'navigation_works' if both navigations succeed.",
            "navigation_works",
        )

    @allure.story("未認証時にSign Inリンクが表示される")
    async def test_未認証時ナビにサインインリンクが表示される(
        self, llm: ChatGoogle, browser_session: BrowserSession
    ):
        """未認証のとき、ナビに 'Sign In' リンクが表示される"""
        await self.run_task(
            llm,
            browser_session,
            "look at the navigation bar. "
            "Confirm that a 'Sign In' link is visible and there is no 'Sign Out' button. "
            "Return 'sign_in_visible' if the 'Sign In' link is shown.",
            "sign_in_visible",
        )

    @allure.story("認証後にSign Outボタンが表示される")
    async def test_認証後ナビにサインアウトボタンが表示される(
        self, llm: ChatGoogle, browser_session: BrowserSession
    ):
        """サインイン後、ナビに 'Sign Out' ボタンが表示される"""
        await self.run_task(
            llm,
            browser_session,
            f"{self._sign_in_instruction()} "
            "Now look at the navigation bar. "
            "Confirm that a 'Sign Out' button is visible and there is no 'Sign In' link. "
            "Return 'sign_out_visible' if the 'Sign Out' button is shown.",
            "sign_out_visible",
        )


# ---------------------------------------------------------------------------
# Todo管理 (3ケース)
# ---------------------------------------------------------------------------


@allure.feature("Todo")
class TestTodo(BaseAgentTest):

    @allure.story("ユーザーがTodoを追加してリストに表示される")
    async def test_Todoを追加するとリストに表示される(
        self, llm: ChatGoogle, browser_session: BrowserSession
    ):
        """Todoを追加し、リストに表示されることを確認する"""
        await self.run_task(
            llm,
            browser_session,
            f"{self._sign_in_instruction()} "
            "On the Todo page, type '買い物に行く' in the input field and click 'Add'. "
            "Confirm that '買い物に行く' appears in the todo list. "
            "Return 'todo_added' if it does.",
            "todo_added",
        )

    @allure.story("ユーザーがTodoを削除する")
    async def test_Todoを追加して削除すると空メッセージが表示される(
        self, llm: ChatGoogle, browser_session: BrowserSession
    ):
        """Todoを追加→削除し、'No todos yet' が表示される"""
        await self.run_task(
            llm,
            browser_session,
            f"{self._sign_in_instruction()} "
            "On the Todo page, type '一時的なタスク' in the input field and click 'Add'. "
            "Wait for it to appear in the list. "
            "Then click the 'Delete' button next to '一時的なタスク'. "
            "Confirm that 'No todos yet' message is displayed. "
            "Return 'todo_deleted' if the empty message is shown.",
            "todo_deleted",
        )

    @allure.story("ユーザーが複数のTodoを管理する")
    async def test_複数Todoから1件削除すると残りが正しく表示される(
        self, llm: ChatGoogle, browser_session: BrowserSession
    ):
        """3件追加→1件削除し、残り2件が正しく表示される"""
        await self.run_task(
            llm,
            browser_session,
            f"{self._sign_in_instruction()} "
            "On the Todo page, add three todos: 'タスクA', 'タスクB', 'タスクC' "
            "(type each one and click 'Add', waiting for it to appear before adding the next). "
            "Then delete 'タスクB' by clicking its 'Delete' button. "
            "Confirm that 'タスクA' and 'タスクC' are still in the list, "
            "but 'タスクB' is gone. "
            "Return 'partial_delete_ok' if the remaining items are correct.",
            "partial_delete_ok",
        )
