from fastmcp import FastMCP


mcp = FastMCP("Calculator")


@mcp.tool()
def multiply(self, a: int, b: int) -> int:
    """Multiply two numbers"""
    return a * b
