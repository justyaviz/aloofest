def check_fake(user):

    if user.is_bot:
        return False

    if not user.username:
        return False

    return True
