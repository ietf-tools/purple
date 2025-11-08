export function useCommentsForDraft(draftName: string) {
  const api = useApi()
  return useAsyncData(
    `comments-${draftName}`,
    () => api.documentsCommentsList({ draftName: draftName }),
    { server: false, lazy: true }
  )
}
