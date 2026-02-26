"""
フィーチャー: Todo管理

ログイン後のTodo作成・表示・削除のユーザージャーニー
"""

import allure

from .conftest import Todoページ


@allure.feature("Todo")
@allure.story("ユーザーがTodoを追加してリストに表示される")
def test_Todoを追加するとリストに表示される(サインイン済み, todo: Todoページ):
    """サインイン済みユーザーがTodoを追加し、リストに反映されることを確認する"""
    # 実行
    todo.todoを追加("買い物に行く")

    # 検証
    assert "買い物に行く" in todo.todoタイトル一覧


@allure.feature("Todo")
@allure.story("ユーザーがTodoを削除する")
def test_Todoを追加して削除すると空メッセージが表示される(サインイン済み, todo: Todoページ):
    """Todoを追加してから削除すると、空のメッセージが表示される"""
    # 準備
    todo.todoを追加("一時的なタスク")

    # 実行
    todo.todoを削除("一時的なタスク")

    # 検証
    assert "No todos yet" in todo.空メッセージ


@allure.feature("Todo")
@allure.story("ユーザーが複数のTodoを管理する")
def test_複数Todoから1件削除すると残りが正しく表示される(サインイン済み, todo: Todoページ):
    """複数Todoを追加し、1件だけ削除すると残りが正しく表示される"""
    # 準備
    todo.todoを追加("タスクA")
    todo.todoを追加("タスクB")
    todo.todoを追加("タスクC")

    # 実行 — 真ん中を削除
    todo.todoを削除("タスクB")

    # 検証
    titles = todo.todoタイトル一覧
    assert "タスクA" in titles
    assert "タスクB" not in titles
    assert "タスクC" in titles
