# Copyright The IETF Trust 2026, All Rights Reserved
import xml.etree.ElementTree as ET

from django.test import TestCase

from .metadata import Metadata, _inline_text, _is_simple_expression


class MetadataTests(TestCase):
    def test_extract_name_from_author_dict(self):
        self.assertEqual(
            Metadata.extract_name_from_author_dict({}), "", "empty input dict"
        )
        self.assertEqual(
            Metadata.extract_name_from_author_dict({"initials": " Ä. B. "}),
            "Ä. B.",
            "initials only plus stripping",
        )
        self.assertEqual(
            Metadata.extract_name_from_author_dict({"surname": " Cly∂e "}),
            "Cly∂e",
            "surname only plus stripping",
        )
        self.assertEqual(
            Metadata.extract_name_from_author_dict(
                {"initials": " À. B. ", "surname": " Clydé"}
            ),
            "À. B. Clydé",
            "initials+surname + stripping",
        )
        self.assertEqual(
            Metadata.extract_name_from_author_dict(
                {
                    "initials": "A. B.",
                    "surname": "Clyde",
                    "fullname": "Diane Egawa",
                    "asciiFullname": "Frank Gouda",
                }
            ),
            "A. B. Clyde",
            "initials+surname have priority",
        )
        self.assertEqual(
            Metadata.extract_name_from_author_dict(
                {"fullname": "Diane Egawa", "asciiFullname": "Frank Gouda"}
            ),
            "F. Gouda",
            "asciiFullname has priority",
        )
        self.assertEqual(
            Metadata.extract_name_from_author_dict(
                {"fullname": "Diane Egawa", "asciiFullname": "Gouda"}
            ),
            "Gouda",
            "asciiFullname has priority + single name",
        )
        self.assertEqual(
            Metadata.extract_name_from_author_dict({"fullname": "∂iane Egawa"}),
            "∂. Egawa",
            "fullname with two names",
        )
        self.assertEqual(
            Metadata.extract_name_from_author_dict({"fullname": "Egawa"}),
            "Egawa",
            "fullname with one name",
        )
        self.assertEqual(
            Metadata.extract_name_from_author_dict({"fullname": "江川"}),
            "江川",
            "fullname with one name",
        )


class IsSimpleExpressionTests(TestCase):
    def test_empty(self):
        self.assertFalse(_is_simple_expression(""))

    def test_plain_word(self):
        self.assertTrue(_is_simple_expression("x"))
        self.assertTrue(_is_simple_expression("alpha"))
        self.assertTrue(_is_simple_expression("abc123"))

    def test_digit_and_decimal(self):
        self.assertTrue(_is_simple_expression("2"))
        self.assertTrue(_is_simple_expression("1.5"))

    def test_sign_only_is_false(self):
        self.assertFalse(_is_simple_expression("+"))
        self.assertFalse(_is_simple_expression("-"))
        self.assertFalse(_is_simple_expression("−"))

    def test_sign_prefix_stripped(self):
        self.assertTrue(_is_simple_expression("+x"))
        self.assertTrue(_is_simple_expression("-n"))
        self.assertTrue(_is_simple_expression("−x"))  # U+2212 minus sign
        self.assertTrue(_is_simple_expression("±n"))  # U+00B1 plus-minus
        self.assertTrue(_is_simple_expression("﹣x"))  # U+FE63 small hyphen-minus

    def test_already_parenthesized(self):
        self.assertTrue(_is_simple_expression("(x+y)"))
        self.assertTrue(_is_simple_expression("+(x+y)"))

    def test_underscore_is_complex(self):
        self.assertFalse(_is_simple_expression("x_y"))

    def test_operator_in_middle_is_complex(self):
        self.assertFalse(_is_simple_expression("x+y"))
        self.assertFalse(_is_simple_expression("a b"))
        self.assertFalse(_is_simple_expression("1.2.3"))


class InlineTextTests(TestCase):
    def _elem(self, xml_str):
        return ET.fromstring(xml_str)

    def test_plain_text(self):
        self.assertEqual(_inline_text(self._elem("<t>Hello world</t>")), "Hello world")

    def test_em(self):
        self.assertEqual(
            _inline_text(self._elem("<t><em>important</em></t>")), "_important_"
        )

    def test_strong(self):
        self.assertEqual(
            _inline_text(self._elem("<t><strong>bold</strong></t>")), "*bold*"
        )

    def test_tt_no_decoration(self):
        self.assertEqual(_inline_text(self._elem("<t><tt>code</tt></t>")), "code")

    def test_sub_simple(self):
        self.assertEqual(_inline_text(self._elem("<t><sub>x</sub></t>")), "_x")

    def test_sub_complex(self):
        self.assertEqual(_inline_text(self._elem("<t><sub>x+y</sub></t>")), "_(x+y)")

    def test_sup_simple(self):
        self.assertEqual(_inline_text(self._elem("<t><sup>n</sup></t>")), "^n")

    def test_sup_complex(self):
        self.assertEqual(_inline_text(self._elem("<t><sup>n+1</sup></t>")), "^(n+1)")

    def test_mixed_inline_with_tail(self):
        elem = self._elem("<t>See <em>RFC</em> for details</t>")
        self.assertEqual(_inline_text(elem), "See _RFC_ for details")

    def test_tt_with_tail(self):
        elem = self._elem("<t>Use <tt>DTLS</tt> over TLS</t>")
        self.assertEqual(_inline_text(elem), "Use DTLS over TLS")

    def test_unknown_tag_passes_through(self):
        elem = self._elem("<t><bcp14>MUST</bcp14> implement</t>")
        self.assertEqual(_inline_text(elem), "MUST implement")

    def test_abstract_multiple_tt_tags(self):
        # Original bug: abstract was truncated at first inline tag
        elem = self._elem("<t>This uses <tt>DTLS</tt> and <tt>TLS</tt> protocols.</t>")
        self.assertEqual(_inline_text(elem), "This uses DTLS and TLS protocols.")
