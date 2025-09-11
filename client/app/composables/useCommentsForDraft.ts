const api = useApi()

export function useCommentsForDraft(draftName: string | undefined) {
  return useAsyncData(
    `comments-${draftName || 'empty'}`,
    async () => {
      if (draftName) {
        return await api.documentsCommentsList({ draftName: draftName })
      }
      return undefined
    }
  )
}
