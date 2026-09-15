export type TextPart = { text: string; href?: string }

// Trailing punctuation is almost always prose, not part of the URL:
// "see https://example.com/x." A closing paren is only kept when the URL
// opened one (Wikipedia-style links).
const URL_PATTERN = /https?:\/\/[^\s<>"']+/g
const TRAILING_PUNCTUATION = /[.,;:!?]+$/

const trimUrl = (url: string): string => {
  let trimmed = url.replace(TRAILING_PUNCTUATION, '')
  while (trimmed.endsWith(')') && !trimmed.includes('(')) {
    trimmed = trimmed.slice(0, -1).replace(TRAILING_PUNCTUATION, '')
  }
  return trimmed
}

/**
 * Split plain text into runs of text and http(s) URLs so the URLs can be
 * rendered as links without interpreting the text as HTML.
 */
export const linkify = (text: string): TextPart[] => {
  const parts: TextPart[] = []
  let cursor = 0
  for (const match of text.matchAll(URL_PATTERN)) {
    const href = trimUrl(match[0])
    const start = match.index
    if (start > cursor) {
      parts.push({ text: text.slice(cursor, start) })
    }
    parts.push({ text: href, href })
    cursor = start + href.length
  }
  if (cursor < text.length) {
    parts.push({ text: text.slice(cursor) })
  }
  return parts
}
