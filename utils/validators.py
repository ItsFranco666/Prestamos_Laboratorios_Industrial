from datetime import datetime

def is_not_empty(value: str) -> bool:
    """Checks if a string is not empty and not just whitespace."""
    return bool(value and value.strip())

def is_integer(value: str) -> bool:
    """Checks if a string can be converted to an integer."""
    if not value:
        return False
    try:
        int(value)
        return True
    except ValueError:
        return False

def is_positive_integer(value: str) -> bool:
    """Checks if a string represents a positive integer."""
    if not is_integer(value):
        return False
    return int(value) > 0

def is_valid_code(value: str, length: int = None) -> bool:
    """Checks if a code is alphanumeric and optionally of a specific length."""
    if not is_not_empty(value):
        return False
    if not value.isalnum(): # Basic check, can be more specific
        return False
    if length is not None and len(value) != length:
        return False
    return True

def is_valid_datetime_format(date_string: str, fmt: str = "%Y-%m-%d %H:%M:%S") -> bool:
    """Checks if a string matches a datetime format."""
    try:
        datetime.strptime(date_string, fmt)
        return True
    except ValueError:
        return False

def is_valid_id(value: str, length: int = None) -> bool:
    """ Comprueba que una identificacion sea correcta """
    if not is_not_empty(value):
        return False
    try:
        # Try to convert to integer
        int_value = int(value)
        # Check if it's exactly 11 digits
        if len(value) != 11:
            return False
        return True
    except ValueError:
        # If conversion to int fails, it's not a valid number
        return False

def is_valid_time_format(time_string: str, fmt: str = "%H:%M:%S") -> bool:
    """Checks if a string matches a time format."""
    try:
        datetime.strptime(time_string, fmt)
        return True
    except ValueError:
        return False

# Example usage (optional, for testing):
if __name__ == '__main__':
    print(f"'  ': {is_not_empty('  ')}")  # False
    print(f"'Test': {is_not_empty('Test')}") # True
    print(f"'123': {is_integer('123')}") # True
    print(f"'abc': {is_integer('abc')}") # False
    print(f"'-5': {is_positive_integer('-5')}") # False
    print(f"'5': {is_positive_integer('5')}") # True
    print(f"'CODE1': {is_valid_code('CODE1')}") # True
    print(f"'CO DE': {is_valid_code('CO DE')}") # False
    print(f"'2023-01-01 10:00:00': {is_valid_datetime_format('2023-01-01 10:00:00')}") # True
    print(f"'10:00': {is_valid_time_format('10:00', '%H:%M')}") # True
