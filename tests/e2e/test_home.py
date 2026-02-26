"""
フィーチャー: ホームページ

初回訪問者がランディングページで体験するジャーニー
"""

import allure

from .conftest import HomePage


@allure.feature("ホーム")
@allure.story("訪問者がウェルカムページを閲覧する")
def test_トップページにタイトルと説明文が表示される(home: HomePage):
    """訪問者がトップページを開き、ウェルカムメッセージを確認する"""
    # 実行
    home.open()

    # 検証
    assert home.title == "Welcome to SampleApp"
    assert "React + FastAPI" in home.description


@allure.feature("ホーム")
@allure.story("訪問者がAboutカードからAboutページへ遷移する")
def test_AboutカードからAboutページへ遷移できる(home: HomePage, page):
    """訪問者がAboutカードをクリックし、Aboutページに移動する"""
    # 準備
    home.open()

    # 実行
    home.click_about_card()

    # 検証
    assert "/about" in page.url
