/**
 * Vue's `class=""` attribute can take strings, arrays, objects, arrays of objects, etc
 * but the typing is just `any`. Use this instead for `class` props.
 *
 * Named VueStyleClass to distinguish from the word "class" used in the context of
 * `class` object-template-like programming.
 **/
export type VueStyleClass =
  | string
  | (string | boolean | undefined)[]
  | Record<string, boolean | undefined>

export const getVNodeText = (vnode: unknown): string => {
  if (!vnode) {
    return ''
  }

  if (typeof vnode === 'string') {
    return vnode
  }

  if (Array.isArray(vnode)) {
    return vnode.map(getVNodeText).join('')
  }

  if (vnode && typeof vnode === 'object' && 'children' in vnode) {
    const { children } = vnode
    if (typeof children === 'string') {
      return children
    } else if (typeof children === 'function') {
      return getVNodeText(children())
    } else if (
      children &&
      typeof children === 'object' &&
      'default' in children &&
      typeof children.default === 'function'
    ) {
      return getVNodeText(children.default())
    } else if (Array.isArray(children)) {
      return children
        .map((item) => getVNodeText(item as ReturnType<typeof h>))
        .join('')
    }
  }

  if(vnode && typeof vnode === 'function') {
    return getVNodeText(vnode())
  }

  return ''
}
