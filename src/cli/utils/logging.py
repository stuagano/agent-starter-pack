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

import sys
from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar, cast

from rich.console import Console

F = TypeVar("F", bound=Callable[..., Any])


class CLILogger:
    """Centralized CLI logging and error handling utility.
    
    This class provides consistent error handling and display formatting
    for CLI operations, implementing DRY principles for common logging patterns.
    """
    
    def __init__(self, console: Console | None = None):
        """Initialize the CLI logger with an optional console instance.
        
        Args:
            console: Rich console instance for output formatting. 
                    If None, creates a new instance.
        """
        self.console = console or Console()
    
    def print_info(self, message: str, style: str = "bold blue") -> None:
        """Print an informational message with consistent styling."""
        self.console.print(message, style=style)
    
    def print_success(self, message: str, style: str = "bold green") -> None:
        """Print a success message with consistent styling."""
        self.console.print(message, style=style)
    
    def print_warning(self, message: str, style: str = "bold yellow") -> None:
        """Print a warning message with consistent styling."""
        self.console.print(message, style=style)
    
    def print_error(self, message: str, style: str = "bold red") -> None:
        """Print an error message with consistent styling."""
        self.console.print(message, style=style)
    
    def handle_cli_error(self, f: F) -> F:
        """Decorator to handle CLI errors gracefully.

        Wraps CLI command functions to catch any exceptions and display them nicely
        to the user before exiting with a non-zero status code.

        Args:
            f: The CLI command function to wrap

        Returns:
            The wrapped function that handles errors
        """
        @wraps(f)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return f(*args, **kwargs)
            except KeyboardInterrupt:
                self.print_warning("\nOperation cancelled by user")
                sys.exit(130)  # Standard exit code for Ctrl+C
            except Exception as e:
                self.print_error(f"Error: {e!s}")
                sys.exit(1)

        return cast(F, wrapper)


# Global instance for backward compatibility
_default_logger = CLILogger()

# Convenience functions that delegate to the default logger
def handle_cli_error(f: F) -> F:
    """Decorator to handle CLI errors gracefully using the default logger."""
    return _default_logger.handle_cli_error(f)

def print_info(message: str, style: str = "bold blue") -> None:
    """Print an informational message using the default logger."""
    _default_logger.print_info(message, style)

def print_success(message: str, style: str = "bold green") -> None:
    """Print a success message using the default logger."""
    _default_logger.print_success(message, style)

def print_warning(message: str, style: str = "bold yellow") -> None:
    """Print a warning message using the default logger."""
    _default_logger.print_warning(message, style)

def print_error(message: str, style: str = "bold red") -> None:
    """Print an error message using the default logger."""
    _default_logger.print_error(message, style)
