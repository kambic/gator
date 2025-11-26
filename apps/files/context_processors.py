from config.version import VERSION


def stuff(request):
    """Pass settings to the frontend"""
    ret = {}

    ret["RSS_URL"] = "/rss"
    ret["VERSION"] = VERSION

    if request.user.is_superuser:
        ret["DJANGO_ADMIN_URL"] = "admin/"

    return ret
