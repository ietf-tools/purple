/**
 * These constants were calculated from DOM Bootstrap CSS variables
 * so they've been hardcoded to ensure same rendering
 * If you change them please test a lot.
 */
export const font_size = 16;
export const line_height = font_size + 2;
export const font_family =
  '"Inter",system-ui,-apple-system,"Segoe UI",Roboto,"Helvetica Neue","Noto Sans","Liberation Sans",Arial,sans-serif,"Apple Color Emoji","Segoe UI Emoji","Segoe UI Symbol","Noto Color Emoji"';
export const font = `${font_size}px ${font_family}`;

export const green = "#198754";
export const blue = "#0d6efd";
export const orange = "#fd7e14";
export const cyan = "#0dcaf0";
export const yellow = "#ffc107";
export const red = "#dc3545";
export const teal = "#20c997";
export const white = "#fff";
export const black = "#212529";
export const gray400 = "#ced4da";

export type Rel = 'refqueue' | 'not-received' | 'withdrawnref' | 'relinfo' | 'refnorm'

export const ref_type: Record<Rel, string> = {
  refqueue: 'has ref queue to',
  'not-received': 'has not received to',
  withdrawnref: 'has withdrawn ref to',
  refnorm: 'has ref norm to',
  relinfo: 'has rel info to'
} as const;

export const get_ref_type = (key: string) => {
  return key in ref_type ? ref_type[key as keyof typeof ref_type] : key
}

export type Group = "" | "none" | "this group" | "other group";
export type Level =
  | ""
  | "Informational"
  | "Experimental"
  | "Proposed Standard"
  | "Best Current Practice"
  | "Draft Standard";

export type Line = {
  text: string;
  width: number;
};

export type Node = NodeParam & {
  x: number;
  y: number;
  r: number;
  lines?: Line[];
  stroke?: number;
};

export type Link = Omit<LinkParam, 'source' | 'target'> & {
  source: Node;
  target: Node;
  rel: Rel;
  replaced?: boolean;
  "post-wg"?: boolean;
  group?: Group;
};

export type Data = {
  links: Link[];
  nodes: Node[];
};

export type NodeParam = {
  id: string;
  url?: string;
  level?: Level;
  group?: string;
  rfc?: boolean;
  replaced?: boolean;
  dead?: boolean;
  expired?: boolean;
  "post-wg"?: boolean;
};

export type LinkParam = {
  source: string;
  target: string;
  rel: Rel;
};

export type DataParam = {
  links: LinkParam[]
  nodes: NodeParam[]
}

export const legendData: DataParam = {
  links: [
    {
      source: "Individual submission",
      target: "Replaced",
      rel: "not-received" satisfies Rel,
    },
    {
      source: "Individual submission",
      target: "IESG or RFC queue",
      rel: "refqueue" satisfies Rel,
    },
    {
      source: "Expired",
      target: "RFC published",
      rel: "not-received" satisfies Rel,
    },
    {
      source: "Product of other group",
      target: "IESG or RFC queue",
      rel: "refqueue" satisfies Rel,
    },
    {
      source: "Product of this group",
      target: "Product of other group",
      rel: "withdrawnref" satisfies Rel,
    },
    {
      source: "Product of this group",
      target: "Expired",
      rel: "withdrawnref" satisfies Rel,
    },
  ],
  nodes: [
    {
      id: "Individual submission",
      level: "Informational",
      group: "",
    },
    {
      id: "Replaced",
      level: "Experimental",
      replaced: true,
    },
    {
      id: "IESG or RFC queue",
      level: "Proposed Standard",
      "post-wg": true,
    },
    {
      id: "Product of other group",
      level: "Best Current Practice",
      group: "other group",
    },
    {
      id: "Expired",
      level: "Informational",
      group: "this group",
      expired: true,
    },
    {
      id: "Product of this group",
      level: "Proposed Standard",
      group: "this group",
    },
    {
      id: "RFC published",
      level: "Draft Standard",
      group: "other group",
      rfc: true,
    },
  ],
};

export const test_data2: DataParam = {
  links: [
    {
      source: "rfc7340",
      target: "draft-cooper-iab-secure-origin",
      rel: "refqueue" satisfies Rel,
    },
    {
      source: "rfc7340",
      target: "draft-rosenberg-sip-rfc4474-concerns",
      rel: "refqueue" satisfies Rel,
    },
    {
      source: "rfc7340",
      target: "draft-jennings-vipr-overview",
      rel: "refqueue" satisfies Rel,
    },
    {
      source: "rfc7340",
      target: "draft-peterson-sipping-retarget",
      rel: "refqueue" satisfies Rel,
    },
    {
      source: "rfc7375",
      target: "draft-peterson-sipping-retarget",
      rel: "refqueue" satisfies Rel,
    },
    {
      source: "rfc9027",
      target: "draft-rosen-stir-emergency-calls",
      rel: "withdrawnref" satisfies Rel,
    },
    {
      source: "rfc8224",
      target: "draft-peterson-sipping-retarget",
      rel: "refqueue" satisfies Rel,
    },
    {
      source: "rfc8816",
      target: "draft-ietf-modern-teri",
      rel: "refqueue" satisfies Rel,
    },
    {
      source: "draft-wendt-stir-vesper",
      target: "draft-wendt-acme-authority-token-jwtclaimcon",
      rel: "refqueue" satisfies Rel,
    },
    {
      source: "rfc8816",
      target: "draft-jennings-vipr-overview",
      rel: "withdrawnref" satisfies Rel,
    },
    {
      source: "rfc8816",
      target: "draft-privacy-pass",
      rel: "refqueue" satisfies Rel,
    },
    {
      source: "draft-wendt-stir-vesper-use-cases",
      target: "draft-wendt-stir-vesper",
      rel: "refqueue" satisfies Rel,
    },
    {
      source: "draft-wendt-stir-vesper-use-cases",
      target: "draft-wendt-acme-authority-token-jwtclaimcon",
      rel: "refqueue" satisfies Rel,
    },
    {
      source: "draft-wendt-stir-vesper-use-cases",
      target: "draft-wendt-stir-certificate-transparency",
      rel: "refqueue" satisfies Rel,
    },
    {
      source: "draft-wendt-stir-vesper-use-cases",
      target: "draft-ietf-stir-certificates-shortlived",
      rel: "withdrawnref" satisfies Rel,
    },
    {
      source: "rfc8224",
      target: "draft-rosenberg-sip-rfc4474-concerns",
      rel: "not-received" satisfies Rel,
    },
    {
      source: "rfc8224",
      target: "draft-ietf-iri-comparison",
      rel: "not-received" satisfies Rel,
    },
    {
      source: "rfc8224",
      target: "draft-kaplan-stir-cider",
      rel: "withdrawnref" satisfies Rel,
    },
    {
      source: "rfc9475",
      target: "draft-peterson-stir-rfc4916-update",
      rel: "refqueue" satisfies Rel,
    },
    {
      source: "draft-ietf-stir-rfc4916-update",
      target: "rfc3325",
      rel: "refqueue" satisfies Rel,
    },
    {
      source: "draft-ietf-stir-certificates-ocsp",
      target: "rfc5912",
      rel: "refqueue" satisfies Rel,
    },
    {
      source: "draft-ietf-stir-rfc4916-update",
      target: "draft-peterson-stir-rfc4916-update",
      rel: "refqueue" satisfies Rel,
    },
    {
      source: "draft-ietf-stir-servprovider-oob",
      target: "rfc8816",
      rel: "not-received" satisfies Rel,
    },
    {
      source: "draft-ietf-stir-certificates-ocsp",
      target: "draft-ietf-stir-certificates-shortlived",
      rel: "not-received" satisfies Rel,
    },
    {
      source: "draft-ietf-stir-certificates-ocsp",
      target: "draft-ietf-tls-rfc8446bis",
      rel: "refqueue" satisfies Rel,
    },
  ],
  nodes: [
    {
      id: "rfc7375",
      rfc: true,
      "post-wg": true,
      expired: false,
      replaced: false,
      group: "stir",
      url: "/doc/draft-ietf-stir-threats/",
      level: "Informational",
    },
    {
      id: "draft-cooper-iab-secure-origin",
      rfc: false,
      "post-wg": false,
      expired: true,
      replaced: false,
      group: "",
      url: "/doc/draft-cooper-iab-secure-origin/",
      level: "",
    },
    {
      id: "rfc8816",
      rfc: true,
      "post-wg": true,
      expired: false,
      replaced: false,
      group: "stir",
      url: "/doc/draft-ietf-stir-oob/",
      level: "Informational",
    },
    {
      id: "rfc5912",
      rfc: true,
      "post-wg": true,
      expired: false,
      replaced: false,
      group: "pkix",
      url: "/doc/rfc5912/",
      level: "Informational",
    },
    {
      id: "draft-wendt-stir-certificate-transparency",
      rfc: false,
      "post-wg": false,
      expired: false,
      replaced: false,
      group: "",
      url: "/doc/draft-wendt-stir-certificate-transparency/",
      level: "",
    },
    {
      id: "draft-ietf-stir-servprovider-oob",
      rfc: false,
      "post-wg": true,
      expired: false,
      replaced: false,
      group: "stir",
      url: "/doc/draft-ietf-stir-servprovider-oob/",
      level: "Proposed Standard",
    },
    {
      id: "draft-rosen-stir-emergency-calls",
      rfc: false,
      "post-wg": false,
      expired: true,
      replaced: false,
      group: "",
      url: "/doc/draft-rosen-stir-emergency-calls/",
      level: "",
    },
    {
      id: "draft-rosenberg-sip-rfc4474-concerns",
      rfc: false,
      "post-wg": false,
      expired: true,
      replaced: false,
      group: "",
      url: "/doc/draft-rosenberg-sip-rfc4474-concerns/",
      level: "",
    },
    {
      id: "draft-ietf-stir-certificates-shortlived",
      rfc: false,
      "post-wg": false,
      expired: false,
      replaced: false,
      group: "stir",
      url: "/doc/draft-ietf-stir-certificates-shortlived/",
      level: "",
    },
    {
      id: "draft-wendt-stir-vesper",
      rfc: false,
      "post-wg": false,
      expired: false,
      replaced: false,
      group: "",
      url: "/doc/draft-wendt-stir-vesper/",
      level: "",
    },
    {
      id: "rfc8816",
      rfc: true,
      "post-wg": true,
      expired: false,
      replaced: false,
      group: "stir",
      url: "/doc/rfc8816/",
      level: "Informational",
    },
    {
      id: "draft-ietf-iri-comparison",
      rfc: false,
      "post-wg": false,
      expired: true,
      replaced: false,
      group: "",
      url: "/doc/draft-ietf-iri-comparison/",
      level: "Proposed Standard",
    },
    {
      id: "rfc9027",
      rfc: true,
      "post-wg": true,
      expired: false,
      replaced: false,
      group: "stir",
      url: "/doc/draft-ietf-stir-rph-emergency-services/",
      level: "Proposed Standard",
    },
    {
      id: "rfc9475",
      rfc: true,
      "post-wg": true,
      expired: false,
      replaced: false,
      group: "stir",
      url: "/doc/draft-ietf-stir-messaging/",
      level: "Proposed Standard",
    },
    {
      id: "draft-privacy-pass",
      rfc: false,
      "post-wg": false,
      expired: true,
      replaced: false,
      group: "",
      url: "/doc/draft-privacy-pass/",
      level: "",
    },
    {
      id: "draft-wendt-acme-authority-token-jwtclaimcon",
      rfc: false,
      "post-wg": false,
      expired: false,
      replaced: false,
      group: "",
      url: "/doc/draft-wendt-acme-authority-token-jwtclaimcon/",
      level: "",
    },
    {
      id: "draft-peterson-stir-rfc4916-update",
      rfc: false,
      "post-wg": false,
      expired: false,
      replaced: true,
      group: "",
      url: "/doc/draft-peterson-stir-rfc4916-update/",
      level: "",
    },
    {
      id: "draft-ietf-modern-teri",
      rfc: false,
      "post-wg": false,
      expired: true,
      replaced: false,
      group: "modern",
      url: "/doc/draft-ietf-modern-teri/",
      level: "",
    },
    {
      id: "draft-ietf-stir-rfc4916-update",
      rfc: false,
      "post-wg": true,
      expired: false,
      replaced: false,
      group: "stir",
      url: "/doc/draft-ietf-stir-rfc4916-update/",
      level: "Proposed Standard",
    },
    {
      id: "draft-jennings-vipr-overview",
      rfc: false,
      "post-wg": false,
      expired: true,
      replaced: false,
      group: "",
      url: "/doc/draft-jennings-vipr-overview/",
      level: "",
    },
    {
      id: "draft-ietf-tls-rfc8446bis",
      rfc: false,
      "post-wg": true,
      expired: false,
      replaced: false,
      group: "tls",
      url: "/doc/draft-ietf-tls-rfc8446bis/",
      level: "Proposed Standard",
    },
    {
      id: "rfc8224",
      rfc: true,
      "post-wg": true,
      expired: false,
      replaced: false,
      group: "stir",
      url: "/doc/draft-ietf-stir-rfc4474bis/",
      level: "Proposed Standard",
    },
    {
      id: "rfc3325",
      rfc: true,
      "post-wg": true,
      expired: false,
      replaced: false,
      group: "sip",
      url: "/doc/rfc3325/",
      level: "Informational",
    },
    {
      id: "rfc7340",
      rfc: true,
      "post-wg": true,
      expired: false,
      replaced: false,
      group: "stir",
      url: "/doc/draft-ietf-stir-problem-statement/",
      level: "Informational",
    },
    {
      id: "draft-kaplan-stir-cider",
      rfc: false,
      "post-wg": false,
      expired: true,
      replaced: false,
      group: "",
      url: "/doc/draft-kaplan-stir-cider/",
      level: "",
    },
    {
      id: "draft-wendt-stir-vesper-use-cases",
      rfc: false,
      "post-wg": false,
      expired: false,
      replaced: false,
      group: "",
      url: "/doc/draft-wendt-stir-vesper-use-cases/",
      level: "",
    },
    {
      id: "draft-peterson-sipping-retarget",
      rfc: false,
      "post-wg": false,
      expired: true,
      replaced: false,
      group: "",
      url: "/doc/draft-peterson-sipping-retarget/",
      level: "",
    },
    {
      id: "draft-ietf-stir-certificates-ocsp",
      rfc: false,
      "post-wg": true,
      expired: false,
      replaced: false,
      group: "stir",
      url: "/doc/draft-ietf-stir-certificates-ocsp/",
      level: "Proposed Standard",
    },
  ],
};
