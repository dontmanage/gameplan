// const
module.exports = {
  presets: [require('dontmanage-ui/src/utils/tailwind.config')],
  content: [
    './index.html',
    './src/**/*.{vue,js,ts,jsx,tsx}',
    './node_modules/dontmanage-ui/src/components/**/*.{vue,js,ts,jsx,tsx}',
    '../node_modules/dontmanage-ui/src/components/**/*.{vue,js,ts,jsx,tsx}',
  ],
  theme: {
    container: {
      center: true,
      padding: {
        DEFAULT: '1rem',
        sm: '2rem',
        lg: '2rem',
        xl: '4rem',
        '2xl': '4rem',
      },
    },
    extend: {
      maxWidth: {
        'main-content': '768px',
      },
      screens: {
        standalone: {
          raw: '(display-mode: standalone)',
        }
      }
    },
  },
  plugins: [],
}
