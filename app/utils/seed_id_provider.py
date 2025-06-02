import uuid


def generate_seed_id():
    """
    Generates a unique seed ID using UUID4.

    Returns:
        str: A unique seed ID as a string.
    """
    return str(uuid.uuid4())