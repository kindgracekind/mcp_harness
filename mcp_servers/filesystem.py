from fastmcp import FastMCP


class Filesystem:
    """Dummy filesystem for testing"""

    def __init__(self):
        self.files = {}

    def write(self, path: str, content: str) -> None:
        self.files[path] = content

    def read(self, path: str) -> str:
        return self.files[path]


def get_filesystem_mcp(filesystem: Filesystem | None = None):
    if filesystem is None:
        filesystem = Filesystem()
    mcp = FastMCP("Filesystem")

    @mcp.tool()
    def write(path: str, content: str) -> None:
        """Write a file to the filesystem."""
        filesystem.write(path, content)

    @mcp.tool()
    def read(path: str) -> str:
        """Read a file from the filesystem."""
        return filesystem.read(path)

    return mcp
