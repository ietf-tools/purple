export function useLabels() {
  return useAsyncData(
    `labels`,
    () => labelsListSingleton(),
    {
      default: () => [],
      server: false
    }
  )
}
