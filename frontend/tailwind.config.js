/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: '#090d16',
        panel: '#0f172a',
        cyberBlue: '#00f0ff',
        cyberPurple: '#8a2be2',
        cyberRed: '#ff0055',
        cyberGreen: '#00ff88',
      },
    },
  },
  plugins: [],
}
