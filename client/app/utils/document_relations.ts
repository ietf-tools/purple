/**
 * Ported from https://github.com/ietf-tools/datatracker/blob/b3f2756f6b5d6adf853eb7779412950291169c38/ietf/static/js/document_relations.js#L106
 */

import * as d3 from "d3"
import { black, blue, cyan, font, get_ref_type, gray400, green, line_height, orange, red, ref_type, teal, white, yellow, type Data, type DataParam, type Line, type Link, type LinkParam, type Node, type NodeParam, type Rel } from "./document_relations-utils"
import { getAncestors } from './dom'

const link_color: Record<Rel, string> = {
  "refqueue": green,
  "not-received": blue,
  "withdrawnref": orange,
  'refnorm':  teal,
  'relinfo': yellow
} as const

const get_link_color = (rel: Rel) => {
  const customColor: string | undefined = link_color[rel as keyof typeof link_color]
  if(customColor !== undefined) {
    return customColor
  }
  console.error(`Unable to find rel style ${JSON.stringify(rel)}`)
  return black
}

const get_name = (sourceOrTarget: Link["source"] | LinkParam["source"]): string => {
  if(typeof sourceOrTarget === 'string') {
    return sourceOrTarget
  }
  return sourceOrTarget.id
}

const DEFAULT_STROKE = 10

function stroke(d: NodeParam) {
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


type LinesProps= { id: string, rfcNumber?: number }
function lines({ id, rfcNumber }: LinesProps): Line[] {
  let line_width_0 = Infinity
  let text = id
  let line: Line = {
    text,
    width: line_width_0,
  }

  const lines: Line[] = []
  if(rfcNumber) {
    const newRfcNumber = `RFC ${rfcNumber}`
    lines.push({
      text: newRfcNumber,
      width: newRfcNumber.length * 10,
      style: 'font-weight: bold'
    })
  }
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
      line_width_0 = measure_width(words[i] ?? '')
      line = { width: line_width_0, text: words[i] ?? '' }
      lines.push(line)
    }
  }
  return lines
}

function measure_width(text: string): number {
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
    const line = lines[i]
    const dy = (Math.abs(i - n / 2) + 0.5) * line_height
    const dx = line ? line.width / 2 : 0
    radius = Math.max(radius, Math.sqrt(dx ** 2 + dy ** 2))
  }
  return radius
}

export type DrawGraphParameters = Parameters<typeof draw_graph>

export function draw_graph(data: DataParam, pushRouter: (path: string) => void) {
  const zoom = d3
    .zoom<SVGSVGElement, unknown>()
    .scaleExtent([1 / 32, 32])
    .on("zoom", zoomed)

  const width = 1000
  const height = 1000

  const svgElement = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  svgElement.setAttribute('class', "block w-full h-full")

  const svg = d3
    .select(svgElement)
    .style("font", font)
    .attr("text-anchor", "middle")
    .attr("dominant-baseline", "central")
    .attr('overflow', "visible")
    .attr("version", "1.1")
    .attr("viewBox", [-width / 2, -height / 2, width, height].join(" "))
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
    .attr("fill", (d) => get_link_color(d))
    .append("path")
    .attr("d", "M0,-5L10,0L0,5")

  const link = svg
    .append("g")
    .attr("fill", "none")
    .attr("stroke-width", 5)
    .selectAll("path")
    .data(data.links)
    .join("path")
    .attr("title", (d) => {
      return `${get_name(d.source)} ${get_ref_type(d.rel)} ${get_name(d.target)}`
    })
    .attr("marker-end", (d) => `url(#marker-${d.rel})`)
    .attr("stroke", (d) => get_link_color(d.rel))
    .attr("class", (d) => d.rel)

  const node = svg.append("g").selectAll("g").data(data.nodes).join("g")

  let max_r = 0
  const a = node
    .append("a")
    .attr("href", (d) => d.url ?? null)
    .attr("title", (d) => {
      const nodePropsWeCareAbout: (keyof NodeParam)[] = [
        "isReplaced",
        "isDead",
        "isExpired",
      ]
      let type = nodePropsWeCareAbout.filter((x) => d[x]).join(" ")
      if (type) {
        type += " "
      }
      if (d.level) {
        type += `${d.level} `
      }
      const typeZero = type[0] ?? ''
      if (d.group != undefined && d.group != "none" && d.group != "") {
        const word = d.isRfc ? "from" : "in"
        type += `group document ${word} ${d.group.toUpperCase()}`
      } else {
        type += "individual document"
      }
      const name = d.isRfc ? [d.rfcNumber, d.id.toUpperCase()].filter(Boolean).join(", ") : d.id
      return `${name} is a${"aeiou".includes(typeZero.toLowerCase()) ? "n" : ""} ${type}`
    }).on('click', (e) => {
      e.preventDefault()
      const { target } = e
      if (!(target instanceof SVGElement || target instanceof HTMLElement)) {
        console.error("Expected element but received ", target)
        return
      }
      const anchor = target.closest('a')
      if (!anchor) {
        console.error("Couldn't find parent of ", target, { parents: getAncestors(target)})
        return
      }
      const href = anchor.getAttribute('href')
      if (!href) {
        console.error("Closest <a> didn't have `href` attribute.", { parents: getAncestors(target)})
        return
      }
      console.log("SPA navigating to ", href)
      pushRouter(href)
    })

  a.append("text")
    .attr("fill", (d) => (d.isRfc || d.isReplaced ? white : black))
    .each((d) => {
      (d as Node).lines = lines({
        rfcNumber: d.rfcNumber,
        id: d.id,
      });
      (d as Node).r = text_radius((d as Node).lines!)
      max_r = Math.max((d as Node).r, max_r)
    })
    .selectAll("tspan")
    .data((d) => (d as Node).lines ?? [])
    .join("tspan")
    .attr("x", 0)
    .attr("style", (d) => d.style ?? '')
    .attr("y", (d, i, x) => (i - x.length / 2 + 0.5) * line_height)
    .text((d) => d.text)

  a.append("circle")
    .attr("stroke", black)
    .lower()
    .attr("fill", (d) => {
      if (d.isRfc) {
        return green
      }
      if (d.isReplaced) {
        return orange
      }
      if (d.isDead) {
        return red
      }
      if (d.isExpired) {
        return gray400
      }
      if (d["post-wg"]) {
        return teal
      }
      if (d.group == "") {
        return white
      }
      return cyan
    })
    .each((d) => ((d as Node).stroke = stroke(d)))
    .attr("r", (d) => {
      const dNode = d as Node
      if (dNode.stroke === undefined) {
        console.error(d)
        throw Error("Expected stroke to be defined. See console.")
      }
      return (dNode.r ?? 0) + dNode.stroke / 2
    })
    .attr("stroke-width", (d) => {
      const dNode = d as Node
      if (dNode.stroke === undefined) {
        console.error(d)
        throw Error("Expected stroke to be defined. See console.")
      }
      return dNode.stroke
    })
    .attr("stroke-dasharray", (d) => {
      if (d.group != "" || d.isRfc) {
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
      const dLink = d as unknown as Link
      const { source, target } = dLink

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
      const dLink = d as unknown as Link
      if(!(this instanceof SVGPathElement)) {
        console.error('SVGPathElement expected but was ', this)
        throw Error('Expected SVGPathElement. See console')
      }

      const pl = this.getTotalLength()
      const start = this.getPointAtLength(
        typeof d.source !== "string"
          ? (dLink.source.r ?? 0) + (dLink.source.stroke ?? 0)
          : 0,
      )

      const { source, target } = dLink

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
      const dNode = d as Node
      return `translate(${dNode.x}, ${dNode.y})`
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
      .nodes(data.nodes as Node[])
      .force(
        "link",
        d3
          .forceLink(data.links)
          .id((d) => {
            const dNode = d as Node
            return dNode.id
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
  ]
}
