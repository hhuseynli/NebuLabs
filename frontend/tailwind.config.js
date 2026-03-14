/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        ember: {
          50: "#fff8ef",
          100: "#ffe5c3",
          500: "#ff8a00",
          700: "#c24f00",
          900: "#411f00"
        },
        slateink: "#0f172a",
        spruce: "#2f6f5e"
      },
      boxShadow: {
        flare: "0 15px 45px -20px rgba(255, 138, 0, 0.55)"
      }
    },
  },
  plugins: [],
};
