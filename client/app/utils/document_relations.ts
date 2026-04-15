/**
 * Ported from https://github.com/ietf-tools/datatracker/blob/b3f2756f6b5d6adf853eb7779412950291169c38/ietf/static/js/document_relations.js#L106
 */
import * as d3 from "d3"
import { black, font, getHumanReadableRelationshipName, green, line_height, orange, red, teal, type DataParam, type Line, type Link, type LinkParam, type Node, type Relationship } from "./document_relations-utils"
import { getAncestors } from './dom'

const TOOLTIP_BUFFER_Y = 5

const link_color: Record<Relationship, string> = {
  "refqueue": green,
  "not-received": red,
  "not-received-2g": orange,
  'not-received-3g': teal,
} as const

const getLinkColor = (rel: Relationship) => {
  const customColor: string | undefined = link_color[rel as keyof typeof link_color]
  if (customColor !== undefined) {
    return customColor
  }
  console.error(`Unable to find rel style ${JSON.stringify(rel)}`)
  return black
}

const DEFAULT_STROKE = 10

function textRadius(lines: Line[]) {
  let radius = 0
  for (let i = 0, n = lines.length; i < n; ++i) {
    const line = lines[i]
    const dy = (Math.abs(i - n / 2) + 0.5) * line_height
    const dx = line ? line.width / 2 : 0
    radius = Math.max(radius, Math.sqrt(dx ** 2 + dy ** 2))
  }
  return radius
}

export type DrawGraphParameters = Parameters<typeof drawGraph>

export type SetTooltip = (props?: undefined | { text: string[], position: [number, number] }) => void

type Props = {
  data: DataParam,
  pushRouter: (path: string) => void,
  colorMode: "light" | "dark",
  setTooltip: SetTooltip
}

export function drawGraph({ data: _data, pushRouter, colorMode, setTooltip }: Props) {
  const data = normalizeData(_data)

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
    .attr("fill", (d) => getLinkColor(d))
    .append("path")
    .attr("d", "M0,-5L10,0L0,5")

  const LINE_STROKE_WIDTH = 5

  // links between circles
  const link = svg
    .append("g")
    .attr("fill", "none")
    .attr("stroke-width", LINE_STROKE_WIDTH)
    .selectAll("path")
    .data(data.links)
    .join("path")
    .attr("title", (d) => {
      return getLinkTitle(d)
    })
    .attr("stroke-dasharray", (d) => {
      switch (d.rel) {
        case 'not-received-2g':
        case 'not-received-3g':
          return 4
      }
      return 0
    })
    .attr('tabindex', 0)
    .on("focus mouseover", function (e, d) {
      d3.select(this).transition()
        .duration(200)
        .attr("opacity", 0.5)

      e.preventDefault()
      const { target } = e
      if (!(target instanceof SVGElement || target instanceof HTMLElement)) {
        console.error("Expected element but received ", target)
        return
      }
      const group = target.closest('g')
      if (!(group instanceof SVGElement)) {
        console.error("Expected svg element but received ", group, ' from ', target)
        return
      }
      const boundingClientRect = group.getBoundingClientRect()

      setTooltip({
        text: getLinkTitle(d),
        position: [boundingClientRect.left + window.scrollX, boundingClientRect.top + window.scrollY - TOOLTIP_BUFFER_Y]
      })
    })
    .on('blur mouseout', function () {
      d3.select(this).transition()
        .duration(200)
        .attr("opacity", 1)

      setTooltip()
    })
    .attr("marker-end", (d) => `url(#marker-${d.rel})`)
    .attr("stroke", (d) => getLinkColor(d.rel))
    .attr("class", (d) => d.rel)

  const node = svg.append("g").selectAll("g").data(data.nodes).join("g")

  let max_r = 0
  const a = node
    .append("a")
    .attr("href", (d) => d.url ??
      '#' // we need a href (eg '#') to be focusable even if it doesn't have a d.url so that the `title` is available
    )
    .attr("title", (d) => getCircleTheme(d).tooltip?.join(" ") ?? null)
    .on("focus mouseover", function (e, d) {
      e.preventDefault()
      const { target } = e
      if (!(target instanceof SVGElement || target instanceof HTMLElement)) {
        console.error("Expected element but received ", target)
        return
      }

      const anchor = target.closest('a')
      if (!(anchor instanceof SVGElement || anchor instanceof HTMLElement)) {
        console.error("Expected svg element but received ", anchor, ' from ', target)
        return
      }
      const boundingClientRect = anchor.getBoundingClientRect()

      const { tooltip } = getCircleTheme(d)

      if (tooltip) {
        console.log("has tooltip", tooltip)
        setTooltip({
          text: tooltip,
          position: [boundingClientRect.left + window.scrollX, boundingClientRect.top + window.scrollY - TOOLTIP_BUFFER_Y]
        })
      } else {
        console.log("hide tooltip?")
        setTooltip()
      }
    })
    .on('blur mouseout', () => {
      setTooltip()
    })
    .on('click', (e) => {
      e.preventDefault()
      const { target } = e
      if (!(target instanceof SVGElement || target instanceof HTMLElement)) {
        console.error("Expected element but received ", target)
        return
      }
      const anchor = target.closest('a')
      if (!anchor) {
        console.error("Couldn't find parent of ", target, { parents: getAncestors(target) })
        return
      }
      const href = anchor.getAttribute('href')
      if (!href) {
        console.error("Closest <a> didn't have `href` attribute.", { parents: getAncestors(target) })
        return
      }
      if (href === '#') {
        console.info('Ignoring href navigation to empty internal link ie "#"')
        return
      }
      console.log("SPA navigating to ", href)
      pushRouter(href)
    })

  a.append("text")
    .attr("fill", (d) => getCircleTheme(d).textColor)
    .each((d) => {
      (d as Node).lines = getCircleTheme(d).text;
      (d as Node).r = textRadius((d as Node).lines!)
      max_r = Math.max((d as Node).r, max_r)
    })
    .selectAll("tspan")
    .data((d) => (d as Node).lines ?? [])
    .join("tspan")
    .attr("x", 0)
    .attr("style", (d) => d.style ?? '')
    .attr("y", (d, i, x) => (i - x.length / 2 + 0.5) * line_height)
    .text((d) => {
      return d.text
    })

  a.append("circle")
    .attr("stroke", black)
    .lower()
    .attr("fill", (d) => {
      return getCircleTheme(d).fill
    })
    .each((d) => {
      (d as Node).stroke = getCircleTheme(d).strokeWidth
    })
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
      const { strokeStyle } = getCircleTheme(d)
      switch (strokeStyle) {
        case 'dotted':
          return 4
        case 'solid':
          return 0
      }
      assertNever(strokeStyle)
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
      if (!(this instanceof SVGPathElement)) {
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
          .distance(0)
          .strength(0.1)
      )
      .force("charge", d3.forceManyBody().strength(-max_r))
      .force("collision", d3.forceCollide(1.25 * max_r))
      .force("x", d3.forceX())
      .force("y", d3.forceY())
      .stop()
      .on("tick", ticked),
  ]
}

const getLinkTitle = (d: LinkParam): string[] => {
  return [
    getHumanReadableRelationshipName(d.rel),
  ]
}
