
# Python Logging Tutorial

Logging in Python is a way to track events that happen when software runs.  
It is useful for debugging, monitoring, and auditing applications.

---

## Why Use Logging?
- Provides more control than `print()` statements.
- Allows setting different levels (debug, info, warning, error, critical).
- Can log to files, streams, or external systems.
- Helps in troubleshooting issues in production.

---

## Basic Example

```python
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Example usage
logging.debug("This is a debug message")    # Not shown (level too low)
logging.info("This is an info message")
logging.warning("This is a warning message")
logging.error("This is an error message")
logging.critical("This is a critical message")
```

---

## Logging to a File

```python
import logging

logging.basicConfig(
    filename="app.log",
    filemode="w",  # Overwrites file each time, use "a" to append
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logging.debug("Debug message in file")
logging.info("Info message in file")
logging.error("Error message in file")
```

---

## Custom Logger

```python
import logging

# Create a custom logger
logger = logging.getLogger("my_logger")
logger.setLevel(logging.DEBUG)

# Create handlers
console_handler = logging.StreamHandler()
file_handler = logging.FileHandler("custom.log")

# Set levels
console_handler.setLevel(logging.WARNING)
file_handler.setLevel(logging.DEBUG)

# Create formatters and add them to handlers
formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# Add handlers to the logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)

# Example logs
logger.debug("Debug message")
logger.warning("Warning message")
logger.error("Error message")
```

---

## Logging Levels Recap

- `DEBUG`: Detailed information, useful for diagnosing problems.
- `INFO`: General events, confirming things are working as expected.
- `WARNING`: Something unexpected happened, but program still works.
- `ERROR`: Serious problem, program may not be able to continue.
- `CRITICAL`: Very serious error, program will likely crash.

---

✅ Use logging instead of print statements in production code.
