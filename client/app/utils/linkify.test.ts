import { test, expect } from 'vitest'
import { linkify } from './linkify'

test('linkify leaves text without URLs alone', () => {
  expect(linkify('no links here')).toEqual([{ text: 'no links here' }])
  expect(linkify('')).toEqual([])
})

test('linkify splits out http and https URLs', () => {
  expect(linkify('see https://example.com/a and http://b.example/c?x=1 now')).toEqual([
    { text: 'see ' },
    { text: 'https://example.com/a', href: 'https://example.com/a' },
    { text: ' and ' },
    { text: 'http://b.example/c?x=1', href: 'http://b.example/c?x=1' },
    { text: ' now' }
  ])
})

test('linkify keeps trailing punctuation as text', () => {
  expect(linkify('ask at https://example.com/x.')).toEqual([
    { text: 'ask at ' },
    { text: 'https://example.com/x', href: 'https://example.com/x' },
    { text: '.' }
  ])
  expect(linkify('(see https://example.com/x)')).toEqual([
    { text: '(see ' },
    { text: 'https://example.com/x', href: 'https://example.com/x' },
    { text: ')' }
  ])
  expect(linkify('https://en.wikipedia.org/wiki/RFC_(disambiguation)')).toEqual([
    {
      text: 'https://en.wikipedia.org/wiki/RFC_(disambiguation)',
      href: 'https://en.wikipedia.org/wiki/RFC_(disambiguation)'
    }
  ])
})

test('linkify preserves newlines between URLs', () => {
  expect(linkify('a https://x.example\nb')).toEqual([
    { text: 'a ' },
    { text: 'https://x.example', href: 'https://x.example' },
    { text: '\nb' }
  ])
})

test('linkify links bare domains but not version numbers or e-mail addresses', () => {
  expect(linkify('see rfc-editor.org/errata, not v1.2 or me@example.com')).toEqual([
    { text: 'see ' },
    { text: 'rfc-editor.org/errata', href: 'http://rfc-editor.org/errata' },
    { text: ', not v1.2 or me@example.com' }
  ])
})
