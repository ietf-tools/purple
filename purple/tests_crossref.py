# Copyright The IETF Trust 2025, All Rights Reserved

from django.test import TestCase

from purple.crossref import _get_name_parts


class CrossrefTests(TestCase):
    def test_get_name_parts(self):
        names = {
            "Legolas Greenleaf": ("Legolas", "Greenleaf", ""),
            "A. Undómiel": ("A.", "Undómiel", ""),
            "Aragorn Elessar 2nd": ("Aragorn", "Elessar", "2nd"),
            "Théoden van Ednew": ("Théoden", "van Ednew", ""),
            "Q": ("", "Q", ""),  # crossref requires a surname
            "Saruman": ("", "Saruman", ""),
        }
        for name, name_parts in names.items():
            self.assertEqual(_get_name_parts(name), name_parts)
