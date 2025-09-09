import re


async def create_data(email, password) -> dict:
    """
    Generate a dictionary with user data to save to the database.

    :param email: User's email
    :param password: User's password
    :return dict: Returns the dict to be sent to the server.
    """
    return {
        "email": email,
        "password": password,
        "re_password": password
    }


def is_valid_password(password: str) -> bool:
    """
    Check the password strength.

    :param password: Password for checking.
    :return bool: Does it match or not
    """
    pattern: str = r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{5,}$'
    return bool(re.match(pattern, password))


def is_valid_email(email: str) -> bool:
    """
    Check the email.

    :param email: Email for checking.
    :return bool: Does it match or not.
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))
