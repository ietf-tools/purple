// Copyright The IETF Trust 2026, All Rights Reserved
const runtimeConfig = useRuntimeConfig()

export const useDatatrackerLinks = () => ({
  personByEmail: (email: string) => `${ runtimeConfig.public.datatrackerBase }/person/${ encodeURIComponent(email) }`
})
