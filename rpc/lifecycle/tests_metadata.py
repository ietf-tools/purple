# Copyright The IETF Trust 2026, All Rights Reserved
import xml.etree.ElementTree as ET
from unittest.mock import MagicMock, patch

from django.test import TestCase
from rpcapi_client.exceptions import ApiException, NotFoundException

from datatracker.rpcapi import DataTrackerUnavailable
from rpc.factories import RfcToBeFactory

from .metadata import (
    DatatrackerInconsistency,
    Metadata,
    MetadataComparator,
    _already_parenthesized,
    _inline_text,
    _is_simple_expression,
)


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


class AlreadyParenthesizedTests(TestCase):
    def test_too_short(self):
        self.assertFalse(_already_parenthesized(""))
        self.assertFalse(_already_parenthesized("("))

    def test_no_outer_parens(self):
        self.assertFalse(_already_parenthesized("x+y"))

    def test_simple(self):
        self.assertTrue(_already_parenthesized("(x+y)"))
        self.assertTrue(_already_parenthesized("(x)"))

    def test_nested_balanced(self):
        self.assertTrue(_already_parenthesized("((x+y))"))

    def test_two_groups(self):
        # outer ( and ) present but inner closes before the end
        self.assertFalse(_already_parenthesized("(a)(b)"))

    def test_inner_unbalanced(self):
        self.assertFalse(_already_parenthesized("(a))"))


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
        self.assertTrue(
            _is_simple_expression("((x + y))")
        )  # double-wrapped: no third layer
        self.assertFalse(
            _is_simple_expression("(a)(b)")
        )  # two groups: not a single balanced wrap

    def test_sign_with_word(self):
        self.assertTrue(_is_simple_expression("+n"))

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
        self.assertEqual(
            Metadata.extract_name_from_author_dict({"fullname": "J Doe"}),
            "J Doe",
            "single letter name",
        )


class ParseDocNameTests(TestCase):
    def test_doc_name_is_captured_verbatim(self):
        xml = '<rfc docName="draft-ietf-foo-16"><front><title>T</title></front></rfc>'
        self.assertEqual(Metadata.parse_rfc_xml(xml)["doc_name"], "draft-ietf-foo-16")

    def test_missing_doc_name_is_empty(self):
        xml = "<rfc><front><title>T</title></front></rfc>"
        self.assertEqual(Metadata.parse_rfc_xml(xml)["doc_name"], "")


class CompareRevisionTests(TestCase):
    """RFCXML and datatracker must agree before the database rev is judged."""

    DRAFT = "draft-ietf-foo-bar"

    def _row(self, rev, *, doc_name, latest=None, draft=True):
        rfc = RfcToBeFactory(rev=rev, draft__name=self.DRAFT)
        if not draft:
            rfc.draft = None
        comparator = MetadataComparator(rfc, {"title": rfc.title, "doc_name": doc_name})
        # Bypass the datatracker fetch by priming the cached_property.
        if draft:
            comparator.__dict__["_datatracker_rev"] = latest
            return comparator.compare_revision()
        with patch("datatracker.rpcapi.get_rpcapi_client", side_effect=AssertionError):
            return comparator.compare_revision()

    def _assert_hard_error(self, row):
        self.assertFalse(row["is_match"])
        self.assertTrue(row["is_error"])
        self.assertFalse(row["can_fix"])
        self.assertIn("publisher must resolve", row["detail"])

    def test_all_agree(self):
        row = self._row("16", doc_name=f"{self.DRAFT}-16", latest="16")
        self.assertTrue(row["is_match"])
        self.assertFalse(row["is_error"])

    def test_agreed_but_database_stale_is_fixable(self):
        row = self._row("15", doc_name=f"{self.DRAFT}-16", latest="16")
        self.assertFalse(row["is_match"])
        self.assertTrue(row["is_error"])
        self.assertTrue(row["can_fix"])
        self.assertEqual(row["db_value"], "15")
        self.assertEqual(row["xml_value"], "16")

    def test_no_draft_compares_xml_with_database_only(self):
        row = self._row("16", doc_name="draft-whatever-16", draft=False)
        self.assertTrue(row["is_match"])
        self.assertFalse(row["is_error"])

    def test_no_draft_stale_database_is_fixable(self):
        row = self._row("15", doc_name="draft-whatever-16", draft=False)
        self.assertFalse(row["is_match"])
        self.assertTrue(row["is_error"])
        self.assertTrue(row["can_fix"])
        self.assertEqual(row["xml_value"], "16")
        self.assertIn("the RFCXML says -16", row["detail"])

    def test_no_draft_with_unusable_doc_name_blocks(self):
        row = self._row("16", doc_name="draft-whatever-final", draft=False)
        self._assert_hard_error(row)
        self.assertIn("no revision suffix", row["detail"])

    def test_document_and_datatracker_disagree(self):
        row = self._row("16", doc_name=f"{self.DRAFT}-16", latest="17")
        self._assert_hard_error(row)
        self.assertIn("-16", row["detail"])
        self.assertIn("-17", row["detail"])

    def test_doc_name_for_another_draft(self):
        row = self._row("16", doc_name="draft-someone-else-16", latest="16")
        self._assert_hard_error(row)
        self.assertIn("not for draft", row["detail"])
        self.assertIn("latest is -16", row["detail"])
        self.assertEqual(row["xml_value"], "")

    def test_doc_name_without_revision_suffix(self):
        row = self._row("16", doc_name=f"{self.DRAFT}-final", latest="16")
        self._assert_hard_error(row)
        self.assertIn("no revision suffix", row["detail"])

    def test_missing_doc_name(self):
        row = self._row("16", doc_name="", latest="16")
        self._assert_hard_error(row)
        self.assertIn("docName not recorded", row["detail"])

    def test_datatracker_failure_is_a_503(self):
        rfc = RfcToBeFactory(rev="16", draft__name=self.DRAFT)
        rpcapi = MagicMock()
        rpcapi.get_draft_by_id.side_effect = ApiException(status=500)
        with (
            patch("datatracker.rpcapi.get_rpcapi_client", return_value=rpcapi),
            self.assertRaises(DataTrackerUnavailable),
        ):
            MetadataComparator(rfc, {"doc_name": f"{self.DRAFT}-16"}).compare_revision()

    def _datatracker_rev(self, rfc, rpcapi):
        with patch("datatracker.rpcapi.get_rpcapi_client", return_value=rpcapi):
            return MetadataComparator(rfc, {})._datatracker_rev

    def test_datatracker_rev_raises_for_missing_draft_or_rev(self):
        rfc = RfcToBeFactory(draft__name=self.DRAFT)
        rpcapi = MagicMock()
        rpcapi.get_draft_by_id.return_value.rev = "16"
        self.assertEqual(self._datatracker_rev(rfc, rpcapi), "16")
        rpcapi.get_draft_by_id.return_value.rev = ""
        with self.assertRaisesRegex(DatatrackerInconsistency, "has no revision"):
            self._datatracker_rev(rfc, rpcapi)
        rpcapi.get_draft_by_id.side_effect = NotFoundException()
        with self.assertRaisesRegex(
            DatatrackerInconsistency, f"has no draft {self.DRAFT}"
        ):
            self._datatracker_rev(rfc, rpcapi)

    @patch.object(MetadataComparator, "compare_all")
    def test_fix_sets_rev_to_agreed_value(self, mock_compare_all):
        rfc = RfcToBeFactory(rev="15", draft__name=self.DRAFT)
        mock_compare_all.return_value = [
            {"field": "revision", "is_match": False, "can_fix": True, "xml_value": "16"}
        ]
        Metadata.update_metadata(rfc, {"doc_name": f"{self.DRAFT}-16"})
        rfc.refresh_from_db()
        self.assertEqual(rfc.rev, "16")
