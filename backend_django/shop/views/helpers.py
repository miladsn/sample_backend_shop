from django.urls import reverse, NoReverseMatch
import re

def get_base_breadcrumbs():
    """
    Creates a base list that always starts from the dashboard

    Similar to the protected method in Laravel's BaseController
    """
    return [
        {
            "title": "داشبورد",
            "url":  reverse('cms:dashboard'),
        }
    ]

def create_module_breadcrumbs(title, url_name, without_link=False):
    """
   Versatile function for generating module breadcrumbs:

    - title: Module title (e.g., 'Products' or 'Categories')
    - url_name: Name of the list route (e.g., 'shop:product_list')
    - without_link: Whether to remove the link (True for the list page)
    """
    breadcrumbs = get_base_breadcrumbs()

    url = None
    if not without_link:
        try:
            url = reverse(url_name)
        except NoReverseMatch:
            url = None

    breadcrumbs.append(
        {
            "title": title,
            "url": url,
        }
    )
    return breadcrumbs





def normalize_iranian_phone(phone: str) -> str:
    """
    Converts any format of Iranian phone numbers into a standard 10-digit format (excluding the leading zero and country code).
    Example: +989123456789, 09123456789, or 9123456789 -> 9123456789
    It also converts Persian/Arabic numerals into English digits.
    """
    if not phone:
        return ''

    # Converting Persian and Arabic numerals to English
    persian_arabic_digits = "۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩"
    english_digits = "01234567890123456789"
    translation_table = str.maketrans(persian_arabic_digits, english_digits)
    phone = str(phone).translate(translation_table).strip()

    #Removing any non-numeric characters (spaces, hyphens, parentheses, +, etc.)
    phone = re.sub(r'\D', '', phone)

    # Removing Iran country codes (0098, 98, or the leading 0)
    if phone.startswith('0098'):
        phone = phone[4:]
    elif phone.startswith('98'):
        phone = phone[2:]

    if phone.startswith('0'):
        phone = phone[1:]

    return phone
