import type { NuxtError } from "#app"

type SnackbarService = ReturnType<typeof useSnackbar>

type Props = {
  snackbar: SnackbarService
  error: unknown
  defaultTitle?: string
}

const MAX_TEXT_LENGTH = 100

export const snackbarForErrors = async ({ snackbar, error, defaultTitle }: Props) => {
  let title = defaultTitle ?? 'Error.'
  let text = `${error}`

  console.log({
     "typeof error === 'object'": typeof error === 'object',
      "'response' in error": 'response' in error,
      "error.response instanceof Response": error && typeof error === 'object' &&
      'response' in error &&
      error.response instanceof Response
  })

  if(error) {
    if (
      typeof error === 'object' &&
      'response' in error &&
      error.response instanceof Response
    ) {
      text = await getErrorTextFromFetchResponse(error.response, text)
    } else if (isNuxtError(error)) {
      text = await getErrorTextFromNuxtError(error, text)
    } else {
      text = JSON.stringify(error)
    }
  }


  // truncating text...
  // showing too much text to users in a toast isn't good UX,
  // so we'll truncate but tell them to read dev console for more
  const wasTruncated = text.length > MAX_TEXT_LENGTH
  if(wasTruncated) {
    console.log("Error", error, "had text:", text)
  }
  text = text.substring(0, MAX_TEXT_LENGTH)
  if (wasTruncated) {
    text += '[...] See dev console for more.'
  }

  snackbar.add({
    type: 'error',
    title,
    text
  })
}

const getErrorTextFromFetchResponse = async (response: Response, text: string): Promise<string> => {
  const contentType = response.headers.get('Content-Type')
  console.log({text})
  switch (contentType) {
    case 'application/json':
      // format the JSON a bit
      const data = await response.json()
      const keys = Object.keys(data)
      if (keys.length === 1) {
        // DRF response, so extract comment
        const containerKey = keys[0]
        const value = data[containerKey]
        text = Array.isArray(value) ? value.join(', ') : `${value}`
        console.log("keys", keys)
      } else {
        text = JSON.stringify(data, null, 2)
      }
      break
    default:
      text = await response.text()
      break
  }
  return text
}

const getErrorTextFromNuxtError = async (error: NuxtError, _text: string): Promise<string> => {
  return `HTTP ${error.statusCode}: ${error.message}`
}

const isNuxtError = (error: unknown): error is NuxtError => {
  return !!(error && typeof error === 'object' && 'message' in error && 'statusCode' in error)
}
