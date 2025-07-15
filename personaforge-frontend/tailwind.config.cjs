/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      fontFamily: {
        inter: ['Inter', 'sans-serif'],
      },
      colors: {
        primary: '#7f5af0',
        accent: '#2cb67d',
        bg: '#16161a',
        surface: '#242629',
        glass: 'rgba(255,255,255,0.08)',
      },
    },
  },
  plugins: [],
}

