"""
フィーチャー: ホームページ

初回訪問者がランディングページで体験するジャーニー
"""

import allure

from .conftest import ホームページ


@allure.feature("ホーム")
@allure.story("訪問者がウェルカムページを閲覧する")
def test_トップページにタイトルと説明文が表示される(ホーム: ホームページ):
    """訪問者がトップページを開き、ウェルカムメッセージを確認する"""
    # 実行
    ホーム.開く()

    # 検証
    assert ホーム.タイトル == "Welcome to SampleApp"
    assert "React + FastAPI" in ホーム.説明文


@allure.feature("ホーム")
@allure.story("訪問者がAboutカードからAboutページへ遷移する")
def test_AboutカードからAboutページへ遷移できる(ホーム: ホームページ, page):
    """訪問者がAboutカードをクリックし、Aboutページに移動する"""
    # 準備
    ホーム.開く()

    # 実行
    ホーム.aboutカードをクリック()

    # 検証
    assert "/about" in page.url
