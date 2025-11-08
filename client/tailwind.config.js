import formsPlugin from '@tailwindcss/forms'

/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./app/layouts/*.{html,ts,vue}",
    "./app/pages/*.{html,ts,vue}",
    "./app/components/*.{html,ts,vue}",
    "./app/utils/*.{html,ts,vue}",
  ],
  darkMode: 'class',
  plugins: [
    formsPlugin
  ],
  theme: {
    extend: {}
  }
}
