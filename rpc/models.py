# Copyright The IETF Trust 2023-2025, All Rights Reserved

import datetime
from dataclasses import dataclass
from itertools import pairwise

from django.db import models
from django.utils import timezone
from rules import always_deny
from rules.contrib.models import RulesModel
from simple_history.models import HistoricalRecords

from .dt_v1_api_utils import (
    DatatrackerFetchFailure,
    NoSuchSlug,
    datatracker_stdlevelname,
    datatracker_streamname,
)
from .rules import is_comment_author, is_rpc_person


class DumpInfo(models.Model):
    timestamp = models.DateTimeField()


class RpcPerson(models.Model):
    datatracker_person = models.OneToOneField(
        "datatracker.DatatrackerPerson", on_delete=models.PROTECT
    )
    can_hold_role = models.ManyToManyField("RpcRole", blank=True)
    capable_of = models.ManyToManyField("Capability", blank=True)
    hours_per_week = models.PositiveSmallIntegerField(default=40)
    manager = models.ForeignKey(
        "RpcPerson",
        blank=True,
        null=True,
        on_delete=models.RESTRICT,
        limit_choices_to={"can_hold_role__slug": "manager"},
        related_name="managed_people",
    )
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return str(self.datatracker_person)


class RfcToBeLabel(models.Model):
    """Through model for linking Label to RfcToBe

    This exists so we can specify on_delete=models.PROTECT for the label FK.
    """

    rfctobe = models.ForeignKey("RfcToBe", on_delete=models.CASCADE)
    label = models.ForeignKey("Label", on_delete=models.PROTECT)

    class Meta:
        verbose_name_plural = "RfcToBe labels"


class RfcToBe(models.Model):
    """RPC representation of a pre-publication RFC"""

    disposition = models.ForeignKey("DispositionName", on_delete=models.PROTECT)
    is_april_first_rfc = models.BooleanField(default=False)
    draft = models.ForeignKey(
        "datatracker.Document", null=True, on_delete=models.PROTECT
    )
    rfc_number = models.PositiveIntegerField(null=True, unique=True)

    submitted_format = models.ForeignKey("SourceFormatName", on_delete=models.PROTECT)
    submitted_std_level = models.ForeignKey(
        "StdLevelName", on_delete=models.PROTECT, related_name="+"
    )
    submitted_boilerplate = models.ForeignKey(
        "TlpBoilerplateChoiceName",
        on_delete=models.PROTECT,
        related_name="+",
        help_text="TLP IPR boilerplate option applicable when document entered the "
        "queue",
    )
    submitted_stream = models.ForeignKey(
        "StreamName", on_delete=models.PROTECT, related_name="+"
    )

    intended_std_level = models.ForeignKey(
        "StdLevelName", on_delete=models.PROTECT, related_name="+"
    )
    intended_boilerplate = models.ForeignKey(
        "TlpBoilerplateChoiceName",
        on_delete=models.PROTECT,
        related_name="+",
        help_text="TLP IPR boilerplate option intended to apply upon publication "
        "as RFC",
    )
    intended_stream = models.ForeignKey(
        "StreamName", on_delete=models.PROTECT, related_name="+"
    )

    external_deadline = models.DateTimeField(null=True)
    internal_goal = models.DateTimeField(null=True)

    # Labels applied to this instance. To track history, see
    # https://django-simple-history.readthedocs.io/en/latest/historical_model.html#tracking-many-to-many-relationships
    # It seems that django-simple-history does not get along with through models
    # declared using a string
    # reference, so we must use the model class itself.
    labels = models.ManyToManyField("Label", through=RfcToBeLabel)

    history = HistoricalRecords(m2m_fields=[labels])

    class Meta:
        verbose_name_plural = "RfcToBes"
        constraints = [
            models.UniqueConstraint(
                fields=["rfc_number"],
                name="unique_non_null_rfc_number",
                nulls_distinct=True,
            )
        ]

    def __str__(self):
        return (
            f"RfcToBe for {self.draft if self.rfc_number is None else self.rfc_number}"
        )

    @dataclass
    class Interval:
        start: datetime.datetime
        end: datetime.datetime | None = None

    def time_intervals_with_label(self, label) -> list[Interval]:
        hist = list(self.history.all())
        label_changes = filter(
            lambda delta: len(delta.changes) > 0,
            (
                newer.diff_against(older, included_fields=["labels"])
                for newer, older in pairwise(hist)
            ),
        )

        intervals: list[RfcToBe.Interval] = []
        for ch in reversed(list(label_changes)):
            # Every changeset will have 1 change because we specified 1 included_field
            if label.pk in [
                related_label["label"] for related_label in ch.changes[0].new
            ]:
                if len(intervals) == 0 or intervals[-1].end is not None:
                    intervals.append(RfcToBe.Interval(start=ch.new_record.history_date))
            else:
                if len(intervals) > 0 and intervals[-1].end is None:
                    intervals[-1].end = ch.new_record.history_date
        if len(intervals) > 0 and intervals[-1].end is None:
            intervals[-1].end = datetime.datetime.now().astimezone(datetime.UTC)
        return intervals


class Name(models.Model):
    slug = models.CharField(max_length=32, primary_key=True)
    name = models.CharField(max_length=255)
    desc = models.TextField(blank=True)
    used = models.BooleanField(default=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class DispositionName(Name):
    pass


class SourceFormatName(Name):
    pass


class StdLevelNameManager(models.Manager):
    def from_slug(self, slug):
        if self.filter(slug=slug).exists():
            return self.get(slug=slug)
        else:
            try:
                _, name, desc = datatracker_stdlevelname(slug)
                return self.create(slug=slug, name=name, desc=desc)
            except (DatatrackerFetchFailure, NoSuchSlug) as err:
                raise self.model.DoesNotExist() from err


class StdLevelName(Name):
    objects = StdLevelNameManager()


class TlpBoilerplateChoiceName(Name):
    pass


class StreamNameManager(models.Manager):
    def from_slug(self, slug):
        if self.filter(slug=slug).exists():
            return self.get(slug=slug)
        else:
            try:
                _, name, desc = datatracker_streamname(slug)
                return self.create(slug=slug, name=name, desc=desc)
            except (DatatrackerFetchFailure, NoSuchSlug) as err:
                raise self.model.DoesNotExist() from err


class StreamName(Name):
    objects = StreamNameManager()


class DocRelationshipName(Name):
    pass


class ClusterMember(models.Model):
    cluster = models.ForeignKey("rpc.Cluster", on_delete=models.CASCADE)
    doc = models.ForeignKey("datatracker.Document", on_delete=models.CASCADE)
    order = models.IntegerField(null=False, blank=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["cluster", "order"],
                name="clustermember_unique_order_in_cluster",
                violation_error_message="order in cluster must be unique",
                deferrable=models.Deferrable.DEFERRED,
            ),
            models.UniqueConstraint(
                fields=["doc"],
                name="clustermember_unique_doc",
                violation_error_message="A document may not appear in more than one "
                "cluster",
                deferrable=models.Deferrable.DEFERRED,
            ),
        ]
        ordering = ["order"]


class Cluster(models.Model):
    number = models.PositiveIntegerField(unique=True)
    docs = models.ManyToManyField("datatracker.Document", through=ClusterMember)

    def __str__(self):
        return f"cluster {self.number} ({self.docs.count()} documents)"


class UnusableRfcNumber(models.Model):
    number = models.PositiveIntegerField(primary_key=True)
    comment = models.TextField(blank=True)

    class Meta:
        ordering = ["number"]

    def __str__(self):
        return str(self.number)


class RpcRole(models.Model):
    slug = models.CharField(max_length=32, primary_key=True)
    name = models.CharField(max_length=255)
    desc = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Capability(models.Model):
    slug = models.CharField(max_length=32, primary_key=True)
    name = models.CharField(max_length=255)
    desc = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "capabilities"

    def __str__(self):
        return self.name


ASSIGNMENT_STATE_CHOICES = (
    ("assigned", "assigned"),
    ("in progress", "in progress"),
    ("done", "done"),
)


class AssignmentQuerySet(models.QuerySet):
    def active(self):
        """QuerySet including only active Assignments"""
        return super().exclude(state="done")


class Assignment(models.Model):
    """Assignment of an RpcPerson to an RfcToBe"""

    objects = AssignmentQuerySet.as_manager()

    rfc_to_be = models.ForeignKey(RfcToBe, on_delete=models.PROTECT)
    person = models.ForeignKey(RpcPerson, on_delete=models.PROTECT)
    role = models.ForeignKey(RpcRole, on_delete=models.PROTECT)
    state = models.CharField(
        max_length=32, choices=ASSIGNMENT_STATE_CHOICES, default="assigned"
    )
    comment = models.TextField(blank=True)
    time_spent = models.DurationField(default=datetime.timedelta(0))  # tbd

    def __str__(self):
        return f"{self.person} assigned as {self.role} for {self.rfc_to_be}"


class RfcAuthor(models.Model):
    # The abbreviated name that appears on the first page of the RFC is
    # captured for search and metadata purposes. (The datatracker name
    # for the person may be different that what appeared on an older RFC
    # as people's names change over time).
    titlepage_name = models.CharField(max_length=128)
    is_editor = models.BooleanField(default=False)
    # For some older RFCs we don't have a datatracker person to link to, and
    # in some cases the listed author wasn't a _person_.
    datatracker_person = models.ForeignKey(
        "datatracker.DatatrackerPerson", on_delete=models.PROTECT, null=True
    )
    rfc_to_be = models.ForeignKey(
        RfcToBe, on_delete=models.PROTECT, related_name="authors"
    )
    order = models.PositiveIntegerField(
        help_text="Order of the author on the document",
        null=False,
        blank=False,
    )

    def __str__(self):
        return f"{self.datatracker_person} as author of {self.rfc_to_be}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["datatracker_person", "rfc_to_be"],
                name="unique_author_per_document",
                violation_error_message="the person is already an author of this "
                "document",
            ),
            models.UniqueConstraint(
                fields=["rfc_to_be", "order"],
                name="unique_author_order_per_document",
                violation_error_message="each author order must be unique per document",
                deferrable=models.Deferrable.DEFERRED,
            ),
        ]
        ordering = ["rfc_to_be", "order"]


class AdditionalEmail(models.Model):
    email = models.EmailField()
    rfc_to_be = models.ForeignKey(RfcToBe, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.email} associated with {self.rfc_to_be}"


class FinalApproval(models.Model):
    """Captures approvals for publication

    This model captures final approval from an rfc's titlepage authors.
    Lack of an approved date means approval has not been provided.

    Sometimes the titlepage author is not a person, such as when it is the IAB.
    The request for approval from such a body is captured in the body field.
    Body would be non-blank, approver would be None, approved would be None.
    A person will provide approval on behalf of that body, so once approved
    is not None, approver will also be not None. Overriding approver will
    always be None when body is used.

    Overriding approver is used when someone has to step in for whoever is
    pointed to as approver (such as when an author passes away or otherwise
    becomes non-responsive). Overriding approver should never be not None if
    approver is None.
    """

    rfc_to_be = models.ForeignKey(RfcToBe, on_delete=models.PROTECT)
    body = models.CharField(max_length=64, blank=True, default="")
    approver = models.ForeignKey(
        "datatracker.DatatrackerPerson",
        on_delete=models.PROTECT,
        null=True,
        related_name="approver_set",
    )
    overriding_approver = models.ForeignKey(
        "datatracker.DatatrackerPerson",
        on_delete=models.PROTECT,
        null=True,
        related_name="overriding_approver_set",
    )
    requested = models.DateTimeField(default=timezone.now)
    approved = models.DateTimeField(null=True)

    def __str__(self):
        if self.approved:
            if self.overriding_approver:
                return (
                    f"final approval from {self.overriding_approver} on behalf of "
                    f"{self.approver}"
                )
            else:
                return f"final approval from {self.approver}"
        else:
            return (
                "request for final approval from "
                f"{self.approver if self.approver else self.body}"
            )

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(approved__isnull=True) | models.Q(approver__isnull=False)
                ),
                name="finalapproval_approval_requires_approver",
                violation_error_message="approval requires an approver",
            ),
            models.CheckConstraint(
                check=(
                    models.Q(overriding_approver__isnull=True)
                    | models.Q(approver__isnull=False)
                ),
                name="finalapproval_approval_override_requires_approver",
                violation_error_message="approval override requires an approver be set",
            ),
            models.CheckConstraint(
                check=(models.Q(body="") | models.Q(overriding_approver__isnull=True)),
                name="finalapproval_body_approval_no_override",
                violation_error_message="body approval cant be overridden",
            ),
        ]


class ActionHolderQuerySet(models.QuerySet):
    def active(self):
        """QuerySet including only not-completed ActionHolders"""
        return super().filter(completed__isnull=True)


class ActionHolder(models.Model):
    """Someone needs to do what the comment says to/about a document

    Notes:
        * An AD may need to approve normative changes during auth48,
          and may need to do this more than once (change one is approved,
          then change two is discovered)
        * Can be attached to a datatracker doc prior to an RfcToBe being created
    """

    objects = ActionHolderQuerySet.as_manager()

    target_document = models.ForeignKey(
        "datatracker.Document",
        null=True,
        on_delete=models.PROTECT,
        related_name="actionholder_set",
    )
    target_rfctobe = models.ForeignKey(
        RfcToBe,
        null=True,
        on_delete=models.PROTECT,
        related_name="actionholder_set",
    )

    datatracker_person = models.ForeignKey(
        "datatracker.DatatrackerPerson", on_delete=models.PROTECT
    )
    body = models.CharField(max_length=64, blank=True, default="")
    since_when = models.DateTimeField(default=timezone.now)
    completed = models.DateTimeField(null=True)
    deadline = models.DateTimeField(null=True)
    comment = models.TextField(blank=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(target_document__isnull=True)
                    ^ models.Q(target_rfctobe__isnull=True)
                ),
                name="actionholder_exactly_one_target",
                violation_error_message="exactly one target field must be set",
            ),
            models.CheckConstraint(
                check=(
                    models.Q(completed__isnull=True)
                    | models.Q(datatracker_person__isnull=False)
                ),
                name="actionholder_completion_requires_person",
                violation_error_message="completion requires a person",
            ),
        ]

    def __str__(self):
        return (
            f"{'Completed' if self.completed else 'Pending'} action held by "
            f"{self.datatracker_person}"
        )


class RpcRelatedDocument(models.Model):
    """Relationship between an RFC-to-be and a draft, RFC, or RFC-to-be

    rtb = RfcToBe.objects.get(...)  # or Document.objects.get(...)
    rtb.rpcrelateddocument_set.all()  # relationships where rtb is source
    rtb.rpcrelateddocument_target_set()  # relationships where rtb is target
    """

    relationship = models.ForeignKey("DocRelationshipName", on_delete=models.PROTECT)
    source = models.ForeignKey(RfcToBe, on_delete=models.PROTECT)
    target_document = models.ForeignKey(
        "datatracker.Document",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="rpcrelateddocument_target_set",
    )
    target_rfctobe = models.ForeignKey(
        RfcToBe,
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="rpcrelateddocument_target_set",
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(target_document__isnull=True)
                    ^ models.Q(target_rfctobe__isnull=True)
                ),
                name="rpcrelateddocument_exactly_one_target",
                violation_error_message="exactly one target field must be set",
            ),
            # Unique for (source, target_document) when target_document is set
            models.UniqueConstraint(
                fields=["source", "target_document"],
                condition=models.Q(target_document__isnull=False),
                name="unique_source_targetdoc",
                violation_error_message="A source/target_document relationship must "
                "be unique.",
            ),
            # Unique for (source, target_rfctobe) when target_rfctobe is set
            models.UniqueConstraint(
                fields=["source", "target_rfctobe"],
                condition=models.Q(target_rfctobe__isnull=False),
                name="unique_source_targetrfctobe",
                violation_error_message="A source/target_rfctobe relationship must "
                "be unique.",
            ),
        ]

    def __str__(self):
        target = self.target_document if self.target_document else self.target_rfctobe
        return f"{self.relationship} relationship from {self.source} to {target}"


class RpcDocumentComment(RulesModel):
    """Private RPC comment about a draft, RFC or RFC-to-be"""

    document = models.ForeignKey(
        "datatracker.Document", null=True, blank=True, on_delete=models.PROTECT
    )
    rfc_to_be = models.ForeignKey(
        RfcToBe, null=True, blank=True, on_delete=models.PROTECT
    )
    comment = models.TextField()
    by = models.ForeignKey("datatracker.DatatrackerPerson", on_delete=models.PROTECT)
    time = models.DateTimeField(default=timezone.now)
    history = HistoricalRecords()

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(document__isnull=True) ^ models.Q(rfc_to_be__isnull=True)
                ),
                name="rpcdocumentcomment_exactly_one_target",
                violation_error_message="exactly one of doc or rfc_to_be must be set",
            )
        ]
        # Permissions applied via AutoPermissionViewSetMixin
        rules_permissions = {
            "add": is_rpc_person,
            "change": is_comment_author,
            "delete": always_deny,
            "view": is_rpc_person,
        }

    def __str__(self):
        target = self.document if self.document else self.rfc_to_be
        return f"RpcDocumentComment about {target} by {self.by} on {self.time:%Y-%m-%d}"

    def last_edit(self):
        """Get HistoricalRecord of last edit event"""
        return self.history.filter(
            history_type="~"
        ).first()  # "~" is "update", ignore create/delete


TAILWIND_COLORS = [
    "slate",
    "gray",
    "zinc",
    "neutral",
    "stone",
    "red",
    "orange",
    "amber",
    "yellow",
    "lime",
    "green",
    "emerald",
    "teal",
    "cyan",
    "sky",
    "blue",
    "indigo",
    "violet",
    "purple",
    "fuchsia",
    "pink",
    "rose",
]


class Label(models.Model):
    """Badges that can be put on other objects"""

    ### Will have to have LabelHistory on objects that have collections of labels
    ### That is, we need to compute when something had a label and how long

    slug = models.CharField(max_length=64, unique=True)
    is_exception = models.BooleanField(default=False)
    is_complexity = models.BooleanField(default=False)
    color = models.CharField(
        max_length=7,
        default="purple",
        choices=zip(TAILWIND_COLORS, TAILWIND_COLORS, strict=False),
    )
    history = HistoricalRecords()

    def __str__(self):
        return self.slug


class RpcAuthorComment(models.Model):
    """Private RPC comment about an author

    Notes:
        rjs = Person(...)
        rjs.rpcauthorcomments_by.all()  # comments by
        rjs.rpcauthorcomment_set.all()  # comments about
    """

    datatracker_person = models.ForeignKey(
        "datatracker.DatatrackerPerson", on_delete=models.PROTECT
    )
    comment = models.TextField()
    by = models.ForeignKey(
        "datatracker.DatatrackerPerson",
        on_delete=models.PROTECT,
        related_name="rpcauthorcomments_by",
    )
    time = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return "RpcAuthorComment about {} by {} on {}".format(
            self.datatracker_person,
            self.by,
            self.time.strftime("%Y-%m-%d"),
        )


class ApprovalLogMessage(models.Model):
    """Public log of final approval-related steps

    These messages will be displayed on the approvals
    views (historically the AUTH48 approvals page) and
    will be publically visible.
    """

    rfc_to_be = models.ForeignKey(RfcToBe, on_delete=models.PROTECT)
    log_message = models.TextField()
    by = models.ForeignKey(
        "datatracker.DatatrackerPerson",
        on_delete=models.PROTECT,
        related_name="approvallogmessage_by",
    )
    time = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return "ApprovalLogMessage for {} by {} on {}".format(
            self.rfc_to_be,
            self.by,
            self.time.strftime("%Y-%m-%d"),
        )
