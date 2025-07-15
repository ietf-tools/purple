// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2024-09-06', // today's date, nothing special otherwise
  colorMode: {
    preference: 'light',
    classSuffix: '',
    fallback: 'light'
  },
  devServer: {
    port: 3000,
    url: 'http://localhost:8088'
  },
  devtools: {
    enabled: true
  },
  headlessui: {
    prefix: 'Headless'
  },
  modules: [
    '@nuxt/devtools',
    '@nuxt/eslint',
    '@nuxtjs/color-mode',
    '@nuxtjs/tailwindcss',
    '@nuxtjs/robots',
    '@pinia/nuxt',
    'nuxt-headlessui',
    'nuxt-icon',
    'nuxt-snackbar',
    'nuxt-svgo',
    'nuxt-security',
    'reka-ui/nuxt',
  ],
  robots: {
    credits: false,
    disallow: ['/']
  },
  runtimeConfig: {
    public: {
      cspScriptSrcHashes: '', // comma-separated list
      datatrackerBase: 'https://datatracker.ietf.org' // NUXT_PUBLIC_DATATRACKER_BASE
    }
  },
  security: {
    // adjusts the defaults, see
    // https://nuxt-security.vercel.app/getting-started/configuration#defaults
    headers: {
      contentSecurityPolicy: {
        'img-src': [
          "'self'",
          'data:',
          '*.ietf.org'
        ],
        'script-src': [
          "'strict-dynamic'",
          "'nonce-{{nonce}}'"
        ]
      }
    }
  },
  snackbar: {
    top: true,
    right: true,
    duration: 5000,
    success: '#059669', // emerald 600
    error: '#e11d48', // rose 600
    warning: '#d97706', // amber 600
    info: '#0284c7' // sky 600
  },
  tailwindcss: {
    viewer: false
  },
  typescript: {
    typeCheck: false
  },
  vite: {
    css: {
      preprocessorOptions: {
        scss: {
          api: 'modern-compiler'
        }
      }
    },
    optimizeDeps: {
      // Deps that vite does not detect statically
      include: [
        'lodash-es',
        'luxon',
        'humanize-duration',
        'vue3-snackbar'
      ]
    },
    plugins: [
      {
        name: 'vue-docs',
        transform (_code, id) {
          if (!/vue&type=docs/.test(id)) return
          return 'export default \'\''
        }
      }
    ]
  }
})
