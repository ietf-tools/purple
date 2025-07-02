import formsPlugin from '@tailwindcss/forms'

/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./layouts/*.{html,ts,vue}",
    "./pages/*.{html,ts,vue}",
    "./utilities/*.{html,ts,vue}",
    "./components/*.{html,ts,vue}",
  ],
  darkMode: 'class',
  plugins: [
    formsPlugin
  ],
  theme: {
    extend: {}
  }
}
