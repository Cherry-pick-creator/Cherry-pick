import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        bg: {
          primary: "#0A0A0A",
          secondary: "#141414",
          tertiary: "#1E1E1E",
        },
        border: "#2A2A2A",
        "text-primary": "#F5F0EB",
        "text-secondary": "#9CA3AF",
        "accent-cyan": "#00E5FF",
        "accent-violet": "#8B5CF6",
        success: "#22C55E",
        warning: "#F59E0B",
        error: "#EF4444",
        cherry: "#DC143C",
      },
      fontFamily: {
        sans: ["Inter", "sans-serif"],
        mono: ["JetBrains Mono", "monospace"],
      },
    },
  },
  plugins: [],
};

export default config;
