class SynthesixError(Exception):
    """Base exception for application-level Synthesix failures."""


class BrowserSessionError(SynthesixError):
    def __init__(self, message: str, *, url: str | None = None, original_error: Exception | None = None):
        super().__init__(message)
        self.url = url
        self.original_error = original_error


class SearchEngineError(SynthesixError):
    def __init__(
        self,
        engine_name: str,
        message: str,
        *,
        query: str | None = None,
        url: str | None = None,
        original_error: Exception | None = None,
        engine_errors: dict[str, Exception] | None = None,
    ):
        super().__init__(message)
        self.engine_name = engine_name
        self.query = query
        self.url = url
        self.original_error = original_error
        self.engine_errors = engine_errors or {}


class RobotChallengeError(SearchEngineError):
    def __init__(
        self,
        engine_name: str,
        message: str,
        *,
        query: str | None = None,
        url: str | None = None,
        captured_artifacts: dict | None = None,
    ):
        super().__init__(engine_name, message, query=query, url=url)
        self.captured_artifacts = captured_artifacts or {}
