export function useHistoryForDraft(draftName: string) {
  const api = useApi()
  return useAsyncData(
    `history-${draftName}`,
    () => api.documentsHistoryList({ draftName: draftName }),
    { server: false, default: () => [], lazy: false }
  )
}
