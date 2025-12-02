export const getAncestors = (elm: HTMLElement | SVGElement) => {
  const parents: Element[] = []
  let a: HTMLElement | SVGElement | null = elm
  while (a) {
    parents.unshift(a)
    a = a.parentElement
  }
  return parents
}
