/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './lib/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  darkMode: ['class', '[data-theme="dark"]'],
  theme: {
    extend: {
      colors: {
        page: 'var(--bg-page)',
        surface: {
          DEFAULT: 'var(--bg-surface)',
          elevated: 'var(--bg-surface-elevated)',
          glass: 'var(--bg-surface-glass)',
        },
        border: {
          subtle: 'var(--border-subtle)',
          DEFAULT: 'var(--border-default)',
          strong: 'var(--border-strong)',
        },
        txt: {
          primary: 'var(--text-primary)',
          secondary: 'var(--text-secondary)',
          tertiary: 'var(--text-tertiary)',
          inverse: 'var(--text-inverse)',
        },
        cta: {
          bg: 'var(--btn-primary-bg)',
          text: 'var(--btn-primary-text)',
          hover: 'var(--btn-primary-hover)',
        },
        status: {
          ok: 'var(--status-ok)',
          'ok-bg': 'var(--status-ok-bg)',
          warn: 'var(--status-warn)',
          'warn-bg': 'var(--status-warn-bg)',
          bad: 'var(--status-bad)',
          'bad-bg': 'var(--status-bad-bg)',
          info: 'var(--status-info)',
          'info-bg': 'var(--status-info-bg)',
        },
      },
      fontFamily: {
        serif: ['var(--font-serif)', 'serif'],
        sans: ['var(--font-sans)', 'sans-serif'],
        mono: ['var(--font-mono)', 'monospace'],
      },
      borderRadius: {
        sm: 'var(--r-sm)',
        md: 'var(--r-md)',
        lg: 'var(--r-lg)',
        pill: 'var(--r-pill)',
      },
      boxShadow: {
        glass: 'var(--glass-shadow)',
      },
    },
  },
  plugins: [],
};
