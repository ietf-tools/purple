from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils import timezone

from rpc.models import RfcToBe


class Name(models.Model):
    slug = models.CharField(max_length=32, primary_key=True)
    name = models.CharField(max_length=255)
    desc = models.TextField(blank=True)
    used = models.BooleanField(default=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class AutoDateTimeField(models.DateTimeField):
    def pre_save(self, model_instance, add):
        value = getattr(model_instance, self.attname)
        if value is None:
            value = timezone.now()
        return value


class Errata(models.Model):
    """
    Model representing an erratum.
    """

    rfc_to_be = models.ForeignKey(
        RfcToBe, on_delete=models.PROTECT, related_name="errata"
    )
    status = models.ForeignKey(
        "Status",
        on_delete=models.PROTECT,
        default="reported",
        related_name="errata",
        db_column="status_slug",
    )
    type = models.ForeignKey(
        "Type", on_delete=models.PROTECT, related_name="errata", db_column="type_slug"
    )
    section = models.TextField(blank=True)
    orig_text = models.TextField(blank=True)
    corrected_text = models.TextField(blank=True)
    submitter_name = models.CharField(max_length=80, blank=True)
    submitter_email = models.EmailField(max_length=120, blank=True)
    submitter_dt_person = models.ForeignKey(
        "datatracker.DatatrackerPerson",
        null=True,
        on_delete=models.PROTECT,
        related_name="errata_submitter_dt_person",
    )
    notes = models.TextField(blank=True)
    submitted_at = models.DateField()
    posted_at = models.DateField(null=True)
    verifier_dt_person = models.ForeignKey(
        "datatracker.DatatrackerPerson",
        null=True,
        on_delete=models.PROTECT,
        related_name="errata_verifier_dt_person",
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = AutoDateTimeField()
    format = ArrayField(
        models.CharField(
            max_length=10, choices=[("HTML", "HTML"), ("PDF", "PDF"), ("TXT", "TXT")]
        ),
        default=list,
        blank=True,
        help_text="A list of formats. Possible values: 'HTML', 'PDF', and 'TXT'.",
    )

    def __str__(self):
        return f"Erratum {self.id} for RFC {self.rfc_to_be.id}"

    class Meta:
        verbose_name_plural = "Errata"


class Status(Name):
    class Meta:
        verbose_name_plural = "Statuses"

    pass


class Type(Name):
    pass


class Log(models.Model):
    """
    Model representing the log of changes or updates to errata.
    """

    errata = models.ForeignKey(
        "Errata", on_delete=models.PROTECT, related_name="logs_errata"
    )
    verifier_dt_person = models.ForeignKey(
        "datatracker.DatatrackerPerson",
        null=True,
        on_delete=models.PROTECT,
        related_name="logs_verifier_dt_person",
    )
    status = models.ForeignKey(
        "Status",
        on_delete=models.PROTECT,
        related_name="logs_status",
        db_column="status_slug",
    )
    type = models.ForeignKey(
        "Type",
        on_delete=models.PROTECT,
        related_name="logs_type",
        db_column="type_slug",
    )
    editor_dt_person = models.ForeignKey(
        "datatracker.DatatrackerPerson",
        on_delete=models.PROTECT,
        related_name="logs_editor_dt_person",
    )
    section = models.TextField(blank=True)
    orig_text = models.TextField(blank=True)
    corrected_text = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Log {self.id} for Erratum {self.errata_id}"


class AreaAssignment(models.Model):
    """
    Model representing area assignments for RFCs.
    """

    rfc_to_be = models.ForeignKey(
        RfcToBe, on_delete=models.PROTECT, related_name="area_assignment_rfc_to_be"
    )
    area_acronym = models.CharField(max_length=32)

    def __str__(self):
        return f"Area Assignment {self.area_acronym} for RCF {self.rfc_to_be_id}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["rfc_to_be", "area_acronym"],
                name="unique_rfc_to_be_area_acronym",
            )
        ]
