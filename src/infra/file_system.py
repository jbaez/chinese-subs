from io import TextIOWrapper


class FileSystem:
    def open(self, file: str, encoding='utf-8') -> TextIOWrapper:
        return open(file=file, encoding=encoding)

    def read(self, path: str) -> str:
        return self.open(path).read()

    def write(self, path: str, content: str) -> None:
        with open(path, 'w') as f:
            f.write(content)