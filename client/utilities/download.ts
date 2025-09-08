/**
 * Triggers a download in the browser.
 *
 * Browsers are wary of download triggers like this (see https://developer.mozilla.org/en-US/docs/Web/Security/User_activation )
 * so this function should be called during a 'click' event in the browser, not in a setTimeout(), or it might not work.
 */
export const downloadTextFile = (filename: string, mimeType: 'text/svg', data: string): void => {
  const blob = new Blob([data], { type: mimeType })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')

  const clickHandler = () => setTimeout(() => {
    // Clean up
    URL.revokeObjectURL(url)
    link.removeEventListener('click', clickHandler)
  }, 150)

  // Clean up after download
  link.addEventListener('click', clickHandler, false)

  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}
