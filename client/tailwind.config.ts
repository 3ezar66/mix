import { type Config } from 'tailwindcss';
import colors from 'tailwindcss/colors';

export default {
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        background: colors.zinc[900],
        foreground: colors.zinc[50],
        muted: {
          DEFAULT: colors.zinc[500],
          foreground: colors.zinc[400],
        },
        persian: {
          surface: colors.zinc[800],
          'surface-variant': colors.zinc[700],
          primary: colors.blue[500],
          secondary: colors.emerald[500],
          error: colors.red[500],
          warning: colors.amber[500],
          success: colors.green[500],
        },
        border: colors.zinc[700],
      },
    },
  },
  plugins: [],
} satisfies Config;
