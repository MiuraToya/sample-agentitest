"""
フィーチャー: 認証

サインイン・アクセス制御・サインアウトのユーザージャーニー
"""

import allure

from .conftest import BASE_URL, LoginPage, NavBar, TodoPage


@allure.feature("認証")
@allure.story("未認証ユーザーがログインページにリダイレクトされる")
def test_未認証でTodoページにアクセスするとログインに飛ぶ(page, login: LoginPage):
    """サインインしていないユーザーが/todoにアクセスするとリダイレクトされる"""
    # 実行
    page.goto(f"{BASE_URL}/todo")
    page.wait_for_load_state("networkidle")

    # 検証
    assert login.is_visible
    assert "/login" in page.url


@allure.feature("認証")
@allure.story("ユーザーがサインインしてTodoページに到達する")
def test_正しい認証情報でサインインするとTodoページが表示される(
    login: LoginPage, todo: TodoPage, page
):
    """ユーザーが正しいメアド・パスワードを入力してTodoページに遷移する"""
    # 準備
    login.open()

    # 実行
    login.sign_in("test@example.com", "Test1234")
    page.wait_for_url("**/todo", timeout=10000)
    page.wait_for_load_state("networkidle")

    # 検証
    assert todo.is_visible


@allure.feature("認証")
@allure.story("ユーザーがサインアウトするとアクセスできなくなる")
def test_サインアウト後にTodoページへアクセスするとログインに戻る(
    signed_in, page, nav: NavBar, login: LoginPage
):
    """サインアウト後、再度/todoにアクセスするとログインページに戻る"""
    # 実行 — サインアウト
    nav.sign_out()

    # 実行 — /todoに再アクセス
    page.goto(f"{BASE_URL}/todo")
    page.wait_for_load_state("networkidle")

    # 検証
    assert login.is_visible
