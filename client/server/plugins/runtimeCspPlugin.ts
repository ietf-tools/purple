// Copyright The IETF Trust 2025, All Rights Reserved
import defu from 'defu'

export default defineNitroPlugin((nitroApp) => {
  // Plugin to augment the build-time nuxt-security configuration with runtime values
  // See https://nuxt-security.vercel.app/advanced/hooks, particularly the examples
  nitroApp.hooks.hook(
    'nuxt-security:routeRules',
    async (appSecurityOptions) => {
      const runtimeConfig = useRuntimeConfig()
      const scriptSrcHashes = runtimeConfig.public?.cspScriptSrcHashes
        ?.split(',')
        .map(h => `'${h.trim()}'`)
        .filter(s => s !== "''") // exclude empty entries
      if (scriptSrcHashes?.length > 0) {
        // defu() will add the hashes to the existing script-src array in the security options
        appSecurityOptions['/**'] = defu(
          {
            headers: {
              contentSecurityPolicy: {
                'script-src': scriptSrcHashes
              }
            }
          },
          appSecurityOptions['/**']
        )
      }
    }
  )
})
