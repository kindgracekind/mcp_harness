from mcp.client.streamable_http import streamablehttp_client
from mcp import ClientSession
import os
from utils.mcp_helpers import Multitool, serialize_content_from_mcp, get_prompt
from utils.llm_helpers import Conversation
import requests
import time

MCP_URL = os.environ.get("MCP_URL", "http://localhost:8080/mcp")
TASK_PROMPT_NAME = os.environ.get("TASK_PROMPT_NAME", "complete_tasks_prompt")


async def perform_tasks():
    async with streamablehttp_client(MCP_URL) as (
        read_stream,
        write_stream,
        _,
    ):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            prompt = await get_prompt(session, TASK_PROMPT_NAME)
            multitool = await Multitool.create(session)
            conversation = Conversation(tools=multitool.get_tools_json())
            res = conversation.add_message(prompt)
            tool_call = res["tool_call"]
            while tool_call:
                result = await multitool.call_tool(tool_call.name, tool_call.input)
                res = conversation.add_tool_result(
                    tool_call.id, serialize_content_from_mcp(result.content)
                )
                tool_call = res["tool_call"]


def ping(url: str):
    try:
        requests.get(url)
    except requests.exceptions.RequestException:
        return False
    return True


async def run_loop():
    waiting_secs = 0.0
    while True:
        start_time = time.time()
        # Check if MCP server is running
        is_mcp_running = ping(MCP_URL)
        if not is_mcp_running:
            print("\033[A\033[K" + f"Waiting for MCP server... ({int(waiting_secs)}s)")
            await asyncio.sleep(1)
            time_elapsed = time.time() - start_time
            waiting_secs += time_elapsed
        else:
            print("MCP server running, performing tasks...")
            await perform_tasks()
            # Reset waiting time
            waiting_secs = 0.0


async def main():
    await run_loop()


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
