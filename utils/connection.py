from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict
from utils.logger import logger
import asyncio
from starlette.websockets import WebSocketState
import json

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}
        self.connection_states: Dict[int, bool] = {}
        
    async def connect(self, websocket: WebSocket, user_id: int):
        try:
            await self.disconnect(user_id)  # Close existing connection
            await websocket.accept()
            self.active_connections[user_id] = websocket
            self.connection_states[user_id] = True
            logger.info(f"WebSocket connection accepted for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Connection error for user {user_id}: {str(e)}")
            return False

    async def disconnect(self, user_id: int):
        if user_id in self.active_connections:
            try:
                ws = self.active_connections[user_id]
                try:
                    if ws.application_state != WebSocketState.DISCONNECTED:
                        await ws.close()
                except Exception as e:
                    logger.error(f"Error closing WebSocket: {str(e)}")
            except Exception as e:
                logger.error(f"Error during disconnect: {str(e)}")
            finally:
                self.active_connections.pop(user_id, None)
                self.connection_states.pop(user_id, None)

    async def force_disconnect(self, user_id: int) -> bool:
        """Force immediate disconnect"""
        try:
            if user_id in self.active_connections:
                ws = self.active_connections[user_id]
                # Clean up first
                self.active_connections.pop(user_id, None)
                self.connection_states.pop(user_id, None)
                
                # Then close connection
                try:
                    await ws.close(code=1000, reason="Session stopped")
                except:
                    pass
                return True
            return False
        except:
            return False

    def is_connected(self, user_id: int) -> bool:
        return self.connection_states.get(user_id, False)

    async def send_message(self, message: str, user_id: int):
        if user_id in self.active_connections:
            try:
                ws = self.active_connections[user_id]
                if ws.application_state == WebSocketState.CONNECTED:
                    await ws.send_text(message)
            except Exception as e:
                logger.error(f"Error sending message: {str(e)}")
                await self.disconnect(user_id)

# Singleton instance
manager = ConnectionManager()
