module.exports = {
  darkMode: 'class',
  content: [
    './app/templates/**/*.html',
    './app/static/js/**/*.js'
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#eef6fb',
          100: '#d9eaf5',
          200: '#b3d4ea',
          300: '#84b8db',
          400: '#5497c4',
          blue: '#3670A0',
          600: '#2c5a84',
          700: '#264a6c',
          800: '#23405c',
          900: '#1e293b',
          yellow: '#ffdd54',
          dark: '#0b1220',
          panel: '#131c2e',
          ink: '#0f172a'
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', '"Segoe UI"', 'Roboto', '"Helvetica Neue"', 'Arial', '"Noto Sans"', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'ui-monospace', 'SFMono-Regular', 'Menlo', 'Consolas', 'monospace']
      },
      boxShadow: {
        card: '0 1px 2px rgba(15, 23, 42, 0.06), 0 8px 24px -12px rgba(15, 23, 42, 0.18)',
        'card-hover': '0 2px 4px rgba(15, 23, 42, 0.06), 0 20px 44px -16px rgba(54, 112, 160, 0.35)',
        glow: '0 0 0 1px rgba(54, 112, 160, 0.12), 0 12px 32px -12px rgba(54, 112, 160, 0.45)'
      },
      borderRadius: {
        '2xl': '1rem',
        '3xl': '1.5rem'
      },
      keyframes: {
        'fade-up': {
          '0%': { opacity: '0', transform: 'translateY(10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' }
        },
        'float-slow': {
          '0%, 100%': { transform: 'translate3d(0, 0, 0)' },
          '50%': { transform: 'translate3d(0, -10px, 0)' }
        }
      },
      animation: {
        'fade-up': 'fade-up 0.5s cubic-bezier(0.22, 1, 0.36, 1) both',
        'float-slow': 'float-slow 7s ease-in-out infinite'
      }
    }
  }
};
