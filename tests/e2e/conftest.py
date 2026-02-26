"""
E2Eテスト設定 — Page Objects & Fixtures

Page Object ModelでUI詳細をテストロジックから分離する。
各ページクラスはユーザーから見える操作・検証を公開する。
"""

from __future__ import annotations

import os

import allure
import boto3
import pytest
from playwright.sync_api import Page

BASE_URL = os.environ.get("E2E_BASE_URL", "https://d214my39l3yw2c.cloudfront.net")
TEST_EMAIL = os.environ.get("E2E_TEST_EMAIL", "test@example.com")
TEST_PASSWORD = os.environ.get("E2E_TEST_PASSWORD", "Test1234")
DYNAMODB_TABLE = os.environ.get("E2E_DYNAMODB_TABLE", "sample-agentitest-todos")
AWS_REGION = os.environ.get("E2E_AWS_REGION", "ap-northeast-1")


# ---------------------------------------------------------------------------
# Page Objects
# ---------------------------------------------------------------------------


class NavBar:
    """全ページ共通のトップナビゲーションバー"""

    def __init__(self, page: Page) -> None:
        self._page = page
        self._home_link = page.get_by_role("link", name="Home")
        self._about_link = page.get_by_role("link", name="About", exact=True)
        self._todo_link = page.get_by_role("link", name="Todo")

    def navigate_to_home(self) -> None:
        self._home_link.click()
        self._page.wait_for_load_state("networkidle")

    def navigate_to_about(self) -> None:
        self._about_link.click()
        self._page.wait_for_load_state("networkidle")

    def navigate_to_todo(self) -> None:
        self._todo_link.click()
        self._page.wait_for_load_state("networkidle")

    def sign_out(self) -> None:
        self._page.get_by_role("button", name="Sign Out").click()
        self._page.wait_for_timeout(500)

    @property
    def is_sign_in_link_visible(self) -> bool:
        return self._page.get_by_role("link", name="Sign In").is_visible()

    @property
    def is_sign_out_button_visible(self) -> bool:
        return self._page.get_by_role("button", name="Sign Out").is_visible()


class HomePage:
    """ランディングページ (/)"""

    def __init__(self, page: Page) -> None:
        self._page = page

    def open(self) -> None:
        self._page.goto(f"{BASE_URL}/")
        self._page.wait_for_load_state("networkidle")

    @property
    def title(self) -> str:
        return self._page.get_by_role("heading", level=1).inner_text()

    @property
    def description(self) -> str:
        return self._page.locator("main p").first.inner_text()

    def click_about_card(self) -> None:
        self._page.get_by_role("heading", name="About").click()
        self._page.wait_for_load_state("networkidle")


class AboutPage:
    """Aboutページ (/about)"""

    def __init__(self, page: Page) -> None:
        self._page = page

    def open(self) -> None:
        self._page.goto(f"{BASE_URL}/about")
        self._page.wait_for_load_state("networkidle")

    @property
    def title(self) -> str:
        return self._page.get_by_role("heading", level=1).inner_text()


class LoginPage:
    """ログイン・サインアップページ (/login)"""

    def __init__(self, page: Page) -> None:
        self._page = page

    def open(self) -> None:
        self._page.goto(f"{BASE_URL}/login")
        self._page.wait_for_load_state("networkidle")

    @property
    def is_visible(self) -> bool:
        return self._page.get_by_role("heading", name="Sign In").is_visible()

    def sign_in(self, email: str, password: str) -> None:
        self._page.get_by_placeholder("Email").fill(email)
        self._page.get_by_placeholder("Password").fill(password)
        self._page.get_by_role("button", name="Sign In").click()


class TodoPage:
    """Todo管理ページ (/todo)"""

    def __init__(self, page: Page) -> None:
        self._page = page

    def open(self) -> None:
        self._page.goto(f"{BASE_URL}/todo")
        self._page.wait_for_load_state("networkidle")

    @property
    def is_visible(self) -> bool:
        return self._page.get_by_role("heading", name="Todo List").is_visible()

    def add_todo(self, title: str) -> None:
        """Todoを入力して追加ボタンを押し、リストに表示されるまで待つ"""
        self._page.get_by_placeholder("Enter a new todo").fill(title)
        self._page.get_by_role("button", name="Add").click()
        self._page.get_by_text(title).first.wait_for(timeout=10000)

    def delete_todo(self, title: str) -> None:
        """指定タイトルのTodoを削除し、消えるまで待つ"""
        row = self._page.locator("li", has_text=title).first
        row.get_by_role("button", name="Delete").click()
        self._page.get_by_text(title).first.wait_for(state="hidden", timeout=10000)

    @property
    def todo_titles(self) -> list[str]:
        items = self._page.locator("li span").all()
        return [item.inner_text() for item in items]

    @property
    def empty_message(self) -> str:
        el = self._page.get_by_text("No todos yet")
        if el.is_visible():
            return el.inner_text()
        return ""


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def browser_context_args():
    """ブラウザコンテキストの設定"""
    return {"viewport": {"width": 1280, "height": 720}}


@pytest.fixture
def nav(page: Page) -> NavBar:
    return NavBar(page)


@pytest.fixture
def home(page: Page) -> HomePage:
    return HomePage(page)


@pytest.fixture
def about(page: Page) -> AboutPage:
    return AboutPage(page)


@pytest.fixture
def login(page: Page) -> LoginPage:
    return LoginPage(page)


@pytest.fixture
def todo(page: Page) -> TodoPage:
    return TodoPage(page)


@pytest.fixture
def signed_in(page: Page) -> None:
    """テストユーザーでサインインし、Todoページに遷移する"""
    page.goto(f"{BASE_URL}/login")
    page.wait_for_load_state("networkidle")
    page.get_by_placeholder("Email").fill(TEST_EMAIL)
    page.get_by_placeholder("Password").fill(TEST_PASSWORD)
    page.get_by_role("button", name="Sign In").click()
    page.wait_for_url("**/todo", timeout=10000)
    page.wait_for_load_state("networkidle")


@pytest.fixture(autouse=True)
def cleanup_test_data():
    """テスト後にDynamoDBのTodoデータを削除する"""
    yield
    kwargs = {"region_name": AWS_REGION}
    if os.environ.get("AWS_PROFILE"):
        kwargs["profile_name"] = os.environ["AWS_PROFILE"]
    session = boto3.Session(**kwargs)
    dynamodb = session.resource("dynamodb")
    table = dynamodb.Table(DYNAMODB_TABLE)
    response = table.scan()
    for item in response.get("Items", []):
        if item["id"] != 0:  # カウンターは保持
            table.delete_item(Key={"id": item["id"]})


@pytest.fixture(autouse=True)
def screenshot_on_failure(page: Page, request):
    """テスト失敗時にAllureレポートにスクリーンショットを添付する"""
    yield
    if request.node.rep_call and request.node.rep_call.failed:
        allure.attach(
            page.screenshot(),
            name="screenshot_on_failure",
            attachment_type=allure.attachment_type.PNG,
        )


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """テスト結果をrequestノードに格納（スクリーンショット用）"""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)
