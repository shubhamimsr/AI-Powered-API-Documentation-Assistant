from pathlib import Path

# Root directory that MCP is allowed to access
WORKSPACE_ROOT = Path(
    r"D:\FQTS Projects\GenAI\python code base\Code Files\python-for-genAI"
).resolve()

# Maximum file size to read (5 MB)
MAX_FILE_SIZE = 5 * 1024 * 1024