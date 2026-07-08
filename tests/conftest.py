"""Pytest fixtures shared across all test modules."""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import create_app


@pytest.fixture()
def app():
    return create_app()


@pytest.fixture()
async def client(app):
    """Async HTTP client wired directly to the ASGI app (no real network)."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac
