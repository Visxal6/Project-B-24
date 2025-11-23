from django import template

register = template.Library()

@register.filter
def get_display_name(user):
    """Return preferred display name for a user object.

    Preference order:
    - user.profile.display_name (if present and non-empty)
    - user.get_full_name() (if non-empty)
    - user.username
    """
    try:
        if hasattr(user, 'profile') and user.profile and getattr(user.profile, 'display_name', None):
            dn = user.profile.display_name
            if dn:
                return dn
    except Exception:
        pass
    try:
        full = user.get_full_name()
        if full:
            return full
    except Exception:
        pass
    try:
        return user.username
    except Exception:
        return ''
