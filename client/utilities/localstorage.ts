export const localStorageWrapper = {
  getItem(key: string): string | null {
    try {
      return localStorage.getItem(key)
    } catch (e: unknown) {
      console.error(e)
    }
    return null
  },
  setItem(key: string, value: string): void {
    try {
      localStorage.setItem(key, value)
    } catch (e: unknown) {
      console.error(e)
    }
  },
  removeItem(key: string): void {
    try {
      localStorage.removeItem(key)
    } catch (e: unknown) {
      console.error(e)
    }
  }
}
