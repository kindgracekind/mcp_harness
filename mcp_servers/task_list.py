from fastmcp import FastMCP
from dataclasses import dataclass
import time


@dataclass
class Task:
    id: int
    description: str
    in_progress: bool = False
    completed: bool = False


class TaskList:

    def __init__(self, tasks: list[str] = [], log_progress: bool = False):
        self.tasks = [Task(id=i, description=task) for i, task in enumerate(tasks)]
        self.log_progress = log_progress

    def add_task(self, task: str):
        self.tasks.append(Task(id=len(self.tasks), description=task))

    def get_task_list(self):
        return self.tasks

    def mark_task_in_progress(self, task_id: int):
        self.tasks[task_id].in_progress = True
        if self.log_progress:
            print(f"Task {task_id} is in progress: '{self.tasks[task_id].description}'")

    def mark_task_complete(self, task_id: int):
        self.tasks[task_id].completed = True

    async def wait_for_all_completed(self, timeout_seconds: int = 10):
        import asyncio

        start_time = time.time()
        while not all(task.completed for task in self.tasks):
            if time.time() - start_time > timeout_seconds:
                raise TimeoutError
            await asyncio.sleep(0.1)


def get_task_list_mcp(task_list: TaskList):
    mcp = FastMCP("TaskList")

    @mcp.tool()
    def get_task_list() -> list[Task]:
        """Get the list of tasks."""
        return task_list.get_task_list()

    @mcp.tool()
    def mark_task_in_progress(task_id: int):
        """Mark a task as in progress."""
        task_list.mark_task_in_progress(task_id)

    @mcp.tool()
    def mark_task_complete(task_id: int):
        """Mark a task as complete."""
        task_list.mark_task_complete(task_id)

    @mcp.prompt()
    def complete_tasks_prompt():
        """Generate a prompt for completing the tasks."""
        return "Please complete the tasks."

    return mcp


# Must match the prompt function name above
TASK_PROMPT_NAME = "complete_tasks_prompt"
