import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        paper: "#EEF0F2",
        ink: "#1B1F3B",
        "ink-soft": "#4A4E6B",
        rule: "#D2D5DC",
        amber: "#C97A2B",
        moss: "#4B6A50",
        rust: "#A6402F",
      },
      fontFamily: {
        serif: ["'Source Serif 4'", "Georgia", "serif"],
        mono: ["'JetBrains Mono'", "ui-monospace", "monospace"],
      },
    },
  },
  plugins: [],
};
export default config;
