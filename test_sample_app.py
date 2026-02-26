import allure
import pytest

from conftest import BaseAgentTest, BrowserSession, ChatGoogle


@allure.feature("Home Page")
class TestHomePage(BaseAgentTest):
    """Tests for the home page."""

    @allure.story("Page Title")
    @allure.title("Test Home Page Title is Visible")
    async def test_home_page_title(
        self,
        llm: ChatGoogle,
        browser_session: BrowserSession,
    ) -> None:
        """Tests that the home page title is displayed."""
        task = "confirm that the 'Sample App' heading is visible on the page. Return 'title_visible' if it is."
        await self.validate_task(llm, browser_session, task, "title_visible", ignore_case=True)


@allure.feature("Navigation")
class TestNavigation(BaseAgentTest):
    """Tests for navigation between pages."""

    @allure.story("Navigate to About")
    @allure.title("Test Navigation to About Page")
    async def test_navigate_to_about(
        self,
        llm: ChatGoogle,
        browser_session: BrowserSession,
    ) -> None:
        """Tests navigation to the About page."""
        task = "click the 'About' link in the navigation, then confirm that the 'About' heading is visible. Return 'about_visible' if it is."
        await self.validate_task(llm, browser_session, task, "about_visible", ignore_case=True)

    @allure.story("Navigate to Todo")
    @allure.title("Test Navigation to Todo Page")
    async def test_navigate_to_todo(
        self,
        llm: ChatGoogle,
        browser_session: BrowserSession,
    ) -> None:
        """Tests navigation to the Todo page."""
        task = "click the 'Todo' link in the navigation, then confirm that the 'Todo List' heading is visible. Return 'todo_visible' if it is."
        await self.validate_task(llm, browser_session, task, "todo_visible", ignore_case=True)


@allure.feature("Todo Functionality")
class TestTodo(BaseAgentTest):
    """Tests for the todo list functionality."""

    @allure.story("Add a Todo")
    @allure.title("Test Adding a New Todo Item")
    async def test_add_todo(
        self,
        llm: ChatGoogle,
        browser_session: BrowserSession,
    ) -> None:
        """Tests adding a new todo item."""
        task = (
            "click the 'Todo' link in the navigation. "
            "Then type 'Buy groceries' into the input field and click the 'Add' button. "
            "Confirm that 'Buy groceries' appears in the list. Return 'todo_added' if it does."
        )
        await self.validate_task(llm, browser_session, task, "todo_added", ignore_case=True)
