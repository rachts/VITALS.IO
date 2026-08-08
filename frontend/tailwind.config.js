/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        base: '#080C14',
        surface: '#0D1220',
        elevated: '#121929',
        'accent-primary': '#00E5FF',
        'accent-secondary': '#7B61FF',
        'accent-warn': '#FF6B35',
        'accent-success': '#00C896',
        'text-primary': '#F0F4FF',
        'text-muted': '#5A6A8A',
        border: '#1E2D45'
      },
      fontFamily: {
        display: ['"Space Grotesk"', 'sans-serif'],
        body: ['Inter', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace']
      }
    },
  },
  plugins: [],
}
