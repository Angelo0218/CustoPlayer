/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    container: {
      center: true,
    },
    extend: {
      colors: {
        'lightyellow': '#fdf3da',
        'lightred' :'#ed6ea0',
        'bule1':'#f0f5f9',
        'bule2':'#c9d6de',
        'bule3':'#52616a',
        'bule4':'#1e2022',
      },
      spacing: {
        '128': '50vw',
        '111': '20vw',
        '123':'50rem',
        '1.5'  :'8rem'
      }
    },
  },
  plugins: [],
}