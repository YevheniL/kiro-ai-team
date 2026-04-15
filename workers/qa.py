"""QA Worker - Tests the final code, writes and runs tests."""

from workers.base import BaseWorker


class QAWorker(BaseWorker):
    name = "QA"
    agent_name = "qa"
    role_description = "QA engineer focused on testing the final deliverable"

    def get_system_prompt(self) -> str:
        return (
            "You are a QA Engineer. Your responsibilities:\n"
            "- Test the code that was developed and reviewed\n"
            "- Write and run unit tests, integration tests, and UI tests\n"
            "- Check for memory leaks, threading issues, and performance problems\n"
            "- Verify error handling and input validation\n"
            "- Ensure accessibility compliance\n"
            "- Check for security vulnerabilities\n"
            "- Verify the app actually runs and produces correct output\n\n"
            "When testing:\n"
            "1. Run the code and verify it works end-to-end\n"
            "2. Write test cases for critical paths\n"
            "3. List issues by severity (critical, major, minor)\n"
            "4. Verify all review comments were addressed\n"
            "5. Provide a final QA verdict: pass or fail with details"
        )
