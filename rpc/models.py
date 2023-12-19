# Copyright The IETF Trust 2023, All Rights Reserved
# -*- coding: utf-8 -*-

import datetime

from dataclasses import dataclass
from itertools import pairwise
from typing import Optional

from django.db import models
from django.utils import timezone

from simple_history.models import HistoricalRecords


class RpcPerson(models.Model):
    datatracker_person = models.OneToOneField(
        "datatracker.DatatrackerPerson", on_delete=models.PROTECT
    )
    can_hold_role = models.ManyToManyField("RpcRole")
    capable_of = models.ManyToManyField("Capability")
    hours_per_week = models.PositiveSmallIntegerField(default=40)
    manager = models.ForeignKey(
        "RpcPerson",
        null=True,
        on_delete=models.RESTRICT,
        limit_choices_to={"can_hold_role__slug": "manager"},
        related_name="managed_people",
    )

    def __str__(self):
        return str(self.datatracker_person)


class RfcToBeLabel(models.Model):
    """Through model for linking Label to RfcToBe

    This exists so we can specify on_delete=models.PROTECT for the label FK.
    """
    rfctobe = models.ForeignKey("RfcToBe", on_delete=models.CASCADE)
    label = models.ForeignKey("Label", on_delete=models.PROTECT)


class RfcToBe(models.Model):
    """RPC representation of a pre-publication RFC"""

    disposition = models.ForeignKey("DispositionName", on_delete=models.PROTECT)
    is_april_first_rfc = models.BooleanField(default=False)
    draft = models.ForeignKey(
        "datatracker.Document", null=True, on_delete=models.PROTECT
    )  # only null if is_april_first_rfc is True
    rfc_number = models.PositiveIntegerField(null=True)

    cluster = models.ForeignKey("Cluster", null=True, on_delete=models.SET_NULL)
    order_in_cluster = models.PositiveSmallIntegerField(default=1)

    submitted_format = models.ForeignKey("SourceFormatName", on_delete=models.PROTECT)
    submitted_std_level = models.ForeignKey(
        "StdLevelName", on_delete=models.PROTECT, related_name="+"
    )
    submitted_boilerplate = models.ForeignKey(
        "TlpBoilerplateChoiceName", on_delete=models.PROTECT, related_name="+"
    )
    submitted_stream = models.ForeignKey(
        "StreamName", on_delete=models.PROTECT, related_name="+"
    )

    intended_std_level = models.ForeignKey(
        "StdLevelName", on_delete=models.PROTECT, related_name="+"
    )
    intended_boilerplate = models.ForeignKey(
        "TlpBoilerplateChoiceName", on_delete=models.PROTECT, related_name="+"
    )
    intended_stream = models.ForeignKey(
        "StreamName", on_delete=models.PROTECT, related_name="+"
    )

    external_deadline = models.DateTimeField(null=True)
    internal_goal = models.DateTimeField(null=True)

    # Labels applied to this instance. To track history, see
    # https://django-simple-history.readthedocs.io/en/latest/historical_model.html#tracking-many-to-many-relationships
    # It seems that django-simple-history does not get along with through models declared using a string
    # reference, so we must use the model class itself.
    labels = models.ManyToManyField("Label", through=RfcToBeLabel)

    history = HistoricalRecords(m2m_fields=[labels])

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(draft__isnull=False) ^ models.Q(is_april_first_rfc=True),
                name="rfctobe_draft_not_null_xor_is_april_first_rfc",
                violation_error_message="draft must be null if and only if is_april_first_rfc",
            ),
            models.UniqueConstraint(
                fields=["cluster", "order_in_cluster"],
                name="rfctobe_unique_order_in_cluster",
                violation_error_message="order in cluster must be unique",
                deferrable=models.Deferrable.DEFERRED,
            ),
        ]

    def __str__(self):
        return (
            f"RfcToBe for {self.draft if self.rfc_number is None else self.rfc_number}"
        )

    @dataclass
    class Interval:
        start: datetime.datetime
        end: Optional[datetime.datetime] = None

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
            if label.pk in [related_label["label"] for related_label in ch.changes[0].new]:
                if len(intervals) == 0 or intervals[-1].end is not None:
                    intervals.append(RfcToBe.Interval(start=ch.new_record.history_date))
            else:
                if len(intervals) > 0 and intervals[-1].end is None:
                    intervals[-1].end = ch.new_record.history_date
        if len(intervals) > 0 and intervals[-1].end is None:
            intervals[-1].end = datetime.datetime.now().astimezone(datetime.timezone.utc)
        return intervals


class Name(models.Model):
    slug = models.CharField(max_length=32, primary_key=True)
    name = models.CharField(max_length=255)
    desc = models.TextField(blank=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class DispositionName(Name):
    pass


class SourceFormatName(Name):
    pass


class StdLevelName(Name):
    pass


class TlpBoilerplateChoiceName(Name):
    pass


class StreamName(Name):
    pass


class DocRelationshipName(Name):
    pass


class Cluster(models.Model):
    number = models.PositiveIntegerField(unique=True)

    def __str__(self):
        return f"cluster {self.number}"


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

    def __str__(self):
        return self.name


ASSIGNMENT_STATE_CHOICES = (
    ("assigned", "assigned"),
    ("in progress", "in progress"),
    ("done", "done"),
)


class Assignment(models.Model):
    """Assignment of an RpcPerson to an RfcToBe"""

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
    datatracker_person = models.ForeignKey(
        "datatracker.DatatrackerPerson", on_delete=models.PROTECT
    )
    rfc_to_be = models.ForeignKey(RfcToBe, on_delete=models.PROTECT)
    auth48_approved = models.DateTimeField(null=True)

    def __str__(self):
        return f"{self.datatracker_person} as author of {self.rfc_to_be}"


class FinalApproval(models.Model):
    rfc_to_be = models.ForeignKey(RfcToBe, on_delete=models.PROTECT)
    approver = models.ForeignKey(
        "datatracker.DatatrackerPerson", on_delete=models.PROTECT
    )
    requested = models.DateTimeField(default=timezone.now)
    approved = models.DateTimeField(null=True)

    def __str__(self):
        if self.approved:
            return f"final approval from {self.approver}"
        else:
            return f"request for final approval from {self.approver}"


class ActionHolder(models.Model):
    """Someone needs to do what the comment says to/about a document

    Notes:
        * An AD may need to approve normative changes during auth48,
          and may need to do this more than once (change one is approved,
          then change two is discovered)
        * Can be attached to a datatracker doc prior to an RfcToBe being created
    """

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
            )
        ]

    def __str__(self):
        return f"{'Completed' if self.completed else 'Pending'} action held by {self.datatracker_person}"


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
        null=True,
        on_delete=models.PROTECT,
        related_name="rpcrelateddocument_target_set",
    )
    target_rfctobe = models.ForeignKey(
        RfcToBe,
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
            )
        ]

    def __str__(self):
        target = self.target_document if self.target_document else self.target_rfctobe
        return f"{self.relationship} relationship from {self.source} to {target}"


class RpcDocumentComment(models.Model):
    """Private RPC comment about a draft, RFC or RFC-to-be"""

    document = models.ForeignKey(
        "datatracker.Document", null=True, on_delete=models.PROTECT
    )
    rfc_to_be = models.ForeignKey(RfcToBe, null=True, on_delete=models.PROTECT)
    comment = models.TextField()
    by = models.ForeignKey("datatracker.DatatrackerPerson", on_delete=models.PROTECT)
    time = models.DateTimeField(default=timezone.now)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(document__isnull=True) ^ models.Q(rfc_to_be__isnull=True)
                ),
                name="rpcdocumentcomment_exactly_one_target",
                violation_error_message="exactly one of document or rfc_to_be must be set",
            )
        ]

    def __str__(self):
        target = self.document if self.document else self.rfc_to_be
        return f"RpcDocumentComment about {target} by {self.by} on {self.time:%Y-%m-%d}"


TAILWIND_COLORS= ["slate","gray","zinc","neutral","stone","red","orange","amber","yellow","lime","green","emerald","teal","cyan","sky","blue","indigo","violet","purple","fuchsia","pink","rose",]

class Label(models.Model):
    """Badges that can be put on other objects"""

    ### Will have to have LabelHistory on objects that have collections of labels
    ### That is, we need to compute when something had a label and how long

    slug = models.CharField(max_length=64)
    is_exception = models.BooleanField(default=False)
    color = models.CharField(
        max_length=7, default="purple", choices=zip(TAILWIND_COLORS, TAILWIND_COLORS)
    )
    history = HistoricalRecords()


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
