
import { DateTime, Duration } from 'luxon'
import type { DurationLike  } from 'luxon'

export const durationStringToHours = (durationString: string | undefined): number => {
  if(durationString === undefined ) return 0
  const [seconds, minutes, hours, days, months, years] = durationString.split(/[ :]/).reverse()
  const durationLike: DurationLike = {
    years: years ? parseFloat(years) : 0,
    months: months ? parseFloat(months) : 0,
    days: days ? parseFloat(days) : 0,
    hours:  hours ? parseFloat(hours) : 0,
    minutes: minutes ? parseFloat(minutes) : 0,
    seconds: seconds ? parseFloat(seconds) : 0,
  }
  const duration = Duration.fromDurationLike(durationLike)
  return duration.as('hours')
}

const HOURS_TO_MILLISECONDS_RATIO = 60 * 60 * 1000

export const hoursToDurationString = (hours: number): string => {
  const duration = Duration.fromMillis(hours * HOURS_TO_MILLISECONDS_RATIO)
  return duration.toFormat('d hh:mm:ss')
}

export const jsDateToInputTypeDate = (date: Date): string => DateTime.fromJSDate(date).toISODate() ?? ''

export const inputTypeDateToDateTime = (isoDateString: string): DateTime => DateTime.fromISO(isoDateString, { zone: 'utc' })

