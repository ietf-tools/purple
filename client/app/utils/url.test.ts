import { test, expect } from 'vitest'
import { isInternalLink } from './url'

test('isInternalLink', ()=> {
  expect(isInternalLink('/something')).toBeTruthy()
  expect(isInternalLink('https://example.com')).toBeFalsy()
})
