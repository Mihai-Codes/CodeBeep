# CodeBeep Development Issues

## Current Status
The bot is now successfully communicating through the unencrypted "CodeBeep Shell" room and basic commands like `/status`, `/help`, and `/agents` are working.

## Known Issues

### 1. API Endpoint Issues
- **Problem**: `/plan` and `/build` commands are failing with `'createdAt'` error
- **Status**: IN PROGRESS
- **Details**: The error occurs when attempting to send messages via the async API endpoint. The current implementation tries to use the `/session/{session_id}/message` endpoint with a short timeout but still encounters the error.
- **Possible Causes**:
  - The session creation API response format has changed
  - The message sending endpoint expects different parameters
  - The server response includes unexpected fields causing parsing errors

### 2. Session Creation/Management
- **Problem**: Need to investigate the session creation and management flow
- **Status**: NEEDS INVESTIGATION
- **Details**: The error might stem from how sessions are created or how the session object is constructed from the API response.

## Completed Tasks
- ✅ Fixed E2E encryption issues by creating an unencrypted "CodeBeep Shell" room
- ✅ Fixed bot crashing from system messages by implementing defensive message handling
- ✅ Fixed bot echoing its own messages by implementing proper self-message detection
- ✅ Basic commands (`/status`, `/help`, `/agents`) are working
- ✅ Bot can connect to OpenCode server successfully

## Next Steps
1. Fix the `/plan` and `/build` commands
2. Test the full workflow with actual coding tasks
3. Investigate the `'createdAt'` error in detail
4. Consider implementing better error handling for API responses