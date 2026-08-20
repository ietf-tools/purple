import type { RpcRole } from '~/purple_client'

/**
 * Resolve RpcRole slugs to their display names. Assignment roles are exposed as
 * slugs throughout the API; this maps them to human-readable names, falling back
 * to the slug for anything not in the roles list (e.g. the synthetic 'blocked').
 * useAsyncData's shared key dedupes the fetch across all callers.
 */
export const useRoleName = () => {
  const api = useApi()
  const { data: roles } = useAsyncData('rpc-roles', () => api.rpcRolesList(), {
    server: false,
    lazy: true,
    default: () => [] as RpcRole[]
  })
  const roleName = (slug: string) => roles.value.find((r) => r.slug === slug)?.name ?? slug
  return { roles, roleName }
}
