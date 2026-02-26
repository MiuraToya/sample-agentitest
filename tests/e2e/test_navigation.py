"""
フィーチャー: ナビゲーション

ページ間遷移と認証状態に応じたナビ表示のジャーニー
"""

import allure

from .conftest import BASE_URL, ナビバー, ホームページ


@allure.feature("ナビゲーション")
@allure.story("訪問者がナビでページ間を移動する")
def test_ナビでHomeとAboutを行き来できる(ホーム: ホームページ, ナビ: ナビバー, page):
    """訪問者がナビバーでHomeとAboutを行き来する"""
    # 準備
    ホーム.開く()

    # 実行・検証 — Aboutへ遷移
    ナビ.aboutへ遷移()
    assert "/about" in page.url

    # 実行・検証 — Homeに戻る
    ナビ.homeへ遷移()
    assert page.url.rstrip("/").endswith(BASE_URL.rstrip("/")) or page.url.endswith("/")


@allure.feature("ナビゲーション")
@allure.story("未認証時にSign Inリンクが表示される")
def test_未認証時ナビにサインインリンクが表示される(ホーム: ホームページ, ナビ: ナビバー):
    """未認証の訪問者にはナビに「Sign In」リンクが表示される"""
    # 準備
    ホーム.開く()

    # 検証
    assert ナビ.サインインリンクが表示されている
    assert not ナビ.サインアウトボタンが表示されている


@allure.feature("ナビゲーション")
@allure.story("認証後にSign Outボタンが表示される")
def test_認証後ナビにサインアウトボタンが表示される(サインイン済み, ナビ: ナビバー):
    """サインイン後、ナビに「Sign Out」ボタンが表示される"""
    # 検証
    assert ナビ.サインアウトボタンが表示されている
    assert not ナビ.サインインリンクが表示されている
