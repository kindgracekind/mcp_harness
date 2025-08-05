from mcp import ClientSession
from fastmcp import FastMCP
import uvicorn
import threading
import time
from mcp.types import Tool


# https://github.com/encode/uvicorn/discussions/1103
class StoppableServer(uvicorn.Server):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.thread = None

    def install_signal_handlers(self):
        pass

    def start(self):
        thread = threading.Thread(target=self.run)
        thread.start()
        while not self.started:
            time.sleep(1e-3)

    def stop(self):
        self.should_exit = True
        if self.thread:
            self.thread.join()
        # There's probably a better way to do this
        time.sleep(1)


def run_mcp_server(mcp_server, port, verbose=False):
    server = StoppableServer(
        config=uvicorn.Config(
            mcp_server.http_app(),
            host="127.0.0.1",
            port=port,
            log_level="critical" if not verbose else "info",
        )
    )
    server.start()
    print("MCP server running on port", port)
    return server


def compose_mcp_servers(*mcp_servers):
    mcp = FastMCP("Composed")
    for server in mcp_servers:
        mcp.mount(server)
    return mcp


def serialize_content_from_mcp(content):
    res = []
    for block in content:
        content = block.model_dump()
        del content["annotations"]
        del content["meta"]
        res.append(content)
    return res


async def get_prompt(session: ClientSession, prompt_name: str) -> str:
    res = await session.get_prompt(prompt_name)
    return res.messages[0].content.text  # type: ignore


class Multitool:
    """Helper to manage tools from multiple MCP servers."""

    sessions: list[ClientSession]
    tools: list[Tool]
    tools_by_session: dict[ClientSession, list[Tool]]

    def __init__(self):
        pass

    @classmethod
    async def create(cls, *sessions: ClientSession):
        self = cls()
        self.tools = []
        self.tools_by_session = {}
        for session in sessions:
            tools = (await session.list_tools()).tools
            for t in tools:
                if not t.description:
                    raise ValueError(f"Tool {t.name} has no description")
            self.tools.extend(tools)
            self.tools_by_session[session] = tools
        return self

    def get_tools_json(self):
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "input_schema": clean_schema(tool.inputSchema),
            }
            for tool in self.tools
        ]

    def get_session_for_tool(self, tool_name):
        for session, tools in self.tools_by_session.items():
            if tool_name in [tool.name for tool in tools]:
                return session
        raise ValueError(f"Tool {tool_name} not found")

    async def call_tool(self, tool_name, arguments):
        session = self.get_session_for_tool(tool_name)
        return await session.call_tool(tool_name, arguments)


# Clean up JSON schema to remove unsupported properties
def clean_schema(schema):
    if isinstance(schema, dict):
        schema_copy = schema.copy()
        if "additionalProperties" in schema_copy:
            del schema_copy["additionalProperties"]
        if "$schema" in schema_copy:
            del schema_copy["$schema"]
        if "title" in schema_copy:
            del schema_copy["title"]

        # Recursively clean nested properties
        for key, value in schema_copy.items():
            if isinstance(value, (dict, list)):
                schema_copy[key] = clean_schema(value)
        return schema_copy
    elif isinstance(schema, list):
        return [clean_schema(item) for item in schema]
    else:
        return schema


async def get_tools_schema(session: ClientSession) -> dict:
    tools = await session.list_tools()
    return {
        tool.name: {
            "input_schema": clean_schema(tool.inputSchema),
            "output_schema": clean_schema(tool.outputSchema),
        }
        for tool in tools.tools
    }
