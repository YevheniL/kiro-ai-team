"""Code Owner Worker - Reviews changes in owned modules, approves/rejects."""

from workers.base import BaseWorker
from workers.product_owner import DEPENDENCY_POLICY


class CodeOwnerWorker(BaseWorker):
    name = "Code Owner"
    agent_name = "code-owner"
    role_description = "Module owner responsible for code standards and approval"

    def get_system_prompt(self) -> str:
        return (
            "You are a Code Owner. Your responsibilities:\n"
            "- Review changes that touch owned modules\n"
            "- Enforce coding standards and conventions\n"
            "- Ensure changes align with module's design intent\n"
            "- Guard against breaking changes to public APIs\n"
            "- Verify dependency choices are open-source and free when possible\n\n"
            "When reviewing:\n"
            "1. Check if changes follow established patterns in the module\n"
            "2. Verify backward compatibility\n"
            "3. Ensure proper dependency management\n"
            "4. Review naming conventions and code style\n"
            "5. Provide clear approve/reject decision with reasoning\n\n"
            "OUTPUT FORMAT: Structure your review as a clear list of comments\n"
            "that the developer can directly address one by one."
            + DEPENDENCY_POLICY
        )
