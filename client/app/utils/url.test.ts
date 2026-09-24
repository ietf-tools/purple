import { test, expect } from 'vitest'
import { isInternalLink, mailArchiveSearchUrl } from './url'

test('isInternalLink', () => {
  expect(isInternalLink('/something')).toBeTruthy()
  expect(isInternalLink('https://example.com')).toBeFalsy()
})

test('mailArchiveSearchUrl', () => {
  expect(mailArchiveSearchUrl('draft-ietf-tls-mldsa')).toBe(
    'https://mailarchive.ietf.org/arch/search/?email_list=rfc-editor&q=subject%3A%28draft-ietf-tls-mldsa%29'
  )
})
