"""
フィーチャー: ナビゲーション

ページ間遷移と認証状態に応じたナビ表示のジャーニー
"""

import allure

from .conftest import BASE_URL, HomePage, NavBar


@allure.feature("ナビゲーション")
@allure.story("訪問者がナビでページ間を移動する")
def test_ナビでHomeとAboutを行き来できる(home: HomePage, nav: NavBar, page):
    """訪問者がナビバーでHomeとAboutを行き来する"""
    # 準備
    home.open()

    # 実行・検証 — Aboutへ遷移
    nav.navigate_to_about()
    assert "/about" in page.url

    # 実行・検証 — Homeに戻る
    nav.navigate_to_home()
    assert page.url.rstrip("/").endswith(BASE_URL.rstrip("/")) or page.url.endswith("/")


@allure.feature("ナビゲーション")
@allure.story("未認証時にSign Inリンクが表示される")
def test_未認証時ナビにサインインリンクが表示される(home: HomePage, nav: NavBar):
    """未認証の訪問者にはナビに「Sign In」リンクが表示される"""
    # 準備
    home.open()

    # 検証
    assert nav.is_sign_in_link_visible
    assert not nav.is_sign_out_button_visible


@allure.feature("ナビゲーション")
@allure.story("認証後にSign Outボタンが表示される")
def test_認証後ナビにサインアウトボタンが表示される(signed_in, nav: NavBar):
    """サインイン後、ナビに「Sign Out」ボタンが表示される"""
    # 検証
    assert nav.is_sign_out_button_visible
    assert not nav.is_sign_in_link_visible
