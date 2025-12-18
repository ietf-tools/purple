# Copyright The IETF Trust 2023-2025, All Rights Reserved

import datetime
import logging
from dataclasses import dataclass
from itertools import pairwise

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import (
    Exists,
    OuterRef,
    Prefetch,
)
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

logger = logging.getLogger(__name__)


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


class UnusableRfcNumber(models.Model):
    number = models.PositiveIntegerField(primary_key=True)
    comment = models.TextField(blank=True)
    history = HistoricalRecords()

    class Meta:
        ordering = ["number"]

    def __str__(self):
        return str(self.number)


class RfcToBeLabel(models.Model):
    """Through model for linking Label to RfcToBe

    This exists so we can specify on_delete=models.PROTECT for the label FK.
    """

    rfctobe = models.ForeignKey("RfcToBe", on_delete=models.CASCADE)
    label = models.ForeignKey("Label", on_delete=models.PROTECT)

    class Meta:
        verbose_name_plural = "RfcToBe labels"


def validate_not_unusable_rfc_number(value):
    """Validate that RFC number is not in UnusableRfcNumber table"""
    if value is not None and UnusableRfcNumber.objects.filter(number=value).exists():
        raise ValidationError(
            f"RFC number {value} is marked as unusable",
            code="unusable_rfc_number",
        )


class RfcToBe(models.Model):
    """RPC representation of a pre-publication RFC"""

    class IanaStatus(models.TextChoices):
        NO_ACTIONS = "no_actions", "This document has no IANA actions"
        NOT_COMPLETED = "not_completed", "IANA has not completed actions in draft"
        COMPLETED = "completed", "IANA has completed actions in draft"
        CHANGES_REQUIRED = (
            "changes_required",
            "Changes to registries are required due to RFC edits",
        )
        RECONCILED = "reconciled", "IANA has reconciled changes between draft and RFC"

    disposition = models.ForeignKey("DispositionName", on_delete=models.PROTECT)
    is_april_first_rfc = models.BooleanField(default=False)
    draft = models.ForeignKey(
        "datatracker.Document", null=True, blank=True, on_delete=models.PROTECT
    )
    rfc_number = models.PositiveIntegerField(
        null=True,
        blank=True,
        unique=True,
        validators=[validate_not_unusable_rfc_number],
    )

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

    external_deadline = models.DateTimeField(null=True, blank=True)
    internal_goal = models.DateTimeField(null=True, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)

    # Labels applied to this instance. To track history, see
    # https://django-simple-history.readthedocs.io/en/latest/historical_model.html#tracking-many-to-many-relationships
    # It seems that django-simple-history does not get along with through models
    # declared using a string
    # reference, so we must use the model class itself.
    labels = models.ManyToManyField("Label", through=RfcToBeLabel)

    iana_status = models.CharField(
        max_length=32,
        choices=IanaStatus.choices,
        default=IanaStatus.NOT_COMPLETED,
        null=True,
        blank=True,
        help_text="Current status of IANA actions for this document",
    )

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

    def _warn_if_not_april1_rfc(self):
        """Emit a warning if called with a non-April-first RFC"""
        if not self.is_april_first_rfc:
            logger.warning(
                f"Warning! RfcToBe(pk={self.pk}) has no draft "
                "and is not an April 1st RFC"
            )

    # Properties that we currently only get from our draft
    @property
    def name(self) -> str:
        if self.draft:
            return self.draft.name
        self._warn_if_not_april1_rfc()
        if self.rfc_number is not None:
            return f"RFC {self.rfc_number}"
        return f"<RfcToBe {self.pk}>"

    @property
    def title(self) -> str:
        if self.draft:
            return self.draft.title
        self._warn_if_not_april1_rfc()
        return "<No title>"

    # Easier interface to the cluster_set
    @property
    def cluster(self) -> "Cluster | None":
        return self.draft.cluster_set.first() if self.draft else None

    @property
    def obsoletes(self) -> models.QuerySet["RfcToBe"]:
        """RfcToBes that this RfcToBe obsoletes"""
        return RfcToBe.objects.filter(
            rpcrelateddocument_target_set__source=self,
            rpcrelateddocument_target_set__relationship_id="obs",
        )

    @property
    def updates(self) -> models.QuerySet["RfcToBe"]:
        """RfcToBes that this RfcToBe obsoletes"""
        return RfcToBe.objects.filter(
            rpcrelateddocument_target_set__source=self,
            rpcrelateddocument_target_set__relationship_id="updates",
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

    def incomplete_activities(self):
        from .lifecycle.activities import incomplete_activities

        return RpcRole.objects.filter(
            slug__in=[activity.role_slug for activity in incomplete_activities(self)]
        )

    def pending_activities(self):
        from .lifecycle.activities import pending_activities

        return RpcRole.objects.filter(
            slug__in=[activity.role_slug for activity in pending_activities(self)]
        )


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


class BlockingReason(Name):
    """Predefined blocking reasons for RfcToBe instances"""

    ACTION_HOLDER_ACTIVE = "actionholder_active"
    LABEL_STREAM_HOLD = "label_stream_hold"
    LABEL_EXTREF_HOLD = "label_extref_hold"
    LABEL_AUTHOR_INPUT_REQUIRED = "label_author_input_required"
    LABEL_IANA_HOLD = "label_iana_hold"
    REFERENCE_NOT_RECEIVED = "ref_not_received"
    REFERENCE_NOT_RECEIVED_2G = "ref_not_received_2g"
    REFERENCE_NOT_RECEIVED_3G = "ref_not_received_3g"
    REFQUEUE_FIRST_EDIT_INCOMPLETE = "refqueue_first_edit_incomplete"
    REFQUEUE_SECOND_EDIT_INCOMPLETE = "refqueue_second_edit_incomplete"
    REFQUEUE_PUBLISH_INCOMPLETE = "refqueue_publish_incomplete"
    FINAL_APPROVAL_PENDING = "final_approval_pending"
    TOOLS_ISSUE = "tools_issue"


class RfcToBeBlockingReason(models.Model):
    """Tracks blocking reasons for RfcToBe instances"""

    rfc_to_be = models.ForeignKey(RfcToBe, on_delete=models.PROTECT)
    reason = models.ForeignKey(BlockingReason, on_delete=models.PROTECT)
    since_when = models.DateTimeField(default=timezone.now)
    resolved = models.DateTimeField(null=True, blank=True)
    history = HistoricalRecords()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["rfc_to_be", "reason"],
                condition=models.Q(resolved__isnull=True),
                name="unique_active_blocking_reason_per_rfc",
                violation_error_message="This blocking reason is already active for "
                "this RFC",
            ),
        ]
        ordering = ["-since_when"]

    def __str__(self):
        status = "Resolved" if self.resolved else "Active"
        return f"{status} blocking reason '{self.reason.slug}' for {self.rfc_to_be}"


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
    REFQUEUE_RELATIONSHIP_SLUG = "refqueue"
    NOT_RECEIVED_RELATIONSHIP_SLUG = "not-received"
    NOT_RECEIVED_2G_RELATIONSHIP_SLUG = "not-received-2g"
    NOT_RECEIVED_3G_RELATIONSHIP_SLUG = "not-received-3g"
    NOT_RECEIVED_RELATIONSHIP_SLUGS = [
        NOT_RECEIVED_RELATIONSHIP_SLUG,
        NOT_RECEIVED_2G_RELATIONSHIP_SLUG,
        NOT_RECEIVED_3G_RELATIONSHIP_SLUG,
    ]
    REFERENCE_RELATIONSHIP_SLUGS = NOT_RECEIVED_RELATIONSHIP_SLUGS + [
        REFQUEUE_RELATIONSHIP_SLUG
    ]


class ClusterMember(models.Model):
    cluster = models.ForeignKey("rpc.Cluster", on_delete=models.CASCADE)
    doc = models.ForeignKey("datatracker.Document", on_delete=models.CASCADE)
    order = models.IntegerField(null=False, blank=False)
    history = HistoricalRecords()

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


class ClusterQuerySet(models.QuerySet):
    def with_data_annotated(self):
        """Prefetch cluster members with related data to avoid N+1 queries"""

        return self.prefetch_related(
            Prefetch(
                "clustermember_set",
                queryset=ClusterMember.objects.exclude(
                    doc__rfctobe__disposition__slug="withdrawn"
                )
                .select_related("doc")
                .prefetch_related(
                    Prefetch(
                        "doc__rfctobe_set",
                        queryset=RfcToBe.objects.exclude(disposition__slug="withdrawn")
                        .select_related("disposition")
                        .prefetch_related(
                            Prefetch(
                                "rpcrelateddocument_set",
                                queryset=RpcRelatedDocument.objects.filter(
                                    relationship__slug__in=(
                                        DocRelationshipName.REFERENCE_RELATIONSHIP_SLUGS
                                    )
                                ).select_related(
                                    "relationship",
                                    "target_document",
                                    "target_rfctobe__draft",
                                ),
                                to_attr="references_annotated",
                            )
                        ),
                        to_attr="rfctobe_annotated",
                    )
                ),
            )
        )

    def with_is_active_annotated(self):
        """Annotate clusters with is_active status
        A cluster is considered active if it is not empty and not all drafts are
        published/withdrawn.
        """
        return self.annotate(
            is_active_annotated=Exists(
                ClusterMember.objects.filter(cluster=OuterRef("pk"))
                .exclude(doc__rfctobe__disposition__slug="published")
                .exclude(doc__rfctobe__disposition__slug="withdrawn")
            )
        )


class Cluster(models.Model):
    objects = ClusterQuerySet.as_manager()
    number = models.PositiveIntegerField(unique=True)
    docs = models.ManyToManyField("datatracker.Document", through=ClusterMember)
    history = HistoricalRecords()

    def __str__(self):
        return f"cluster {self.number} ({self.docs.count()} documents)"


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


class _AssignmentState(models.TextChoices):
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    WITHDRAWN = "withdrawn"
    CLOSED_FOR_HOLD = "closed_for_hold"


ASSIGNMENT_INACTIVE_STATES = [
    _AssignmentState.DONE,
    _AssignmentState.WITHDRAWN,
    _AssignmentState.CLOSED_FOR_HOLD,
]


class AssignmentQuerySet(models.QuerySet):
    def active(self):
        """QuerySet including only active Assignments"""
        return super().exclude(state__in=ASSIGNMENT_INACTIVE_STATES)


class Assignment(models.Model):
    """Assignment of an RpcPerson to an RfcToBe"""

    State = _AssignmentState

    # Custom manager
    objects = AssignmentQuerySet.as_manager()

    # Fields
    rfc_to_be = models.ForeignKey(RfcToBe, on_delete=models.PROTECT)
    person = models.ForeignKey(
        RpcPerson, on_delete=models.PROTECT, null=True, blank=True
    )
    role = models.ForeignKey(RpcRole, on_delete=models.PROTECT)
    state = models.CharField(max_length=32, choices=State, default=State.ASSIGNED)
    comment = models.TextField(blank=True)
    time_spent = models.DurationField(default=datetime.timedelta(0))  # tbd
    history = HistoricalRecords()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["person", "rfc_to_be", "role"],
                condition=~models.Q(state__in=ASSIGNMENT_INACTIVE_STATES),
                name="unique_active_assignment_per_person_rfc_role",
                violation_error_message="A person can only have one active assignment "
                "per RFC and role",
            ),
        ]

    def __str__(self):
        return f"{self.person} assigned as {self.role} for {self.rfc_to_be}"

    def when_entered_state(self, state: State) -> datetime.datetime | None:
        last_held = self.history.filter(state=state).last()
        return None if last_held is None else last_held.history_date

    def when_left_state(self, state: State) -> datetime.datetime | None:
        last_held = self.history.filter(state=state).last()
        following_state = None if last_held is None else last_held.next_record
        return None if following_state is None else following_state.history_date

    def when_assigned(self) -> datetime.datetime | None:
        return self.when_entered_state(self.State.ASSIGNED)

    def when_started(self) -> datetime.datetime | None:
        return self.when_entered_state(self.State.IN_PROGRESS)

    def when_completed(self) -> datetime.datetime | None:
        return self.when_entered_state(self.State.DONE)


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
        "datatracker.DatatrackerPerson", on_delete=models.PROTECT, null=True, blank=True
    )
    rfc_to_be = models.ForeignKey(
        RfcToBe, on_delete=models.PROTECT, related_name="authors"
    )
    order = models.PositiveIntegerField(
        help_text="Order of the author on the document",
        null=False,
        blank=False,
    )
    affiliation = models.CharField(max_length=255, null=True, blank=True)

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


class FinalApprovalQuerySet(models.QuerySet):
    def active(self):
        """QuerySet including only not-completed FinalApprovals"""
        return self.filter(approved__isnull=True)


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

    objects = FinalApprovalQuerySet.as_manager()

    rfc_to_be = models.ForeignKey(RfcToBe, on_delete=models.PROTECT)
    approver = models.ForeignKey(
        "datatracker.DatatrackerPerson",
        on_delete=models.PROTECT,
        related_name="approver_set",
    )
    overriding_approver = models.ForeignKey(
        "datatracker.DatatrackerPerson",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="overriding_approver_set",
    )
    requested = models.DateTimeField(default=timezone.now)
    approved = models.DateTimeField(null=True, blank=True)

    history = HistoricalRecords()

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
            return f"request for final approval from {self.approver}"


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
        blank=True,
        on_delete=models.PROTECT,
        related_name="actionholder_set",
    )
    target_rfctobe = models.ForeignKey(
        RfcToBe,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="actionholder_set",
    )

    datatracker_person = models.ForeignKey(
        "datatracker.DatatrackerPerson", on_delete=models.PROTECT
    )
    body = models.CharField(max_length=64, blank=True, default="")
    since_when = models.DateTimeField(default=timezone.now)
    completed = models.DateTimeField(null=True, blank=True)
    deadline = models.DateTimeField(null=True, blank=True)
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
            # Unique for (source, target_document, relationship) when target_document
            # is set
            models.UniqueConstraint(
                fields=["source", "target_document", "relationship"],
                condition=models.Q(target_document__isnull=False),
                name="unique_source_targetdoc_relationship",
                violation_error_message="A source/target_document/relationship "
                "combination must be unique.",
            ),
            # Unique for (source, target_rfctobe, relationship) when target_rfctobe
            # is set
            models.UniqueConstraint(
                fields=["source", "target_rfctobe", "relationship"],
                condition=models.Q(target_rfctobe__isnull=False),
                name="unique_source_targetrfctobe_relationship",
                violation_error_message="A source/target_rfctobe/relationship "
                "combination must be unique.",
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
    used = models.BooleanField(default=True)
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
    history = HistoricalRecords()

    def __str__(self):
        return "ApprovalLogMessage for {} by {} on {}".format(
            self.rfc_to_be,
            self.by,
            self.time.strftime("%Y-%m-%d"),
        )


class SubseriesMember(models.Model):
    """Tracks which RFC belongs to which subseries and its number"""

    rfc_to_be = models.ForeignKey(RfcToBe, on_delete=models.PROTECT)
    type = models.ForeignKey("SubseriesTypeName", on_delete=models.PROTECT)
    number = models.PositiveIntegerField()
    history = HistoricalRecords()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["rfc_to_be", "type", "number"],
                name="unique_subseries_member",
                violation_error_message="an RfcToBe can only be in the same subseries "
                "once",
            )
        ]

    def __str__(self):
        return (
            f"RfcToBe {self.rfc_to_be.id} is part of subseries {self.type.slug} "
            f" {self.number}"
        )


class SubseriesTypeName(Name):
    """Types of subseries, e.g., BCP, FYI, STD, etc."""

    pass
