type ProgressCallback = (progressPercent: number) => void

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

export const sleep = (durationMs: number) =>
  new Promise((resolve) => setTimeout(resolve, durationMs))
