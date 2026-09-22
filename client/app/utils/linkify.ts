import { LinkifyIt } from 'linkify-it'

export type TextPart = { text: string; href?: string }

// Bare domains ("rfc-editor.org/errata") are linked; e-mail addresses are not,
// so an address in a note stays plain text.
const linkifier = new LinkifyIt({ fuzzyLink: true, fuzzyEmail: false })

/**
 * Split plain text into runs of text and URLs so the URLs can be rendered as
 * links without interpreting the text as HTML. Bare domains keep their typed
 * text but link to a normalised http URL.
 */
export const linkify = (text: string): TextPart[] => {
  const parts: TextPart[] = []
  let cursor = 0
  for (const match of linkifier.match(text) ?? []) {
    if (match.index > cursor) {
      parts.push({ text: text.slice(cursor, match.index) })
    }
    parts.push({ text: match.raw, href: match.url })
    cursor = match.lastIndex
  }
  if (cursor < text.length) {
    parts.push({ text: text.slice(cursor) })
  }
  return parts
}
