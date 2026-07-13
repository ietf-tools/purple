// Copyright The IETF Trust 2026, All Rights Reserved
const runtimeConfig = useRuntimeConfig()

export const useQueueLinks = () => ({
  finalReview: (rfcNumber: number) =>
    `${ runtimeConfig.public.queueBase }/final-review/rfc${ rfcNumber }/`
})
