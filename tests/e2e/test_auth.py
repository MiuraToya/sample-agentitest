"""
フィーチャー: 認証

サインイン・アクセス制御・サインアウトのユーザージャーニー
"""

import allure

from .conftest import BASE_URL, ログインページ, Todoページ, ナビバー


@allure.feature("認証")
@allure.story("未認証ユーザーがログインページにリダイレクトされる")
def test_未認証でTodoページにアクセスするとログインに飛ぶ(page, ログイン: ログインページ):
    """サインインしていないユーザーが/todoにアクセスするとリダイレクトされる"""
    # 実行
    page.goto(f"{BASE_URL}/todo")
    page.wait_for_load_state("networkidle")

    # 検証
    assert ログイン.表示されている
    assert "/login" in page.url


@allure.feature("認証")
@allure.story("ユーザーがサインインしてTodoページに到達する")
def test_正しい認証情報でサインインするとTodoページが表示される(
    ログイン: ログインページ, todo: Todoページ, page
):
    """ユーザーが正しいメアド・パスワードを入力してTodoページに遷移する"""
    # 準備
    ログイン.開く()

    # 実行
    ログイン.サインイン("test@example.com", "Test1234")
    page.wait_for_url("**/todo", timeout=10000)
    page.wait_for_load_state("networkidle")

    # 検証
    assert todo.表示されている


@allure.feature("認証")
@allure.story("ユーザーがサインアウトするとアクセスできなくなる")
def test_サインアウト後にTodoページへアクセスするとログインに戻る(
    サインイン済み, page, ナビ: ナビバー, ログイン: ログインページ
):
    """サインアウト後、再度/todoにアクセスするとログインページに戻る"""
    # 実行 — サインアウト
    ナビ.サインアウト()

    # 実行 — /todoに再アクセス
    page.goto(f"{BASE_URL}/todo")
    page.wait_for_load_state("networkidle")

    # 検証
    assert ログイン.表示されている
