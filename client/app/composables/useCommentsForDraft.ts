const api = useApi()

export function useCommentsForDraft(draftName: string | undefined) {
  return useAsyncData(
    `comments-${draftName || 'empty'}`,
    async () => {
      if (draftName) {
        return api.documentsCommentsList({ draftName: draftName })
      }
      return undefined
    }
  )
}
