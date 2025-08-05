import asyncio
from mcp_servers.task_list import TaskList, get_task_list_mcp
from mcp_servers.filesystem import Filesystem, get_filesystem_mcp
from mcp_servers.calculator import mcp as calculator_mcp
from utils.mcp_helpers import compose_mcp_servers, run_mcp_server
from utils.test_utils import TestSuite

MCP_PORT = 8080

suite = TestSuite("Math Agent")


@suite.test("Agent can multiply two numbers without a calculator")
async def test_product_without_calculator():
    num_a = 983745
    num_b = 29837423
    expected_output = num_a * num_b
    task_list = TaskList(
        log_progress=True,
    )
    task_list.add_task(
        f"Multiply {num_a} * {num_b} and write the product to a file called 'output.txt'."
    )
    task_list_mcp = get_task_list_mcp(task_list)
    filesystem = Filesystem()
    filesystem_mcp = get_filesystem_mcp(filesystem)
    # Compose MCP servers and run
    all_mcp_servers = [task_list_mcp, filesystem_mcp]
    composed_mcp = compose_mcp_servers(*all_mcp_servers)
    mcp_server = run_mcp_server(composed_mcp, port=MCP_PORT)
    # Wait a minute for the agent to complete the task(s)
    try:
        await task_list.wait_for_all_completed(timeout_seconds=60)
    except TimeoutError:
        raise TimeoutError("Tasks did not complete in time")
    finally:
        mcp_server.stop()

    # Check output
    output = filesystem.read("output.txt")
    assert (
        int(output) == expected_output
    ), f"Expected {expected_output} but got {output}"


@suite.test("Agent can multiply two numbers with a calculator")
async def test_product_with_calculator():
    num_a = 983745
    num_b = 29837423
    expected_output = num_a * num_b
    task_list = TaskList(
        log_progress=True,
    )
    task_list.add_task(
        f"Multiply {num_a} * {num_b} and write the product to a file called 'output.txt'."
    )
    task_list_mcp = get_task_list_mcp(task_list)
    filesystem = Filesystem()
    filesystem_mcp = get_filesystem_mcp(filesystem)
    # Compose MCP servers and run
    all_mcp_servers = [task_list_mcp, filesystem_mcp, calculator_mcp]
    composed_mcp = compose_mcp_servers(*all_mcp_servers)
    mcp_server = run_mcp_server(composed_mcp, port=MCP_PORT)
    # Wait a minute for the agent to complete the task(s)
    try:
        await task_list.wait_for_all_completed(timeout_seconds=60)
    except TimeoutError:
        raise TimeoutError("Tasks did not complete in time")
    finally:
        mcp_server.stop()

    # Check output
    output = filesystem.read("output.txt")
    assert (
        int(output) == expected_output
    ), f"Expected {expected_output} but got {output}"


async def run():
    await suite.run()


if __name__ == "__main__":
    import asyncio

    asyncio.run(run())
