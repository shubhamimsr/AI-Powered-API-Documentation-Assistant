# from pathlib import Path


# def hello(name: str = "Shubham") -> str:
#     return f"Hello {name}, welcome to APIMind MCP Server!"


# def list_files(path: str):

#     root = Path(path)

#     if not root.exists():
#         return {
#             "success": False,
#             "message": "Directory does not exist."
#         }

#     files = []

#     for item in root.rglob("*"):

#         if item.is_file():

#             files.append(
#                 str(item.relative_to(root))
#             )

#     return {
#         "success": True,
#         "count": len(files),
#         "files": files
#     }