/**
 * Typically we can't use conventional internal links because the browser
 * gives up scrolling before the SPA has loaded.
 *
 * So this reimplements native browser functionality of scrolling to an #id
 * when the page loads.
 *
 * Usage: onMounted(() => onMountedScrollToHash())
 */
export const onMountedScrollToHash = () => {
  if (!document.location.hash) {
    return
  }
  const stickyElement = document.getElementById(STICKY_DOM_ID)
  const stickyHeight = stickyElement?.offsetHeight ?? 0
  const hash = document.location.hash.replace(/^#/, '')
  const target = document.getElementById(hash)
  if (target) {
    const boundingClientRect = target.getBoundingClientRect()
    const targetTopPx = window.scrollY + boundingClientRect.top - stickyHeight
    window.scrollTo(0, targetTopPx)
  } else {
    console.log(`Couldn't find #${hash}`)
  }
}

export const STICKY_DOM_ID = 'sticky-header'
