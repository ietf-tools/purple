import { startCase } from "lodash-es";
import type { Cluster, RfcToBe } from "~/purple_client";

/**
 * These constants were calculated from DOM Bootstrap CSS variables
 * so they've been hardcoded to ensure same rendering
 * If you change them please test a lot.
 */
export const font_size = 14
export const line_height = font_size + 2
export const font_family =
  '"Inter",system-ui,-apple-system,"Segoe UI",Roboto,"Helvetica Neue","Noto Sans","Liberation Sans",Arial,sans-serif,"Apple Color Emoji","Segoe UI Emoji","Segoe UI Symbol","Noto Color Emoji"';
export const font = `${font_size}px ${font_family}`

export const green = "#198754"
export const blue = "#4d9efd"
export const purple = '#bb44bb'
export const orange = "#fd7e14"
export const cyan = "#0dcaf0"
export const yellow = "#ffc107"
export const red = "#ee828d"
export const teal = "#20c997"
export const white = "#fff"
export const black = "#212529"
export const gray200 = "#E5E7EB"
export const gray400 = "#ced4da"
export const gray800 = "#4e444a"

export type Relationship = 'refqueue' |
  'not-received' | // implicit 1g
  'not-received-2g' |
  'not-received-3g'

export const ref_type: Record<Relationship, string> = {
  refqueue: 'ref queue',
  'not-received': 'not received',
  'not-received-2g': 'not received 2g',
  'not-received-3g': 'not received 3g',
} as const;

export const getHumanReadableRelationshipName = (relationship: Relationship | string) => {
  return relationship in ref_type ? ref_type[relationship as keyof typeof ref_type] : relationship
}

export type Group = "" | "none" | "this group" | "other group"
export type Level =
  | ""
  | "Informational"
  | "Experimental"
  | "Proposed Standard"
  | "Best Current Practice"
  | "Draft Standard"

export const parseLevel = (maybeLevel: string): Level => {
  switch (maybeLevel) {
    case "":
      return ""
    case "inf":
    case "Informational":
      return "Informational"
    case "bcp":
    case "Best Current Practice":
      return "Best Current Practice"
    case "draft":
    case "Draft Standard":
      return "Draft Standard"
    case "exp":
    case "Experimental":
      return "Experimental"
    case "ps":
    case "Proposed Standard":
      return "Proposed Standard"
  }
  console.warn("Unable to parse level: ", maybeLevel)
  return ""
}

export const dispositionValues = [undefined, 'created', 'in_progress', 'published', 'withdrawn'] as const

type Disposition = (typeof dispositionValues)[number]

export const parseDisposition = (maybeDisposition: string | undefined | null): Disposition => {
  if (!maybeDisposition) return undefined

  switch (maybeDisposition) {
    case 'created':
    case 'in_progress':
    case 'published':
    case 'withdrawn':
      return maybeDisposition
  }
  console.warn("Unable to parse disposition: ", maybeDisposition)
  return undefined
}

export const parseRelationship = (maybeRelationship: string): Relationship => {
  switch (maybeRelationship) {
    case 'refqueue' satisfies Relationship:
    case 'not-received' satisfies Relationship:
    case 'not-received-2g' satisfies Relationship:
    case 'not-received-3g' satisfies Relationship:
      return maybeRelationship
  }
  console.warn("Unable to parse relationship: ", maybeRelationship)
  return 'not-received'
}

export type Line = {
  text: string
  width: number
  style?: string
};

export type Node = NodeParam & {
  x: number
  y: number
  r: number
  lines?: Line[]
  stroke?: number
};

export type Link = Omit<LinkParam, 'source' | 'target'> & {
  source: Node
  target: Node
  rel: Relationship
};

export type Data = {
  links: Link[]
  nodes: Node[]
};

export type NodeParam = {
  id: string
  url?: string
  isReceived?: boolean
  disposition: Disposition
  rfcNumber?: number | undefined,
  rfcToBe?: RfcToBe
};

export type LinkParam = {
  source: string;
  target: string;
  rel: Relationship;
};

export type DataParam = {
  links: LinkParam[]
  nodes: NodeParam[]
}

export const legendData: DataParam = {
  links: [
    { source: "draft-one-with-rfc", target: "draft-is-not-received", rel: "not-received" },
    { source: "draft-one-with-rfc", target: "draft-refnorm-target", rel: 'not-received-2g' },
    { source: "draft-one-with-rfc", target: "draft-refqueue-target", rel: 'not-received-3g' },
    { source: "draft-one-with-rfc", target: "draft-relinfo-target", rel: 'refqueue' },
    { source: "draft-one-with-rfc", target: "draft-withdrawnref-target", rel: 'not-received' },
    { source: "draft-one-with-rfc", target: 'draft-is-received', rel: 'not-received' },
  ],
  nodes: [
    { id: 'draft-one-with-rfc', rfcToBe: { rfcNumber: 100, disposition: '', labels: [], submittedFormat: '', title: '', boilerplate: '', stdLevel: '', stream: '', publicationStdLevel: '', publicationStream: '', authors: [], group: '' }, disposition: undefined },
    { id: 'draft-one-without-rfc', disposition: undefined },
    { id: 'draft-is-not-received', isReceived: false, disposition: undefined },
    { id: 'draft-is-received', isReceived: true, disposition: undefined },
    { id: 'draft-refnorm-target', isReceived: true, disposition: undefined },
    { id: 'draft-refqueue-target', isReceived: true, disposition: undefined },
    { id: 'draft-relinfo-target', isReceived: true, disposition: undefined },
    { id: 'draft-withdrawnref-target', isReceived: true, disposition: undefined },
  ],
};

export const complexClusterExample: Cluster = {
  "number": 535,
  "documents": [
    {
      "name": "draft-ietf-cose-key-thumbprint",
      "rfcNumber": 9679,
      "disposition": "published",
      "isReceived": true,
      "order": 1
    },
    {
      "name": "draft-ietf-suit-manifest",
      "disposition": "in_progress",
      "references": [
        {
          "id": 42,
          "relationship": "refqueue",
          "draftName": "draft-ietf-suit-manifest",
          "targetDraftName": "draft-ietf-suit-report"
        },
        {
          "id": 43,
          "relationship": "not-received",
          "draftName": "draft-ietf-suit-manifest",
          "targetDraftName": "draft-ietf-suit-update-management"
        },
        {
          "id": 44,
          "relationship": "refqueue",
          "draftName": "draft-ietf-suit-manifest",
          "targetDraftName": "draft-ietf-suit-trust-domains"
        },
        {
          "id": 45,
          "relationship": "refqueue",
          "draftName": "draft-ietf-suit-manifest",
          "targetDraftName": "draft-ietf-suit-firmware-encryption"
        },
        {
          "id": 46,
          "relationship": "refqueue",
          "draftName": "draft-ietf-suit-manifest",
          "targetDraftName": "draft-ietf-suit-mti"
        }
      ],
      "isReceived": true,
      "order": 2
    },
    {
      "name": "draft-ietf-suit-firmware-encryption",
      "disposition": "in_progress",
      "references": [
        {
          "id": 48,
          "relationship": "refqueue",
          "draftName": "draft-ietf-suit-firmware-encryption",
          "targetDraftName": "draft-ietf-suit-manifest"
        },
        {
          "id": 49,
          "relationship": "refqueue",
          "draftName": "draft-ietf-suit-firmware-encryption",
          "targetDraftName": "draft-ietf-suit-trust-domains"
        },
        {
          "id": 50,
          "relationship": "refqueue",
          "draftName": "draft-ietf-suit-firmware-encryption",
          "targetDraftName": "draft-ietf-suit-mti"
        },
        {
          "id": 117,
          "relationship": "not-received-2g",
          "draftName": "draft-ietf-suit-firmware-encryption",
          "targetDraftName": "draft-ietf-suit-update-management"
        },
        {
          "id": 123,
          "relationship": "not-received-3g",
          "draftName": "draft-ietf-suit-firmware-encryption",
          "targetDraftName": "draft-ietf-suit-update-management"
        }
      ],
      "isReceived": true,
      "order": 3
    },
    {
      "name": "draft-ietf-suit-mti",
      "disposition": "in_progress",
      "references": [
        {
          "id": 77,
          "relationship": "refqueue",
          "draftName": "draft-ietf-suit-mti",
          "targetDraftName": "draft-ietf-suit-manifest"
        },
        {
          "id": 119,
          "relationship": "not-received-2g",
          "draftName": "draft-ietf-suit-mti",
          "targetDraftName": "draft-ietf-suit-update-management"
        }
      ],
      "isReceived": true,
      "order": 4
    },
    {
      "name": "draft-ietf-suit-report",
      "disposition": "in_progress",
      "references": [
        {
          "id": 102,
          "relationship": "refqueue",
          "draftName": "draft-ietf-suit-report",
          "targetDraftName": "draft-ietf-suit-mti"
        },
        {
          "id": 103,
          "relationship": "refqueue",
          "draftName": "draft-ietf-suit-report",
          "targetDraftName": "draft-ietf-suit-manifest"
        },
        {
          "id": 120,
          "relationship": "not-received-2g",
          "draftName": "draft-ietf-suit-report",
          "targetDraftName": "draft-ietf-suit-update-management"
        },
        {
          "id": 125,
          "relationship": "not-received-3g",
          "draftName": "draft-ietf-suit-report",
          "targetDraftName": "draft-ietf-suit-update-management"
        }
      ],
      "isReceived": true,
      "order": 5
    },
    {
      "name": "draft-ietf-suit-trust-domains",
      "disposition": "in_progress",
      "references": [
        {
          "id": 75,
          "relationship": "refqueue",
          "draftName": "draft-ietf-suit-trust-domains",
          "targetDraftName": "draft-ietf-suit-manifest"
        },
        {
          "id": 76,
          "relationship": "refqueue",
          "draftName": "draft-ietf-suit-trust-domains",
          "targetDraftName": "draft-ietf-suit-firmware-encryption"
        },
        {
          "id": 118,
          "relationship": "not-received-2g",
          "draftName": "draft-ietf-suit-trust-domains",
          "targetDraftName": "draft-ietf-suit-update-management"
        },
        {
          "id": 124,
          "relationship": "not-received-3g",
          "draftName": "draft-ietf-suit-trust-domains",
          "targetDraftName": "draft-ietf-suit-update-management"
        }
      ],
      "isReceived": true,
      "order": 6
    },
    {
      "name": "draft-ietf-suit-update-management",
      "references": [
        {
          "relationship": "refqueue",
          "draftName": "draft-ietf-suit-update-management",
          "targetDraftName": "draft-ietf-suit-manifest"
        }
      ],
      "isReceived": false,
      "order": 7
    },
    {
      "name": "draft-ietf-suit-mud",
      "disposition": "in_progress",
      "references": [
        {
          "id": 47,
          "relationship": "refqueue",
          "draftName": "draft-ietf-suit-mud",
          "targetDraftName": "draft-ietf-suit-manifest"
        },
        {
          "id": 116,
          "relationship": "not-received-2g",
          "draftName": "draft-ietf-suit-mud",
          "targetDraftName": "draft-ietf-suit-update-management"
        }
      ],
      "isReceived": true,
      "order": 8
    }
  ],
  "isActive": true
}
