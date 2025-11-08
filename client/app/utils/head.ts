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
      return titleChunk ? `${titleChunk} - RFC Production Center` : 'RFC Production Center'
    }
  })
}
