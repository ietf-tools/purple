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
export const blue = "#0d6efd"
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

export type Relationship = 'refqueue' | 'not-received' | 'withdrawnref' | 'relinfo' | 'refnorm'

export const ref_type: Record<Relationship, string> = {
  refqueue: 'has ref queue to',
  'not-received': 'has not received to',
  withdrawnref: 'has withdrawn ref to',
  refnorm: 'has ref norm to',
  relinfo: 'has rel info to'
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

type Disposition = undefined | 'assigned' | 'in_progress' | 'done'

export const parseDisposition = (maybeDisposition: string | undefined | null): Disposition => {
  if (!maybeDisposition) return undefined

  switch (maybeDisposition) {
    case 'assigned':
    case 'in_progress':
    case 'done':
      return maybeDisposition
  }
  console.warn("Unable to parse disposition: ", maybeDisposition)
  return undefined
}

export const parseRelationship = (maybeRelationship: string): Relationship => {
  switch (maybeRelationship) {
    case 'refqueue':
    case 'not-received':
    case 'withdrawnref':
    case 'relinfo':
    case 'refnorm':
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
  rfcNumber?: number
  isRfc: boolean
  isReceived?: boolean
  disposition: Disposition
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
    { source: "draft-one-with-rfc", target: "draft-is-not-received", rel: "not-received"},
    { source: "draft-one-with-rfc", target: "draft-refnorm-target", rel: "refnorm"},
    { source: "draft-one-with-rfc", target: "draft-refqueue-target", rel: "refqueue"},
    { source: "draft-one-with-rfc", target: "draft-relinfo-target", rel: "relinfo"},
    { source: "draft-one-with-rfc", target: "draft-withdrawnref-target", rel: "withdrawnref"},
    { source: "draft-one-with-rfc", target: 'draft-is-received', rel: 'refnorm'},
  ],
  nodes: [
    { id: 'draft-one-with-rfc', isRfc: true, rfcNumber: 100, disposition: undefined },
    { id: 'draft-one-without-rfc', isRfc: false, disposition: undefined },
    { id: 'draft-is-not-received', isRfc: false, isReceived: false, disposition: undefined },
    { id: 'draft-is-received', isRfc: false, isReceived: true, disposition: undefined },
    { id: 'draft-refnorm-target', isRfc: false, isReceived: true, disposition: undefined },
    { id: 'draft-refqueue-target', isRfc: false, isReceived: true, disposition: undefined },
    { id: 'draft-relinfo-target', isRfc: false, isReceived: true, disposition: undefined },
    { id: 'draft-withdrawnref-target', isRfc: false, isReceived: true, disposition: undefined },
  ],
};
