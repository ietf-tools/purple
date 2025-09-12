const api = useApi()

export function useCommentsForDraft(draftName: string) {
  return useAsyncData(
    `comments-${draftName}`,
    () => api.documentsCommentsList({ draftName: draftName })
  )
}
