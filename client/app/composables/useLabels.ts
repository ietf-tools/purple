export function useLabels() {
  const api = useApi()
  return useAsyncData(
    `labels`,
    () => api.labelsList(),
    {
      default: () => [],
      server: false
    }
  )
}
