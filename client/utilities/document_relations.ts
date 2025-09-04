/**
 * Ported from https://github.com/ietf-tools/datatracker/blob/b3f2756f6b5d6adf853eb7779412950291169c38/ietf/static/js/document_relations.js#L106
 */

import * as d3 from "d3"

/**
 * These constants were calculated from DOM Bootstrap CSS variables
 * so they've been hardcoded to ensure same rendering
 * If you change them please test a lot.
 */
const font_size = 16
const line_height = font_size + 2
const font_family =
  '"Inter",system-ui,-apple-system,"Segoe UI",Roboto,"Helvetica Neue","Noto Sans","Liberation Sans",Arial,sans-serif,"Apple Color Emoji","Segoe UI Emoji","Segoe UI Symbol","Noto Color Emoji"'
const font = `${font_size}px ${font_family}`

const green = "#198754"
const blue = "#0d6efd"
const orange = "#fd7e14"
const cyan = "#0dcaf0"
const yellow = "#ffc107"
const red = "#dc3545"
const teal = "#20c997"
const white = "#fff"
const black = "#212529"
const gray400 = "#ced4da"

const link_color = {
  refinfo: green,
  refnorm: blue,
  replaces: orange,
  refunk: cyan,
  refold: yellow,
  downref: red,
} as const

const ref_type = {
  refinfo: "has an Informative reference to",
  refnorm: "has a Normative reference to",
  replaces: "replaces",
  refunk: "has an Unknown type of reference to",
  refold: "has an Undefined type of reference to",
  downref: "has a Downward reference (DOWNREF) to",
} as const

type Group = "" | "none" | "this group" | "other group"
type Level =
  | ""
  | "Informational"
  | "Experimental"
  | "Proposed Standard"
  | "Best Current Practice"
  | "Draft Standard"

type Line = {
  text: string
  width: number
}

export type Node = {
  id: string
  url?: string
  level?: Level
  group?: Group
  rfc?: boolean
  replaced?: boolean
  dead?: boolean
  expired?: boolean
  "post-wg"?: boolean
  x?: number
  y?: number
  r?: number
  lines?: Line[]
  stroke?: number
}

export type Link = {
  source: string | Node
  target: string | Node
  rel: keyof typeof ref_type
  replaced?: boolean
  "post-wg"?: boolean
  group?: Group
}

export type Data = {
  links: Link[]
  nodes: Node[]
}

function assert(val: unknown): asserts val {
  if (!val) {
    console.error(val)
    throw Error(`Assertion failed. See console.`)
  }
}

function assertData(val: unknown): asserts val is Data {
  assert(val)
  assert(typeof val === "object")
  assert("links" in val)
  assert("nodes" in val)
}

const DEFAULT_STROKE = 10

function stroke(d: Node) {
  if (
    d.level == "Informational" ||
    d.level == "Experimental" ||
    d.level == ""
  ) {
    return 1
  }
  if (d.level == "Proposed Standard") {
    return 4
  }
  if (d.level == "Best Current Practice") {
    return 8
  }
  // all others (draft/full standards)
  return 10
}

// code partially adapted from
// https://observablehq.com/@mbostock/fit-text-to-circle

function lines(text: string): Line[] {
  let line_width_0 = Infinity
  let line: Line = {
    // TODO: setting a default value is a change when porting to TS. This might be wrong
    text,
    width: line_width_0,
  }

  const lines: Line[] = []
  let sep = "-"
  let words = text.trim().split(/-/g)
  if (words.length == 1) {
    words = text.trim().split(/\s/g)
    sep = " "
  }
  words = words.map((x, i, a) => (i < a.length - 1 ? x + sep : x))
  if (words.length == 1) {
    words = text
      .trim()
      .split(/rfc/g)
      .map((x, i, a) => (i < a.length - 1 ? x + "RFC" : x))
  }
  const target_width = Math.sqrt(measure_width(text.trim()) * line_height)
  for (let i = 0, n = words.length; i < n; ++i) {
    let line_text = (line ? line.text : "") + words[i]
    let line_width = measure_width(line_text)
    if ((line_width_0 + line_width) / 2 < target_width) {
      line.width = line_width_0 = line_width
      line.text = line_text
    } else {
      line_width_0 = measure_width(words[i])
      line = { width: line_width_0, text: words[i] }
      lines.push(line)
    }
  }
  return lines
}

function measure_width(text: string) {
  const context = document.createElement("canvas").getContext("2d")

  if (!context) {
    console.error({ context })
    throw Error("Unable to get canvas context. See console for more")
  }
  context.font = font
  return context.measureText(text).width
}

function text_radius(lines: Line[]) {
  let radius = 0
  for (let i = 0, n = lines.length; i < n; ++i) {
    const dy = (Math.abs(i - n / 2) + 0.5) * line_height
    const dx = lines[i].width / 2
    radius = Math.max(radius, Math.sqrt(dx ** 2 + dy ** 2))
  }
  return radius
}

export function draw_graph(data: Data, group: Group) {
  // console.log(data);
  // let el = $.parseHTML('<svg class="w-100 h-100"></svg>');

  const zoom = d3
    .zoom<HTMLElement, unknown>()
    .scaleExtent([1 / 32, 32])
    .on("zoom", zoomed)

  const width = 1000
  const height = 1000

  const svgElement = document.createElement("svg")
  svgElement.className = "block w-full h-full"

  const svg = d3
    .select(svgElement)
    .style("font", font)
    .attr("text-anchor", "middle")
    .attr("dominant-baseline", "central")

    .attr('xmlns',  "http://www.w3.org/2000/svg")

    .attr("viewBox", [-width / 2, -height / 2, width, height])
    .call(zoom)

  svg
    .append("defs")
    .selectAll("marker")
    .data(new Set(data.links.map((d) => d.rel)))
    .join("marker")
    .attr("id", (d) => `marker-${d}`)
    .attr("viewBox", "0 -5 10 10")
    .attr("refX", 7.85)
    .attr("markerWidth", 4)
    .attr("markerHeight", 4)
    .attr("stroke-width", 0.2)
    .attr("stroke", black)
    .attr("orient", "auto")
    .attr("fill", (d) => link_color[d])
    .append("path")
    .attr("d", "M0,-5L10,0L0,5")

  const link = svg
    .append("g")
    .attr("fill", "none")
    .attr("stroke-width", 5)
    .selectAll("path")
    .data(data.links)
    .join("path")
    .attr("title", (d) => `${d.source} ${ref_type[d.rel]} ${d.target}`)
    .attr("marker-end", (d) => `url(#marker-${d.rel})`)
    .attr("stroke", (d) => link_color[d.rel])
    .attr("class", (d) => d.rel)

  const node = svg.append("g").selectAll("g").data(data.nodes).join("g")

  let max_r = 0
  const a = node
    .append("a")
    .attr("href", (d) => d.url ?? null)
    .attr("title", (d) => {
      const nodePropsWeCareAbout: (keyof Node)[] = [
        "replaced",
        "dead",
        "expired",
      ]
      let type = nodePropsWeCareAbout.filter((x) => d[x]).join(" ")
      if (type) {
        type += " "
      }
      if (d.level) {
        type += `${d.level} `
      }
      if (d.group != undefined && d.group != "none" && d.group != "") {
        const word = d.rfc ? "from" : "in"
        type += `group document ${word} ${d.group.toUpperCase()}`
      } else {
        type += "individual document"
      }
      const name = d.rfc ? d.id.toUpperCase() : d.id
      return `${name} is a${"aeiou".includes(type[0].toLowerCase()) ? "n" : ""} ${type}`
    })

  a.append("text")
    .attr("fill", (d) => (d.rfc || d.replaced ? white : black))
    .each((d) => {
      d.lines = lines(d.id)
      d.r = text_radius(d.lines)
      max_r = Math.max(d.r, max_r)
    })
    .selectAll("tspan")
    .data((d) => d.lines ?? [])
    .join("tspan")
    .attr("x", 0)
    .attr("y", (d, i, x) => (i - x.length / 2 + 0.5) * line_height)
    .text((d) => d.text)

  a.append("circle")
    .attr("stroke", black)
    .lower()
    .attr("fill", (d) => {
      if (d.rfc) {
        return green
      }
      if (d.replaced) {
        return orange
      }
      if (d.dead) {
        return red
      }
      if (d.expired) {
        return gray400
      }
      if (d["post-wg"]) {
        return teal
      }
      if (d.group == group || d.group == "this group") {
        return yellow
      }
      if (d.group == "") {
        return white
      }
      return cyan
    })
    .each((d) => (d.stroke = stroke(d)))
    .attr("r", (d) => {
      if (d.stroke === undefined) {
        console.error(d)
        throw Error("Expected stroke to be defined. See console.")
      }
      return (d.r ?? 0) + d.stroke / 2
    })
    .attr("stroke-width", (d) => {
      if (d.stroke === undefined) {
        console.error(d)
        throw Error("Expected stroke to be defined. See console.")
      }
      return d.stroke
    })
    .attr("stroke-dasharray", (d) => {
      if (d.group != "" || d.rfc) {
        return 0
      }
      return 4
    })

  const adjust = DEFAULT_STROKE / 2

  function ticked(
    // TSDOCS: "`this` parameters are fake parameters that come first in the parameter list of a function" -
    // https://www.typescriptlang.org/docs/handbook/functions.html#this-parameters
    this: d3.Simulation<d3.SimulationNodeDatum, undefined>,
  ) {
    // don't animate each tick
    for (let i = 0; i < 3; i++) {
      this.tick()
    }

    // code for straight links:
    // link.attr("d", function (d) {
    //     const dx = d.target.x - d.source.x;
    //     const dy = d.target.y - d.source.y;

    //     const path_len = Math.sqrt((dx * dx) +
    //         (dy * dy));

    //     const offx = (dx * d.target.r) /
    //         path_len;
    //     const offy = (dy * d.target.r) /
    //         path_len;
    //     return `
    //         M${d.source.x},${d.source.y}
    //         L${d.target.x - offx},${d.target.y - offy}
    //     `;
    // });

    // code for arced links:
    link.attr("d", (d) => {

      const { source, target } = d

      if (typeof source === "string" || typeof target === "string") {
        return ""
      }

      if (
        source.r === undefined ||
        source.stroke === undefined ||
        target.r === undefined ||
        target.stroke === undefined
      ) {
        return ""
      }

      if (
        source.x === undefined ||
        source.y === undefined ||
        target.x === undefined ||
        target.y === undefined
      ) {
        return ""
      }
      const r = Math.hypot(target.x - source.x, target.y - source.y)
      return `M${source.x},${source.y} A${r},${r} 0 0,1 ${target.x},${target.y}`
    })
    // TODO: figure out how to combine this with above
    link.attr("d", function (d) {
      if (!(this instanceof SVGPathElement)) {
        console.error({ notSvgPathElement: this })
        throw Error("Expected SVGPathElement. See console")
      }
      const pl = this.getTotalLength()
      const start = this.getPointAtLength(
        typeof d.source !== "string"
          ? (d.source.r ?? 0) + (d.source.stroke ?? 0)
          : 0,
      )

      const { source, target } = d

      if (typeof source === "string" || typeof target === "string") {
        return ""
      }

      if (
        source.r === undefined ||
        source.stroke === undefined ||
        target.r === undefined ||
        target.stroke === undefined
      ) {
        return ""
      }

      if (
        source.x === undefined ||
        source.y === undefined ||
        target.x === undefined ||
        target.y === undefined
      ) {
        return ""
      }

      const end = this.getPointAtLength(pl - target.r - target.stroke)
      const r = Math.hypot(target.x - source.x, target.y - source.y)

      return `M${start.x},${start.y} A${r},${r} 0 0,1 ${end.x},${end.y}`
    })

    node.selectAll("circle, text").attr("transform", (d) => {
      console.log("UNKNOWN VAL (d?.x/y)", d)
      // assertData(d)
      return `translate(${d.x}, ${d.y})`
    })

    // auto pan and zoom during simulation
    const _svgNode = svg.node()
    if (!_svgNode) {
      console.error({ svg, _svgNode })
      throw Error("Unable to get SVG Node from D3. See console.")
    }
    const svgNode = _svgNode as unknown as SVGGraphicsElement
    const bbox = svgNode.getBBox()
    svg.attr("viewBox", [
      bbox.x - adjust,
      bbox.y - adjust,
      bbox.width + 2 * adjust,
      bbox.height + 2 * adjust,
    ])
  }

  function zoomed({ transform }: { transform: string }) {
    link.attr("transform", transform)
    node.attr("transform", transform)
  }

  return [
    svg.node(),
    d3
      .forceSimulation()
      .nodes(data.nodes)
      .force(
        "link",
        d3
          .forceLink(data.links)
          .id((d) => {

            console.log("UNKNOWN VAL (d?.id)", d)
            return d.id
          })
          .distance(0),
        // .strength(1)
      )
      .force("charge", d3.forceManyBody().strength(-max_r))
      .force("collision", d3.forceCollide(1.25 * max_r))
      .force("x", d3.forceX())
      .force("y", d3.forceY())
      .stop()
      .on("tick", ticked),
    // .on("end", function () {
    //     $("#download-svg")
    //         .removeClass("disabled")
    //         .html('<i class="bi bi-download"></i> Download');
    // })
  ]

  // // See https://github.com/d3/d3-force/blob/main/README.md#simulation_tick
  // for (let i = 0, n = Math.ceil(Math.log(simulation.alphaMin()) /
  //         Math.log(1 - simulation.alphaDecay())); i <
  //     n; ++i) {
  //     simulation.tick();
  // }
  // ticked();
}
