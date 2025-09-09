from django.contrib.auth.tokens import PasswordResetTokenGenerator
from djoser.email import PasswordResetEmail


class CustomPasswordResetEmail(PasswordResetEmail):
    """
    A class for adding the necessary context
    and replacing the standard message.
    """
    def get_context_data(self) -> dict:
        """Adding the necessary data to the context."""
        context = super().get_context_data()
        user = context.get("user")
        context["uid"] = context.get("uid")
        context["token"] = PasswordResetTokenGenerator()
        context["email"] = user.email if user else ""
        return context
