import os

from mcp.server.fastmcp import FastMCP
from tools.hello import hello
from tools.filesystem import list_files, read_file
from tools.rag import search_api_documentation
from tools.code_generator import generate_api_code

mcp = FastMCP(
    "APIMind MCP Server",
    host="127.0.0.1",
    port=int(os.getenv("MCP_PORT", "9000")),
    json_response=True
)


@mcp.tool()
def hello_tool(name: str = "Developer") -> str:
    """Simple greeting tool."""
    print("======== Running MCP ========")
    return hello(name)


@mcp.tool()
def list_project_files(path: str = ""):
    """List all files inside the configured workspace."""
    return list_files(path)

@mcp.tool()
def read_project_file(path: str):
    """Read a file from the configured workspace."""
    return read_file(path)

@mcp.tool()
def ask_api_documentation(
    question: str,
    source_file: str = ""
):
    """Ask questions about uploaded API documentation."""
    return search_api_documentation(
        question,
        source_file
    )

@mcp.tool()
def generate_code(
    question: str,
    language: str = "python",
    source_file: str = ""
):
    """Generate API integration code."""

    return generate_api_code(
        question,
        language,
        source_file
    )






if __name__ == "__main__":
    print("Running MCP Server...")
    mcp.run(transport="streamable-http")

