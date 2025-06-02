import uuid

def generate_session_id():
    """
    Generates a unique session ID using UUID4.

    Returns:
        str: A unique session ID as a string.
    """
    return str(uuid.uuid4())