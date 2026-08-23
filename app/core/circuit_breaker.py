import time


class CircuitBreaker:
    def __init__(self, failure_threshold: int = 3, reset_timeout_seconds: int = 30) -> None:
        self.failure_threshold = failure_threshold
        self.reset_timeout_seconds = reset_timeout_seconds
        self.failure_count = 0
        self.opened_at: float | None = None

    def is_open(self) -> bool:
        if self.opened_at is None:
            return False

        elapsed = time.monotonic() - self.opened_at
        if elapsed > self.reset_timeout_seconds:
            # cooldown has passed — move to half-open by clearing opened_at,
            # allowing exactly one request through as a test
            self.opened_at = None
            return False

        return True

    def record_success(self) -> None:
        self.failure_count = 0
        self.opened_at = None

    def record_failure(self) -> None:
        self.failure_count += 1
        if self.failure_count >= self.failure_threshold:
            self.opened_at = time.monotonic()