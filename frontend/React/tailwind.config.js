export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'Geist', 'SF Pro Display', 'sans-serif'],
      },
      colors: {
        background: "#09090B",
        surface: "#111827",
        "surface-light": "#1f2937",
        primary: "#9333ea", // Purple
        secondary: "#3b82f6", // Blue
        accent: "#06b6d4", // Cyan
        text: "#f8fafc",
        "text-muted": "#9ca3af",
        success: "#10b981", // Emerald
        warning: "#f59e0b", // Amber
        danger: "#e11d48", // Rose
      },
      animation: {
        'gradient': 'gradient 8s linear infinite',
      },
      keyframes: {
        gradient: {
          '0%, 100%': {
            'background-size': '200% 200%',
            'background-position': 'left center'
          },
          '50%': {
            'background-size': '200% 200%',
            'background-position': 'right center'
          },
        },
      }
    },
  },
  plugins: [],
}
