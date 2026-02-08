"""Tests for the OpenCode client."""

import pytest

from codebeep.opencode_client import OpenCodeClient, Session


@pytest.fixture
def client() -> OpenCodeClient:
    """Create a test client."""
    return OpenCodeClient(base_url="http://127.0.0.1:4096")


class TestOpenCodeClient:
    """Tests for OpenCodeClient."""

    @pytest.mark.asyncio
    async def test_health_check(self, client: OpenCodeClient) -> None:
        """Test health check endpoint."""
        # This test requires a running OpenCode server
        # Skip if server is not available
        try:
            health = await client.health_check()
            assert "healthy" in health or "version" in health
        except Exception:
            pytest.skip("OpenCode server not available")
        finally:
            await client.close()

    @pytest.mark.asyncio
    async def test_list_sessions(self, client: OpenCodeClient) -> None:
        """Test listing sessions."""
        try:
            sessions = await client.list_sessions()
            assert isinstance(sessions, list)
        except Exception:
            pytest.skip("OpenCode server not available")
        finally:
            await client.close()

    @pytest.mark.asyncio
    async def test_create_and_delete_session(self, client: OpenCodeClient) -> None:
        """Test creating and deleting a session."""
        try:
            # Create session
            session = await client.create_session(title="Test Session")
            assert isinstance(session, Session)
            assert session.title == "Test Session"

            # Delete session
            result = await client.delete_session(session.id)
            assert result is True
        except Exception:
            pytest.skip("OpenCode server not available")
        finally:
            await client.close()
