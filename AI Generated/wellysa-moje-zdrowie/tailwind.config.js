/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        wellysa: {
          green: '#0BB07F',
        },
        charcoal: '#1E293B',
        section: '#F8FAFC',
      },
      fontFamily: {
        sans: ['Sora', 'system-ui', 'sans-serif'],
      },
      borderRadius: {
        card: '20px',
      },
    },
  },
  plugins: [],
}
