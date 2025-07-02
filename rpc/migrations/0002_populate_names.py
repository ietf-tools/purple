from django.db import migrations


def forward(apps, schema_editor):
    SourceFormatName = apps.get_model("rpc", "SourceFormatName")
    SourceFormatName.objects.create(
        slug="unknown",
        name="Source Format Unknown",
        desc="Don't know in which format the source was submitted",
    )
    SourceFormatName.objects.create(
        slug="xml-v3",
        name="RFCXML v3",
        desc="RFCXML v3",
    )
    SourceFormatName.objects.create(
        slug="xml-v2",
        name="RFCXML v2",
        desc="RFCXML v2",
    )
    SourceFormatName.objects.create(
        slug="md",
        name="Markdown",
        desc="Markdown",
    )
    SourceFormatName.objects.create(
        slug="txt",
        name="plaintext",
        desc="plaintext",
    )

    TlpBoilerplateChoiceName = apps.get_model("rpc", "TlpBoilerplateChoiceName")
    TlpBoilerplateChoiceName.objects.create(
        slug="unknown",
        name="TLP IPR Boilerplate Choice Unknown",
        desc="Don't know what ipr boilerplate was used",
    )
    TlpBoilerplateChoiceName.objects.create(
        slug="trust200902",
        name="trust200902",
        desc="Notice from the text of section 6.b of the TLP",
    )
    TlpBoilerplateChoiceName.objects.create(
        slug="noModificationTrust200902",
        name="noModificationTrust200902",
        desc="Notice from the text of sections 6.b and 6.c.i of the TLP "
        "(may be appropriate when republishing standards produced by a standards body "
        "other than the IETF, industry consortia, or companies, typically as an "
        "Informational "
        "RFC)",
    )
    TlpBoilerplateChoiceName.objects.create(
        slug="noDerivativesTrust200902",
        name="noDerivativesTrust200902",
        desc="Notice from the text of sections 6.b and 6.c.ii of the TLP "
        "(may be used on I-Ds intended to provide background information to educate"
        "and facilitate discussions within IETF working groups but not"
        "intended to be published as RFCs)",
    )
    TlpBoilerplateChoiceName.objects.create(
        slug="pre5378Trust200902",
        name="pre5378Trust200902",
        desc="Notice from the text of sections 6.b and 6.c.iii of the TLP "
        "(see TLP Modification of 15 Feb 2009 section of Trust FAQ)",
    )
    TlpBoilerplateChoiceName.objects.create(
        slug="trust200811",
        name="trust200811",
        desc="Historic value similar to trust200902",
    )
    TlpBoilerplateChoiceName.objects.create(
        slug="noModificationTrust200811",
        name="noModificationTrust200811",
        desc="Historic value similar to noModificationTrust200902",
    )
    TlpBoilerplateChoiceName.objects.create(
        slug="noDerivativesTrust200811",
        name="noDerivativesTrust200811",
        desc="Historic value similar to noDerivativesTrust200902",
    )

    DispositionName = apps.get_model("rpc", "DispositionName")
    DispositionName.objects.create(
        slug="created",
        name="Created",
        desc="RfcToBe has been created but has not yet entered the work queue",
    )
    DispositionName.objects.create(
        slug="in_progress", name="In Progress", desc="RfcToBe is a work in progress"
    )
    DispositionName.objects.create(
        slug="published", name="Published", desc="RfcToBe has been published as an RFC"
    )
    DispositionName.objects.create(
        slug="withdrawn", name="Withdrawn", desc="RfcToBe has been withdrawn"
    )


def reverse(apps, schema_editor):
    DispositionName = apps.get_model("rpc", "DispositionName")
    DispositionName.objects.all().delete()

    TlpBoilerplateChoiceName = apps.get_model("rpc", "TlpBoilerplateChoiceName")
    TlpBoilerplateChoiceName.objects.filter(
        slug__in=[
            "unknown",
            "trust200902",
            "noModificationTrust200902",
            "noDerivativesTrust200902",
            "pre5378Trust200902",
            "trust200811",
            "noModificationTrust200811",
            "noDerivativesTrust200811",
        ]
    ).delete()

    SourceFormatName = apps.get_model("rpc", "SourceFormatName")
    SourceFormatName.objects.filter(
        slug__in=["unknown", "xml-v3", "xml-v2", "md", "txt"]
    ).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("rpc", "0001_initial"),
    ]

    operations = [migrations.RunPython(forward, reverse)]
