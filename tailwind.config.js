/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',
    './apps/**/templates/**/*.html',
    './apps/**/forms.py',
    './apps/**/admin.py',
    './static/js/**/*.js',
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        brand: {
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
          950: '#020617',
        },
        crimson: {
          500: '#e11d48',
          600: '#be123c',
          700: '#9f1239',
        }
      },
      fontFamily: {
        serif: ['"Playfair Display"', 'Georgia', 'Cambria', 'Times New Roman', 'serif'],
        sans: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
      },
      typography: {
        DEFAULT: {
          css: {
            maxWidth: '100%',
            color: '#334155',
            lineHeight: '1.8',
            p: {
              marginBottom: '1.5em',
            },
            h1: {
              fontFamily: '"Playfair Display", Georgia, serif',
              fontWeight: '700',
              color: '#0f172a',
            },
            h2: {
              fontFamily: '"Playfair Display", Georgia, serif',
              fontWeight: '700',
              color: '#0f172a',
              marginTop: '1.8em',
              marginBottom: '0.8em',
            },
            h3: {
              fontFamily: '"Playfair Display", Georgia, serif',
              fontWeight: '600',
              color: '#0f172a',
            },
            blockquote: {
              fontFamily: '"Playfair Display", Georgia, serif',
              fontStyle: 'italic',
              borderLeftColor: '#be123c',
              borderLeftWidth: '4px',
              paddingLeft: '1.25rem',
              color: '#1e293b',
            },
          },
        },
        invert: {
          css: {
            color: '#cbd5e1',
            h1: { color: '#f8fafc' },
            h2: { color: '#f8fafc' },
            h3: { color: '#f8fafc' },
            blockquote: {
              borderLeftColor: '#e11d48',
              color: '#f1f5f9',
            },
          },
        },
      },
    },
  },
  plugins: [],
}
