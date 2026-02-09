"""Main bot implementation for codebeep."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from nio import InviteMemberEvent, MegolmEvent, RoomMessageText, Event, RoomPreset
import simplematrixbotlib as botlib

from codebeep.commands import ALL_COMMANDS, Command, CommandResult
from codebeep.config import Config
from codebeep.opencode_client import OpenCodeClient, Session

logger = logging.getLogger(__name__)


class CodeBeepBot:
    """Matrix bot that integrates with OpenCode for mobile coding tasks."""

    def __init__(self, config: Config) -> None:
        """Initialize the bot.

        Args:
            config: Bot configuration
        """
        self.config = config
        self.opencode = OpenCodeClient(
            base_url=config.opencode.server_url,
        )

        # Set up Matrix credentials
        self.creds = botlib.Creds(
            homeserver=config.matrix.homeserver,
            username=config.matrix.username,
            password=config.matrix.password,
            access_token=config.matrix.access_token,
        )

        # Bot configuration
        bot_config = botlib.Config()
        bot_config.emoji_verify = True
        bot_config.ignore_unverified_devices = True
        bot_config.store_path = ".codebeep_store"

        self.bot = botlib.Bot(self.creds, bot_config)

        # Register commands
        self.commands: dict[str, Command] = {}
        for cmd_class in ALL_COMMANDS:
            cmd = cmd_class()
            self.commands[cmd.name] = cmd
            # Also register aliases
            for alias in cmd.aliases:
                self.commands[alias] = cmd

        # State
        self.current_model: str | None = None
        self.active_session: Session | None = None
        self._event_task: asyncio.Task[None] | None = None

    async def get_or_create_session(self) -> Session:
        """Get the active session or create a new one.

        Returns:
            Active or new session
        """
        if self.active_session is not None:
            # Verify session still exists
            try:
                session = await self.opencode.get_session(self.active_session.id)
                return session
            except Exception:
                self.active_session = None

        # Create new session
        self.active_session = await self.opencode.create_session(title="codebeep mobile session")
        return self.active_session

    def is_user_allowed(self, user_id: str) -> bool:
        """Check if a user is allowed to interact with the bot.

        Args:
            user_id: Matrix user ID

        Returns:
            True if allowed
        """
        allowed = self.config.matrix.allowed_users
        if not allowed:
            return True  # No restrictions
        return user_id in allowed

    async def handle_message(self, room: Any, event: Any) -> None:
        """Handle incoming messages.

        Args:
            room: Matrix room
            event: Message event
        """
        # Defensive checks
        if not hasattr(event, "sender") or not event.sender:
            logger.info(f"DEBUG: Event has no sender, ignoring")
            return

        logger.info(f"DEBUG: handle_message called for room {room.room_id} from {event.sender}")

        # Extract message body from event
        body = (
            event.body
            if hasattr(event, "body")
            else event.source.get("content", {}).get("body", "")
        )
        sender = event.sender

        # Check if message has content
        if not body:
            logger.info(f"DEBUG: Message has no body, ignoring")
            return

        # Use MessageMatch to check if message is from bot
        try:
            match = botlib.MessageMatch(room, event, self.bot, self.config.bot.prefix)
            if not match.is_not_from_this_bot():
                logger.info(f"DEBUG: Message from bot itself, ignoring")
                return
        except Exception as e:
            logger.warning(f"DEBUG: MessageMatch error: {e}, falling back to manual check")
            # Fallback: manually check if sender is the bot
            if sender == self.config.matrix.username:
                logger.info(f"DEBUG: Message from bot itself (manual check), ignoring")
                return

        logger.info(f"DEBUG: Processing message from {sender}: '{body}'")

        # Check if user is allowed
        if not self.is_user_allowed(sender):
            logger.warning(f"Unauthorized user attempted to use bot: {sender}")
            return

        # Check for command prefix
        if not body.startswith(self.config.bot.prefix):
            return

        # Parse command
        parts = body[len(self.config.bot.prefix) :].split(maxsplit=1)
        if not parts:
            return

        cmd_name = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""

        # Find and execute command
        cmd = self.commands.get(cmd_name)
        if cmd is None:
            if self.config.bot.unknown_command_reply:
                await self.bot.api.send_text_message(
                    room.room_id,
                    f"Unknown command: {cmd_name}\nUse /help to see available commands.",
                )
            return

        # Show typing indicator
        if self.config.bot.typing_indicator:
            await self.bot.api.async_client.room_typing(room.room_id, True)

        try:
            result = await cmd.execute(self, args)
            await self._send_result(room.room_id, result)
        except Exception as e:
            logger.exception(f"Error executing command {cmd_name}")
            await self.bot.api.send_text_message(
                room.room_id,
                f"Error executing command: {e}",
            )
        finally:
            if self.config.bot.typing_indicator:
                await self.bot.api.async_client.room_typing(room.room_id, False)

    async def _send_result(self, room_id: str, result: CommandResult) -> None:
        """Send a command result to a room.

        Args:
            room_id: Room ID
            result: Command result
        """
        message = result.message

        # Split long messages
        max_len = self.config.bot.max_message_length
        if len(message) > max_len:
            parts = [message[i : i + max_len] for i in range(0, len(message), max_len)]
            for part in parts:
                await self.bot.api.send_markdown_message(room_id, part)
        else:
            await self.bot.api.send_markdown_message(room_id, message)

    async def _monitor_events(self) -> None:
        """Monitor OpenCode events and notify users of completions."""
        try:
            async for event in self.opencode.subscribe_events():
                event_type = event.get("type", "")

                # Handle session completion events
                if event_type == "session.message":
                    session_id = event.get("sessionID")
                    message_data = event.get("message", {})
                    role = message_data.get("info", {}).get("role")

                    if role == "assistant":
                        # Task completed, notify user
                        # TODO: Track which room to notify
                        logger.info(f"Session {session_id} completed")

        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.exception(f"Error monitoring events: {e}")

    async def start(self) -> None:
        """Start the bot."""
        logger.info("Starting codebeep bot...")

        # Verify OpenCode connection
        try:
            health = await self.opencode.health_check()
            logger.info(f"Connected to OpenCode server: {health.get('version', 'unknown')}")
        except Exception as e:
            logger.error(f"Failed to connect to OpenCode server: {e}")
            raise

        # Run the bot
        logger.info("Bot is running. Waiting for messages...")
        await self.bot.api.login()

        # Register message handler
        async def on_message(room: Any, event: Any) -> None:
            await self.handle_message(room, event)

        self.bot.api.async_client.add_event_callback(on_message, RoomMessageText)

        # Register invite handler
        async def on_invite(room: Any, event: Any) -> None:
            if not isinstance(event, InviteMemberEvent):
                return
            sender = event.sender
            if self.is_user_allowed(sender):
                logger.info(f"Joining room {room.room_id} invited by {sender}")
                await self.bot.api.async_client.join(room.room_id)
            else:
                logger.warning(f"Ignoring invite from {sender} to {room.room_id}")

        self.bot.api.async_client.add_event_callback(on_invite, InviteMemberEvent)

        # Debug: Log encrypted events
        async def on_encrypted(room: Any, event: MegolmEvent) -> None:
            logger.info(f"DEBUG: Received Encrypted Event in {room.room_id} from {event.sender}")

        self.bot.api.async_client.add_event_callback(on_encrypted, MegolmEvent)

        # Debug: Log decrypted text events
        async def on_text_debug(room: Any, event: RoomMessageText) -> None:
            logger.info(
                f"DEBUG: Received Decrypted Text in {room.room_id} from {event.sender}: '{event.body}'"
            )

        self.bot.api.async_client.add_event_callback(on_text_debug, RoomMessageText)

        # Start event monitoring
        self._event_task = asyncio.create_task(self._monitor_events())

        # Bootstrap: Create unencrypted room
        try:
            logger.info("Bootstrapping: Creating CodeBeep Shell room...")
            # Create room without encryption
            resp = await self.bot.api.async_client.room_create(
                name="CodeBeep Shell",
                topic="Unencrypted command shell for CodeBeep",
                preset=RoomPreset.private_chat,
            )
            # Log result
            logger.info(f"Room create response: {resp}")
            room_id = resp.room_id
            logger.info(f"Created room: {room_id}")

            # Create room alias for easier joining
            alias = "#codebeep-shell:matrix.org"
            logger.info(f"Setting room alias: {alias}")
            alias_resp = await self.bot.api.async_client.room_put_alias(
                room_alias=alias, room_id=room_id
            )
            logger.info(f"Alias response: {alias_resp}")

            # Log matrix.to link
            logger.info(f"==================================================")
            logger.info(f"JOIN LINK: https://matrix.to/#/{alias}")
            logger.info(f"ROOM ID: {room_id}")
            logger.info(f"==================================================")

            # Explicitly invite the user
            logger.info(f"Inviting @mihai-chindris:beeper.com to room {room_id}...")
            invite_resp = await self.bot.api.async_client.room_invite(
                room_id=room_id, user_id="@mihai-chindris:beeper.com"
            )
            logger.info(f"Invite response: {invite_resp}")
        except Exception as e:
            logger.error(f"Bootstrap error: {e}")

        await self.bot.api.async_client.sync_forever(timeout=30000)

    async def stop(self) -> None:
        """Stop the bot."""
        logger.info("Stopping codebeep bot...")

        if self._event_task:
            self._event_task.cancel()
            try:
                await self._event_task
            except asyncio.CancelledError:
                pass

        await self.opencode.close()
        logger.info("Bot stopped.")


async def run_bot(config: Config) -> None:
    """Run the bot with the given configuration.

    Args:
        config: Bot configuration
    """
    bot = CodeBeepBot(config)
    try:
        await bot.start()
    except KeyboardInterrupt:
        pass
    finally:
        await bot.stop()
