# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
from pathlib import Path
from typing import Any, Dict, List

import yaml

# Backward compatibility constant
SAVED_CHAT_PATH = str(os.getcwd()) + "/.saved_chats"


class ChatProcessor:
    """Centralized chat processing and storage utility.
    
    This class handles text cleaning, message sanitization, and chat persistence
    operations, implementing DRY principles for common chat processing patterns.
    """
    
    def __init__(self, saved_chat_path: str | None = None):
        """Initialize the chat processor with optional custom path.
        
        Args:
            saved_chat_path: Custom path for saving chats. If None, uses default.
        """
        self.saved_chat_path = saved_chat_path or SAVED_CHAT_PATH
    
    def clean_text(self, text: str) -> str:
        """Preprocess the input text by removing leading and trailing newlines.
        
        This method implements consistent text cleaning logic that can be reused
        across different parts of the chat system.
        
        Args:
            text: Input text to clean.
            
        Returns:
            Cleaned text with leading and trailing newlines removed.
        """
        if not text:
            return text

        # Remove leading newlines
        if text.startswith("\n"):
            text = text[1:]
            
        # Remove trailing newlines
        if text.endswith("\n"):
            text = text[:-1]
            
        return text
    
    def sanitize_message_content(self, content: str | List[Dict[str, str]]) -> str | List[Dict[str, str]]:
        """Sanitize individual message content based on its type.
        
        Args:
            content: Message content (string or list of parts).
            
        Returns:
            Sanitized content.
        """
        if isinstance(content, list):
            for part in content:
                if part.get("type") == "text" and "text" in part:
                    part["text"] = self.clean_text(part["text"])
        else:
            content = self.clean_text(content)
        
        return content
    
    def sanitize_messages(
        self,
        messages: List[Dict[str, str | List[Dict[str, str]]]],
    ) -> List[Dict[str, str | List[Dict[str, str]]]]:
        """Preprocess and fix the content of messages.
        
        This method applies consistent text cleaning to all messages in a conversation,
        handling both simple text content and multimodal content lists.
        
        Args:
            messages: List of message dictionaries to sanitize.
            
        Returns:
            List of sanitized message dictionaries.
        """
        for message in messages:
            if "content" in message:
                message["content"] = self.sanitize_message_content(message["content"])
        
        return messages
    
    def ensure_save_directory(self) -> None:
        """Ensure the chat save directory exists."""
        Path(self.saved_chat_path).mkdir(parents=True, exist_ok=True)
    
    def save_chat_session(self, session_data: Dict[str, Any], session_id: str) -> str:
        """Save a chat session to a YAML file.
        
        Args:
            session_data: Session data dictionary containing messages and metadata.
            session_id: Unique identifier for the session.
            
        Returns:
            Path to the saved file.
        """
        self.ensure_save_directory()
        
        # Sanitize messages before saving
        if "messages" in session_data and session_data["messages"]:
            session_data["messages"] = self.sanitize_messages(session_data["messages"])
        
        filename = f"{session_id}.yaml"
        filepath = Path(self.saved_chat_path) / filename
        
        with open(filepath, "w") as file:
            yaml.dump(
                [session_data],
                file,
                allow_unicode=True,
                default_flow_style=False,
                encoding="utf-8",
            )
        
        return str(filepath)
    
    def save_chat(self, st: Any) -> None:
        """Save the current chat session to a YAML file using Streamlit session state.
        
        This method maintains backward compatibility with the existing interface
        while leveraging the new class-based implementation.
        
        Args:
            st: Streamlit module instance with session state.
        """
        session_id = st.session_state["session_id"]
        session = st.session_state.user_chats[session_id]
        messages = session.get("messages", [])
        
        if len(messages) > 0:
            filepath = self.save_chat_session(session, session_id)
            st.toast(f"Chat saved to path: ↓ {filepath}")


# Convenience functions that delegate to a processor using current SAVED_CHAT_PATH
def clean_text(text: str) -> str:
    """Preprocess the input text by removing leading and trailing newlines."""
    processor = ChatProcessor(SAVED_CHAT_PATH)
    return processor.clean_text(text)

def sanitize_messages(
    messages: List[Dict[str, str | List[Dict[str, str]]]],
) -> List[Dict[str, str | List[Dict[str, str]]]]:
    """Preprocess and fix the content of messages."""
    processor = ChatProcessor(SAVED_CHAT_PATH)
    return processor.sanitize_messages(messages)

def save_chat(st: Any) -> None:
    """Save the current chat session to a YAML file."""
    processor = ChatProcessor(SAVED_CHAT_PATH)
    processor.save_chat(st)
