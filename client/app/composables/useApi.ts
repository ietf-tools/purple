import { Configuration, PurpleApi } from '~/purple_client'

const safeMethods = ['GET', 'HEAD', 'OPTIONS', 'TRACE']

export const useApi = () => {
  const csrf = useCookie('csrftoken', { sameSite: 'strict' })

  const configuration = new Configuration({
    basePath: '',
    middleware: [{
      pre: async ({ init: { method, headers } }) => {
        if (!method) {
          throw Error(`Required 'method' but was ${method}`)
        }
        if (!headers) {
          throw Error(`Required 'headers' but was ${headers}`)
        }
        // Add CSRF token for unsafe methods
        if (!safeMethods.includes(method) &&
            !Array.isArray(headers) &&
            !(headers instanceof Headers) &&
            csrf.value
        ) {
          headers['X-CSRFToken'] = csrf.value
        }
      }
    }]
  })
  return new PurpleApi(configuration)
}
