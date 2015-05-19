"""EdX Branding API

Provides a way to retrieve "branded" parts of the site,
such as the site footer.

This information exposed to:
1) Templates in the LMS.
2) Consumers of the branding API.

This ensures that branded UI elements such as the footer
are consistent across the LMS and other sites (such as
the marketing site and blog).

"""
import logging

from django.conf import settings
from django.utils.translation import ugettext as _
from staticfiles.storage import staticfiles_storage

from microsite_configuration import microsite
from edxmako.shortcuts import marketing_link

log = logging.getLogger("edx.footer")


def get_base_url(is_secure=True):
    """Retrieve the base URL for the API, including the protocol and domain.

    Keyword Arguments:
        is_secure (bool): If True, use https:// in URLs.

    Returns: unicode

    """
    return _absolute_url(is_secure, "")


def get_footer(is_secure=True):
    """Retrieve information used to render the footer.

    This will handle both the OpenEdX and EdX.org versions
    of the footer.  All user-facing text is internationalized.

    Currently, this does NOT support theming.

    Keyword Arguments:
        is_secure (bool): If True, use https:// in URLs.

    Returns: dict

    Example:
    >>> get_footer()
    {
        "copyright": "(c) 2015 EdX Inc",
        "logo_image": "http://www.example.com/logo.png",
        "social_links": [
            {
                "name": "facebook",
                "title": "Facebook",
                "url": "http://www.facebook.com/example",
                "icon-class": "fa-facebook-square"
            },
            ...
        ],
        "navigation_links": [
            {
                "name": "about",
                "title": "About",
                "url": "http://www.example.com/about.html"
            },
            ...
        ],
        "mobile_links": [
            {
                "name": "apple",
                "title": "Apple",
                "url": "http://store.apple.com/example_app"
                "image": "http://example.com/static/apple_logo.png"
            },
            ...
        ],
        "legal_links": [
            {
                "url": "http://example.com/terms-of-service.html",
                "name": "terms_of_service",
                "title': "Terms of Service"
            },
            # ...
        ],
        "openedx_link": {
            "url": "http://open.edx.org",
            "title": "Powered by Open edX",
            "image": "http://example.com/openedx.png"
        }
    }

    """
    return {
        "copyright": _footer_copyright(),
        "logo_image": _footer_logo_img(is_secure),
        "social_links": _footer_social_links(),
        "navigation_links": _footer_navigation_links(),
        "mobile_links": _footer_mobile_links(is_secure),
        "legal_links": _footer_legal_links(),
        "openedx_link": _footer_openedx_link(is_secure),
    }


def _footer_copyright():
    """Return the copyright to display in the footer.

    Returns: unicode

    """
    org_name = (
        "edX Inc" if settings.FEATURES.get('IS_EDX_DOMAIN', False)
        else microsite.get_value('PLATFORM_NAME', settings.PLATFORM_NAME)
    )

    # Translators: 'EdX', 'edX', and 'Open edX' are trademarks of 'edX Inc.'.
    # Please do not translate any of these trademarks and company names.
    return _(
        u"\u00A9 {org_name}.  All rights reserved except where noted.  "
        u"EdX, Open edX and the edX and OpenEdX logos are registered trademarks "
        u"or trademarks of edX Inc."
    ).format(org_name=org_name)


def _footer_openedx_link(is_secure):
    """Return the image link for "powered by OpenEdX".

    Args:
        is_secure (bool): Whether the request is using TLS.

    Returns: dict

    """
    return {
        "url": "http://open.edx.org",
        "title": _("Powered by Open edX"),
        "image": _absolute_url_staticfile(is_secure, "images/openedx-logo-tag.png")
    }


def _footer_social_links():
    """Return the social media links to display in the footer.

    Returns: list

    """
    links = []
    for social_name in settings.SOCIAL_MEDIA_FOOTER_NAMES:
        links.append(
            {
                "name": social_name,
                "title": unicode(settings.SOCIAL_MEDIA_FOOTER_DISPLAY.get(social_name, {}).get("title", "")),
                "url": settings.SOCIAL_MEDIA_FOOTER_URLS.get(social_name, "#"),
                "icon-class": settings.SOCIAL_MEDIA_FOOTER_DISPLAY.get(social_name, {}).get("icon", ""),
            }
        )
    return links


def _footer_navigation_links():
    """Return the navigation links to display in the footer. """
    return [
        {
            "name": link_name,
            "title": link_title,
            "url": link_url
        }
        for link_name, link_url, link_title in [
            ("about", marketing_link("ABOUT"), _("About")),
            ("news", marketing_link("NEWS"), _("News")),
            ("contact", marketing_link("CONTACT"), _("Contact")),
            ("faq", marketing_link("FAQ"), _("FAQ")),
            ("blog", marketing_link("BLOG"), _("edX Blog")),
            ("donate", marketing_link("DONATE"), _("Donate to edX")),
            ("jobs", marketing_link("JOBS"), _("Jobs at edX")),
        ]
        if link_url and link_url != "#"
    ]


def _footer_legal_links():
    """Return the legal footer links (e.g. terms of service). """
    return [
        {
            "name": "terms_of_service",
            "title": _("Terms of Service"),
            "url": marketing_link("TOS")
        },
        {
            "name": "privacy_policy",
            "title": _("Privacy Policy"),
            "url": marketing_link("PRIVACY")
        },
        # TODO: add accessibility policy when it is ready
    ]


def _footer_mobile_links(is_secure):
    """Return the mobile app store links.

    Args:
        is_secure (bool): Whether the request is using TLS.

    Returns: list

    """
    mobile_links = []
    if settings.FEATURES.get('ENABLE_FOOTER_MOBILE_APP_LINKS'):
        mobile_links = [
            {
                "name": "apple",
                "title": "Apple",
                "url": settings.MOBILE_STORE_URLS.get('apple', '#'),
                "image": _absolute_url_staticfile(is_secure, 'images/app/app_store_badge_135x40.svg')
            },
            {
                "name": "google",
                "title": "Google",
                "url": settings.MOBILE_STORE_URLS.get('google', '#'),
                "image": _absolute_url_staticfile(is_secure, 'images/app/google_play_badge_45.png')
            }
        ]
    return mobile_links


def _footer_logo_img(is_secure):
    """Return the logo used for footer about link

    Args:
        is_secure (bool): Whether the request is using TLS.

    Returns:
        Absolute url to logo
    """
    logo_name = (
        u"images/edx-theme/edx-header-logo.png"
        if settings.FEATURES.get('IS_EDX_DOMAIN', False)
        else u"images/default-theme/logo.png"
    )

    return _absolute_url_staticfile(is_secure, logo_name)


def _absolute_url(is_secure, url_path):
    """Construct an absolute URL back to the site.

    Arguments:
        is_secure (bool): If true, use HTTPS as the protocol.
        url_path (unicode): The path of the URL.

    Returns:
        unicode

    """
    protocol = "https://" if is_secure else "http://"
    site_name = microsite.get_value('SITE_NAME', settings.SITE_NAME)
    return u"{protocol}{site_name}{url_path}".format(
        protocol=protocol,
        site_name=site_name,
        url_path=url_path,
    )


def _absolute_url_staticfile(is_secure, name):
    """Construct an absolute URL back to a static resource on the site.

    Arguments:
        is_secure (bool): If true, use HTTPS as the protocol.
        name (unicode): The name of the static resource to retrieve.

    Returns:
        unicode

    """
    url_path = staticfiles_storage.url(name)
    return _absolute_url(is_secure, url_path)
