# Copyright The IETF Trust 2023-2024, All Rights Reserved
from django.db.models import F, Max, Subquery, Value
from django.db.models.functions import Coalesce

from datatracker.models import Document

from .models import Cluster, ClusterMember, DumpInfo, RfcToBe, UnusableRfcNumber


class VersionInfo:
    """Application version information model"""

    version = "version-access-not-yet-implemented"

    def __init__(self):
        # If we have a DumpInfo, populate the dump_timestamp property
        dumpinfo = DumpInfo.objects.order_by("-timestamp").first()
        if dumpinfo is not None:
            self.dump_timestamp = dumpinfo.timestamp


def next_rfc_number(count=1) -> list[int]:
    """Find the next count contiguous available RFC numbers"""
    # In the worst-case, we can always use (n + 1) to (n + count) where n is the last
    # unavailable number.
    last_unavailable_number = max(
        (
            UnusableRfcNumber.objects.aggregate(Max("number"))["number__max"] or 0,
            RfcToBe.objects.aggregate(Max("rfc_number"))["rfc_number__max"] or 0,
            # todo get last RFC number from datatracker
        )
    )
    # todo consider holes in the unavailable number sequence
    return list(range(last_unavailable_number + 1, last_unavailable_number + 1 + count))


def create_rpc_related_document(relationship_slug, source, target_draft_name):
    from .serializers import CreateRpcRelatedDocumentSerializer

    data = {
        "relationship": relationship_slug,
        "source": source,
        "target_draft_name": target_draft_name,
    }

    serializer = CreateRpcRelatedDocumentSerializer(data=data)
    if serializer.is_valid(raise_exception=True):
        return serializer.save()
    return None


def create_cluster() -> Cluster:
    """Create a new Cluster with the next available number."""
    next_number = Coalesce(
        Subquery(
            Cluster.objects.order_by("-number")
            .annotate(next_num=F("number") + Value(1))
            .values("next_num")[:1]
        ),
        Value(1),
    )
    return Cluster.objects.create(number=next_number)


def add_doc_to_cluster(cluster: Cluster, doc: Document) -> None:
    """Add a Document to a Cluster, skipping if already a member of any cluster."""
    if ClusterMember.objects.filter(doc=doc).exists():
        return

    annotated_clusters = Cluster.objects.annotate(
        next_order=Max("clustermember__order", default=0) + Value(1)
    )
    doc.clustermember_set.create(
        cluster=cluster,
        order=Subquery(
            annotated_clusters.filter(pk=cluster.pk).values_list("next_order")
        ),
    )


def get_or_create_draft_by_name(draft_name, *, rpcapi):
    """Get a datatracker Document for a draft given its name

    n.b., creates a Document object if needed
    """
    drafts = rpcapi.get_drafts_by_names([draft_name])

    draft_info = next(
        (d for d in drafts if getattr(d, "name", None) == draft_name), None
    )
    if draft_info is None:
        return None
    # todo manage updates if the details below change before draft reaches pubreq!
    document, _ = Document.objects.get_or_create(
        datatracker_id=draft_info.id,
        defaults={
            "name": draft_info.name,
            "rev": draft_info.rev,
            "title": draft_info.title,
            "stream": "" if draft_info.stream is None else draft_info.stream,
            "pages": draft_info.pages,
            "intended_std_level": getattr(draft_info, "intended_std_level", "") or "",
        },
    )
    return document
