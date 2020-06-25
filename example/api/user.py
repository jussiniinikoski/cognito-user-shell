import getpass
import re


class PasswordValidationError(ValueError):
    """Generic password validation error."""


def validate_new_password(password):
    """Validate new password."""
    if len(password) < 8:
        raise PasswordValidationError("Password should contain at least 8 characters")
    elif re.search('[0-9]', password) is None:
        raise PasswordValidationError("Password should contain at least one number")
    elif re.search('[A-Z]', password) is None:
        raise PasswordValidationError("Password should contain at least one capital letter")
    return True


def change_password(client):
    """Change user password."""
    old_password = getpass.getpass("Enter old password: ")
    new_password = getpass.getpass("Enter new password: ")
    if new_password == "":
        return
    new_password2 = getpass.getpass("Type password again: ")
    if new_password != new_password2:
        print("Error. Passwords did not match.")
        return
    try:
        validate_new_password(new_password)
    except PasswordValidationError as e:
        print(e)
        return
    try:
        _aws_resp = client.aws_client.change_password(
            PreviousPassword=old_password,
            ProposedPassword=new_password,
            AccessToken=client.access_token,
        )
    except client.aws_client.exceptions.InvalidPasswordException:
        print("Error. Invalid password.")
    else:
        print("Password Changed.")
