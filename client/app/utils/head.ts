export const useDefaultHead = () => {
  useHead({
    link: [
      { rel: 'preconnect', href: 'https://rsms.me' },
      { rel: 'stylesheet', href: 'https://rsms.me/inter/inter.css' }
    ],
    bodyAttrs: {
      class: 'h-full'
    },
    htmlAttrs: {
      class: 'h-full'
    },
    titleTemplate: (titleChunk) => {
      const prefix = import.meta.dev ? '[DEV] ' : ''
      return titleChunk
        ? `${prefix}${titleChunk} - RFC Production Center`
        : `${prefix}RFC Production Center`
    }
  })
}
