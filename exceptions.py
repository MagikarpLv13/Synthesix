class SynthesixError(Exception):
    """Base exception for application-level Synthesix failures."""


class InvestigationError(SynthesixError):
    """Base exception for investigation storage and workflow failures."""


class EvidenceCaptureError(InvestigationError):
    """Raised when an evidence artifact cannot be captured or persisted."""


class UrlAnalysisError(InvestigationError):
    """Raised when a saved URL cannot be analyzed safely."""


class InvestigationValidationError(InvestigationError):
    """Raised when investigation input does not satisfy application rules."""


class InvestigationNotFoundError(InvestigationError):
    def __init__(self, investigation_id: str):
        super().__init__(f"Investigation not found: {investigation_id}")
        self.investigation_id = investigation_id


class InvestigationHasDataError(InvestigationError):
    def __init__(
        self,
        investigation_id: str,
        *,
        search_count: int,
        result_count: int,
    ):
        super().__init__(
            "Investigation contains search data and must be archived instead of deleted."
        )
        self.investigation_id = investigation_id
        self.search_count = search_count
        self.result_count = result_count


class InvestigationResultNotFoundError(InvestigationError):
    def __init__(self, investigation_id: str, result_id: str):
        super().__init__(
            f"Result {result_id} is not attached to investigation {investigation_id}."
        )
        self.investigation_id = investigation_id
        self.result_id = result_id


class SearchRunNotFoundError(InvestigationError):
    def __init__(self, search_run_id: str):
        super().__init__(f"Search run not found: {search_run_id}")
        self.search_run_id = search_run_id


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
