/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          500: '#0ea5e9',
          600: '#0284c7',
          700: '#0369a1',
        },
        gray: {
          50: '#f8fafc',
          100: '#f1f5f9',
          200: '#e2e8f0',
          300: '#cbd5e1',
          400: '#94a3b8',
          500: '#64748b',
          600: '#475569',
          700: '#334155',
          800: '#1e293b',
          900: '#0f172a',
        }
      },
      fontFamily: {
        sans: ['Plus Jakarta Sans', 'system-ui', 'sans-serif'],
      },
      borderRadius: {
        'lg': '12px',
        'md': '8px',
      },
      boxShadow: {
        'card': '0 1px 3px rgba(0, 0, 0, 0.06)',
        'card-md': '0 4px 12px rgba(0, 0, 0, 0.08)',
      },
    },
  },
}
