import { test, expect } from 'vitest'
import { durationStringToHours, hoursToDurationString } from './form'

test('durationStringToHours', () => {
  expect(durationStringToHours('00:00:00')).toBe(0)
  expect(durationStringToHours('01:00:00')).toBe(1)
  expect(durationStringToHours('23:00:00')).toBe(23)
  expect(durationStringToHours('1 00:00:00')).toBe(24)
  expect(durationStringToHours('24 00:00:00')).toBe(576)
  expect(durationStringToHours('23 00:00:00')).toBe(552)
  expect(durationStringToHours('1:23 00:00:00')).toBe(1272)

  // fractions
  expect(durationStringToHours('01:15:00')).toBe(1.25)
  expect(durationStringToHours('70:15:00')).toBe(70.25)
})

test('hoursToDurationString', () => {
  expect(hoursToDurationString(0)).toBe('0 00:00:00')
  expect(hoursToDurationString(1)).toBe('0 01:00:00')
  expect(hoursToDurationString(24)).toBe('1 00:00:00')

  // fractions
  expect(hoursToDurationString(1.25)).toBe('0 01:15:00')
  expect(hoursToDurationString(70.25)).toBe('2 22:15:00')
})

test('durationStringToHours(hoursToDurationString(h))', () => {
  // ensure the converters are reversible
  expect(durationStringToHours(hoursToDurationString(1))).toBe(1)
  expect(durationStringToHours(hoursToDurationString(2))).toBe(2)
  expect(durationStringToHours(hoursToDurationString(25))).toBe(25)
  expect(durationStringToHours(hoursToDurationString(100))).toBe(100)
})
