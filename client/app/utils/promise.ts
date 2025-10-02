type ProgressCallback = (
  /**
   * Be sure to round the value if displaying the number to users. This may have a lot of decimal places.
   */
  progressPercent: number
) => void

/**
 * An equivalent to the inbuilt Promise.all() except with a progress % callback
 */
export const promiseAllProgress = (
  promises: Promise<any>[],
  progressCallback: ProgressCallback
) => {
  let progress = 0
  progressCallback(progress)
  promises.forEach((promise) =>
    promise.then(() => {
      progress++
      const progressPercent = (progress * 100) / promises.length
      progressCallback(progressPercent)
    })
  )
  return Promise.all(promises)
}

/**
 * setTimeout as a promise
 */
export const sleep = (durationMs: number) =>
  new Promise((resolve) => setTimeout(resolve, durationMs))
