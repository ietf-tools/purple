// Copyright The IETF Trust 2026, All Rights Reserved
const runtimeConfig = useRuntimeConfig()

export const useDatatrackerLinks = () => ({
  document: (name: string) =>
    `${runtimeConfig.public.datatrackerBase}/doc/${encodeURIComponent(name)}/`,
  personByEmail: (email: string) =>
    `${runtimeConfig.public.datatrackerBase}/person/${encodeURIComponent(email)}`,
  profile: `${runtimeConfig.public.datatrackerBase}/accounts/profile/`
})
