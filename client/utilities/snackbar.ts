type SnackbarService = ReturnType<typeof useSnackbar>

type Props = {
  snackbar: SnackbarService
  error: unknown
  defaultTitle?: string
}

export const snackbarForErrors = async ({ snackbar, error, defaultTitle }: Props) => {
  let title = defaultTitle ?? 'Error.'
  let text = `${error}`

  // handle Fetch exceptions
  if (
    error &&
    typeof error === 'object' &&
    'response' in error &&
    error.response instanceof Response
  ) {
    const { response } = error
    const contentType = response.headers.get('Content-Type')
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
        } else {
          text = JSON.stringify(data, null, 2)
        }
        break
      default:
        text = await response.text()
        break
    }
  } else if (error && typeof error === 'object') {

    if ('message' in error && 'statusCode' in error) {
      // useAsyncData errors are shaped like this
      text = `HTTP ${error.statusCode}: ${error.message}`
    } else {
      text = JSON.stringify(error)
    }
  }

  snackbar.add({
    type: 'error',
    title,
    text
  })
}
