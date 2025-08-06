"""
Conversation Persistence for FreeCAD AI Addon

Handles saving, loading, and managing conversation history with FreeCAD
context.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any
from dataclasses import asdict
import hashlib

from freecad_ai_addon.ui.conversation_widget import ChatMessage, MessageType
from freecad_ai_addon.utils.logging import get_logger
from freecad_ai_addon.utils.config import get_config_manager

logger = get_logger('conversation_persistence')


class ConversationPersistence:
    """Manages conversation persistence and history"""

    def __init__(self):
        self.config_manager = get_config_manager()
        self.conversations_dir = self._get_conversations_directory()
        self._ensure_directory_exists()

    def _get_conversations_directory(self) -> Path:
        """Get the conversations storage directory"""
        # Get FreeCAD user data directory
        try:
            import FreeCAD as App
            user_data_dir = Path(App.getUserAppDataDir())
        except ImportError:
            # Fallback to home directory if FreeCAD not available
            user_data_dir = Path.home() / ".FreeCAD"

        conversations_dir = user_data_dir / "ai_addon" / "conversations"
        return conversations_dir

    def _ensure_directory_exists(self):
        """Ensure conversations directory exists"""
        self.conversations_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Conversations directory: {self.conversations_dir}")

    def save_conversation(self, conversation_id: str,
                          messages: List[ChatMessage],
                          metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Save conversation to disk"""
        try:
            conversation_data = {
                "id": conversation_id,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "metadata": metadata or {},
                "messages": [self._message_to_dict(msg) for msg in messages]
            }

            # Add FreeCAD context if available
            freecad_context = self._get_freecad_context()
            if freecad_context:
                conversation_data["freecad_context"] = freecad_context

            # Save to file
            filepath = self.conversations_dir / f"{conversation_id}.json"
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(conversation_data, f, indent=2, ensure_ascii=False)

            logger.info(f"Saved conversation {conversation_id} to {filepath}")
            return True

        except Exception as e:
            logger.error(f"Failed to save conversation {conversation_id}: {e}")
            return False

    def load_conversation(self, conversation_id: str) -> Optional[
            Dict[str, Any]]:
        """Load conversation from disk"""
        try:
            filepath = self.conversations_dir / f"{conversation_id}.json"
            if not filepath.exists():
                logger.warning(f"Conversation file not found: {filepath}")
                return None

            with open(filepath, 'r', encoding='utf-8') as f:
                conversation_data = json.load(f)

            # Convert message dicts back to ChatMessage objects
            messages = [
                self._dict_to_message(msg_dict)
                for msg_dict in conversation_data.get("messages", [])
            ]
            conversation_data["messages"] = messages

            logger.info(f"Loaded conversation {conversation_id}")
            return conversation_data

        except Exception as e:
            logger.error(f"Failed to load conversation {conversation_id}: {e}")
            return None

    def list_conversations(self) -> List[Dict[str, Any]]:
        """List all saved conversations with metadata"""
        conversations = []

        try:
            for filepath in self.conversations_dir.glob("*.json"):
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)

                    # Extract summary information
                    message_count = len(data.get("messages", []))
                    last_message = None
                    if message_count > 0:
                        last_msg = data["messages"][-1]
                        last_message = last_msg.get("content", "")[:100]

                    conversation_info = {
                        "id": data.get("id", filepath.stem),
                        "created_at": data.get("created_at"),
                        "updated_at": data.get("updated_at"),
                        "message_count": message_count,
                        "last_message_preview": last_message,
                        "metadata": data.get("metadata", {})
                    }
                    conversations.append(conversation_info)

                except Exception as e:
                    logger.warning(f"Failed to read conversation {filepath}: {e}")
                    continue

            # Sort by updated_at (newest first)
            conversations.sort(
                key=lambda x: x.get("updated_at", ""),
                reverse=True
            )

        except Exception as e:
            logger.error(f"Failed to list conversations: {e}")

        return conversations

    def delete_conversation(self, conversation_id: str) -> bool:
        """Delete conversation from disk"""
        try:
            filepath = self.conversations_dir / f"{conversation_id}.json"
            if filepath.exists():
                filepath.unlink()
                logger.info(f"Deleted conversation {conversation_id}")
                return True
            else:
                logger.warning(f"Conversation {conversation_id} not found")
                return False

        except Exception as e:
            logger.error(f"Failed to delete conversation {conversation_id}: {e}")
            return False

    def export_conversation(self, conversation_id: str,
                          export_format: str = "markdown") -> Optional[str]:
        """Export conversation to different formats"""
        conversation = self.load_conversation(conversation_id)
        if not conversation:
            return None

        if export_format.lower() == "markdown":
            return self._export_to_markdown(conversation)
        elif export_format.lower() == "json":
            return json.dumps(conversation, indent=2, ensure_ascii=False)
        elif export_format.lower() == "text":
            return self._export_to_text(conversation)
        else:
            logger.error(f"Unsupported export format: {export_format}")
            return None

    def search_conversations(self, query: str) -> List[Dict[str, Any]]:
        """Search conversations by content"""
        matching_conversations = []
        query_lower = query.lower()

        for conv_info in self.list_conversations():
            conversation = self.load_conversation(conv_info["id"])
            if not conversation:
                continue

            # Search in message content
            for message in conversation["messages"]:
                if query_lower in message.get("content", "").lower():
                    matching_conversations.append(conv_info)
                    break

        return matching_conversations

    def create_conversation_id(self, first_message: str = "") -> str:
        """Create unique conversation ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Add hash of first message for uniqueness
        if first_message:
            message_hash = hashlib.md5(
                first_message.encode('utf-8')
            ).hexdigest()[:8]
            return f"conv_{timestamp}_{message_hash}"
        else:
            return f"conv_{timestamp}"

    def _message_to_dict(self, message: ChatMessage) -> Dict[str, Any]:
        """Convert ChatMessage to dictionary for JSON serialization"""
        msg_dict = asdict(message)
        # Convert enum to string
        msg_dict["type"] = message.type.value
        # Convert datetime to ISO string
        msg_dict["timestamp"] = message.timestamp.isoformat()
        return msg_dict

    def _dict_to_message(self, msg_dict: Dict[str, Any]) -> ChatMessage:
        """Convert dictionary back to ChatMessage object"""
        # Convert string back to enum
        msg_dict["type"] = MessageType(msg_dict["type"])
        # Convert ISO string back to datetime
        msg_dict["timestamp"] = datetime.fromisoformat(msg_dict["timestamp"])
        return ChatMessage(**msg_dict)

    def _get_freecad_context(self) -> Optional[Dict[str, Any]]:
        """Get current FreeCAD context for conversation"""
        try:
            import FreeCAD as App

            if not App.ActiveDocument:
                return None

            context = {
                "document_name": App.ActiveDocument.Name,
                "document_label": App.ActiveDocument.Label,
                "object_count": len(App.ActiveDocument.Objects),
                "objects": []
            }

            # Get basic info about objects
            for obj in App.ActiveDocument.Objects[:10]:  # Limit to first 10
                obj_info = {
                    "name": obj.Name,
                    "label": obj.Label,
                    "type": obj.TypeId
                }

                # Add geometric info if available
                if hasattr(obj, 'Shape') and obj.Shape:
                    obj_info["volume"] = obj.Shape.Volume
                    obj_info["surface_area"] = obj.Shape.Area

                context["objects"].append(obj_info)

            return context

        except ImportError:
            return None
        except Exception as e:
            logger.warning(f"Failed to get FreeCAD context: {e}")
            return None

    def _export_to_markdown(self, conversation: Dict[str, Any]) -> str:
        """Export conversation to markdown format"""
        lines = []

        # Header
        lines.append(f"# Conversation: {conversation.get('id', 'Unknown')}")
        lines.append(f"**Created:** {conversation.get('created_at', 'Unknown')}")
        lines.append(f"**Updated:** {conversation.get('updated_at', 'Unknown')}")
        lines.append("")

        # FreeCAD context if available
        if "freecad_context" in conversation:
            ctx = conversation["freecad_context"]
            lines.append("## FreeCAD Context")
            lines.append(f"- **Document:** {ctx.get('document_name', 'N/A')}")
            lines.append(f"- **Objects:** {ctx.get('object_count', 0)}")
            lines.append("")

        # Messages
        lines.append("## Conversation")
        lines.append("")

        for message in conversation["messages"]:
            # Message header
            msg_type = message.get("type", "unknown")
            timestamp = message.get("timestamp", "")
            lines.append(f"### {msg_type.title()}")
            lines.append(f"*{timestamp}*")
            lines.append("")

            # Message content
            content = message.get("content", "")
            lines.append(content)
            lines.append("")
            lines.append("---")
            lines.append("")

        return "\n".join(lines)

    def _export_to_text(self, conversation: Dict[str, Any]) -> str:
        """Export conversation to plain text format"""
        lines = []

        # Header
        lines.append(f"Conversation: {conversation.get('id', 'Unknown')}")
        lines.append(f"Created: {conversation.get('created_at', 'Unknown')}")
        lines.append(f"Updated: {conversation.get('updated_at', 'Unknown')}")
        lines.append("=" * 60)
        lines.append("")

        # Messages
        for i, message in enumerate(conversation["messages"], 1):
            msg_type = message.get("type", "unknown")
            timestamp = message.get("timestamp", "")
            content = message.get("content", "")

            lines.append(f"[{i}] {msg_type.upper()} - {timestamp}")
            lines.append("-" * 40)
            lines.append(content)
            lines.append("")

        return "\n".join(lines)


# Global instance
_persistence_instance = None


def get_conversation_persistence() -> ConversationPersistence:
    """Get global conversation persistence instance"""
    global _persistence_instance
    if _persistence_instance is None:
        _persistence_instance = ConversationPersistence()
    return _persistence_instance
