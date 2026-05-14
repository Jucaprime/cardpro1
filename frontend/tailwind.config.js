/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        neon: {
          green: '#39FF14',
          glow: 'rgba(57, 255, 20, 0.5)'
        }
      }
    },
  },
  plugins: [],
}
