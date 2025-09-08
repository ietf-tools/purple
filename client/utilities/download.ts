export const downloadTextFile = (filename: string, mimeType: 'text/svg', data: string): void => {
  const blob = new Blob([data], { type: mimeType })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')

  // Clean up after download
  link.addEventListener('click', () =>
    setTimeout(() => URL.revokeObjectURL(url), 150)
  )

  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}
