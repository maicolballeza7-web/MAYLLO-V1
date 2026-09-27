def read_text(path: str):
    with open(path, "r", encoding="utf-8") as handle:
        return handle.read()


def write_text(path: str, content: str):
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(content)
    return path
