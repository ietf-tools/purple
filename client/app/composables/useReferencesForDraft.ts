export function useReferencesForDraft(draftName: string) {
  const api = useApi()
  return useAsyncData(
    `references-${draftName}`,
    () => api.documentsReferencesList({ draftName }),
    {
      default: () => [],
      server: false
    }
  )
}
