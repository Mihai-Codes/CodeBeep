"""OpenCode Server API client."""

from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import dataclass
from typing import Any, AsyncIterator

import httpx

logger = logging.getLogger(__name__)


@dataclass
class Session:
    """Represents an OpenCode session."""

    id: str
    title: str | None
    parent_id: str | None
    created_at: str
    updated_at: str
    share: dict[str, Any] | None = None


@dataclass
class Message:
    """Represents a message in a session."""

    id: str
    session_id: str
    role: str
    created_at: str
    parts: list[dict[str, Any]]


@dataclass
class SessionStatus:
    """Status of a session."""

    session_id: str
    status: str  # "idle", "running", "waiting"
    agent: str | None = None
    model: str | None = None


class OpenCodeClient:
    """Client for interacting with the OpenCode server API."""

    def __init__(
        self,
        base_url: str = "http://127.0.0.1:4096",
        timeout: float = 30.0,
    ) -> None:
        """Initialize the OpenCode client.

        Args:
            base_url: Base URL of the OpenCode server
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create the HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self.timeout,
            )
        return self._client

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def health_check(self) -> dict[str, Any]:
        """Check server health.

        Returns:
            Health status including version
        """
        client = await self._get_client()
        response = await client.get("/global/health")
        response.raise_for_status()
        return response.json()

    async def get_config(self) -> dict[str, Any]:
        """Get server configuration.

        Returns:
            Server configuration
        """
        client = await self._get_client()
        response = await client.get("/config")
        response.raise_for_status()
        return response.json()

    async def list_sessions(self) -> list[Session]:
        """List all sessions.

        Returns:
            List of sessions
        """
        client = await self._get_client()
        response = await client.get("/session")
        response.raise_for_status()
        data = response.json()
        return [
            Session(
                id=s["id"],
                title=s.get("title"),
                parent_id=s.get("parentID"),
                created_at=s["createdAt"],
                updated_at=s["updatedAt"],
                share=s.get("share"),
            )
            for s in data
        ]

    async def get_session_status(self) -> dict[str, SessionStatus]:
        """Get status for all sessions.

        Returns:
            Dictionary mapping session ID to status
        """
        client = await self._get_client()
        response = await client.get("/session/status")
        response.raise_for_status()
        data = response.json()
        return {
            session_id: SessionStatus(
                session_id=session_id,
                status=status.get("status", "idle"),
                agent=status.get("agent"),
                model=status.get("model"),
            )
            for session_id, status in data.items()
        }

    async def create_session(
        self,
        title: str | None = None,
        parent_id: str | None = None,
    ) -> Session:
        """Create a new session.

        Args:
            title: Optional session title
            parent_id: Optional parent session ID

        Returns:
            Created session
        """
        client = await self._get_client()
        body: dict[str, Any] = {}
        if title:
            body["title"] = title
        if parent_id:
            body["parentID"] = parent_id

        response = await client.post("/session", json=body)
        response.raise_for_status()
        s = response.json()
        return Session(
            id=s["id"],
            title=s.get("title"),
            parent_id=s.get("parentID"),
            created_at=s["createdAt"],
            updated_at=s["updatedAt"],
            share=s.get("share"),
        )

    async def get_session(self, session_id: str) -> Session:
        """Get session details.

        Args:
            session_id: Session ID

        Returns:
            Session details
        """
        client = await self._get_client()
        response = await client.get(f"/session/{session_id}")
        response.raise_for_status()
        s = response.json()
        return Session(
            id=s["id"],
            title=s.get("title"),
            parent_id=s.get("parentID"),
            created_at=s["createdAt"],
            updated_at=s["updatedAt"],
            share=s.get("share"),
        )

    async def delete_session(self, session_id: str) -> bool:
        """Delete a session.

        Args:
            session_id: Session ID

        Returns:
            True if deleted successfully
        """
        client = await self._get_client()
        response = await client.delete(f"/session/{session_id}")
        response.raise_for_status()
        return response.json()

    async def abort_session(self, session_id: str) -> bool:
        """Abort a running session.

        Args:
            session_id: Session ID

        Returns:
            True if aborted successfully
        """
        client = await self._get_client()
        response = await client.post(f"/session/{session_id}/abort")
        response.raise_for_status()
        return response.json()

    async def get_messages(
        self,
        session_id: str,
        limit: int | None = None,
    ) -> list[Message]:
        """Get messages in a session.

        Args:
            session_id: Session ID
            limit: Maximum number of messages to return

        Returns:
            List of messages
        """
        client = await self._get_client()
        params = {}
        if limit:
            params["limit"] = limit

        response = await client.get(f"/session/{session_id}/message", params=params)
        response.raise_for_status()
        data = response.json()
        return [
            Message(
                id=m["info"]["id"],
                session_id=m["info"]["sessionID"],
                role=m["info"]["role"],
                created_at=m["info"]["createdAt"],
                parts=m.get("parts", []),
            )
            for m in data
        ]

    async def send_message(
        self,
        session_id: str,
        content: str,
        agent: str | None = None,
        model: str | None = None,
    ) -> Message:
        """Send a message and wait for response.

        Args:
            session_id: Session ID
            content: Message content
            agent: Agent to use (build, plan, etc.)
            model: Model to use

        Returns:
            Response message
        """
        client = await self._get_client()
        body: dict[str, Any] = {
            "parts": [{"type": "text", "text": content}],
        }
        if agent:
            body["agent"] = agent
        if model:
            body["model"] = model

        # Use longer timeout for message processing
        response = await client.post(
            f"/session/{session_id}/message",
            json=body,
            timeout=300.0,  # 5 minutes
        )
        response.raise_for_status()
        m = response.json()
        return Message(
            id=m["info"]["id"],
            session_id=m["info"]["sessionID"],
            role=m["info"]["role"],
            created_at=m["info"]["createdAt"],
            parts=m.get("parts", []),
        )

    async def send_message_async(
        self,
        session_id: str,
        content: str,
        agent: str | None = None,
        model: str | None = None,
    ) -> None:
        """Send a message asynchronously (don't wait for response).

        Args:
            session_id: Session ID
            content: Message content
            agent: Agent to use
            model: Model to use
        """
        client = await self._get_client()
        body: dict[str, Any] = {
            "parts": [{"type": "text", "text": content}],
        }
        if agent:
            body["agent"] = agent
        if model:
            body["model"] = model

        response = await client.post(f"/session/{session_id}/prompt_async", json=body)
        response.raise_for_status()

    async def execute_command(
        self,
        session_id: str,
        command: str,
        arguments: str = "",
        agent: str | None = None,
        model: str | None = None,
    ) -> Message:
        """Execute a slash command.

        Args:
            session_id: Session ID
            command: Command name (without /)
            arguments: Command arguments
            agent: Agent to use
            model: Model to use

        Returns:
            Response message
        """
        client = await self._get_client()
        body: dict[str, Any] = {
            "command": command,
            "arguments": arguments,
        }
        if agent:
            body["agent"] = agent
        if model:
            body["model"] = model

        response = await client.post(
            f"/session/{session_id}/command",
            json=body,
            timeout=300.0,
        )
        response.raise_for_status()
        m = response.json()
        return Message(
            id=m["info"]["id"],
            session_id=m["info"]["sessionID"],
            role=m["info"]["role"],
            created_at=m["info"]["createdAt"],
            parts=m.get("parts", []),
        )

    async def list_agents(self) -> list[dict[str, Any]]:
        """List available agents.

        Returns:
            List of agent definitions
        """
        client = await self._get_client()
        response = await client.get("/agent")
        response.raise_for_status()
        return response.json()

    async def list_commands(self) -> list[dict[str, Any]]:
        """List available commands.

        Returns:
            List of command definitions
        """
        client = await self._get_client()
        response = await client.get("/command")
        response.raise_for_status()
        return response.json()

    async def subscribe_events(self) -> AsyncIterator[dict[str, Any]]:
        """Subscribe to server-sent events.

        Yields:
            Event data dictionaries
        """
        client = await self._get_client()
        async with client.stream("GET", "/event") as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = line[6:]
                    if data:
                        try:
                            yield json.loads(data)
                        except json.JSONDecodeError:
                            logger.warning(f"Failed to parse event: {data}")

    async def get_diff(
        self, session_id: str, message_id: str | None = None
    ) -> list[dict[str, Any]]:
        """Get the diff for a session.

        Args:
            session_id: Session ID
            message_id: Optional message ID to get diff at

        Returns:
            List of file diffs
        """
        client = await self._get_client()
        params = {}
        if message_id:
            params["messageID"] = message_id

        response = await client.get(f"/session/{session_id}/diff", params=params)
        response.raise_for_status()
        return response.json()
