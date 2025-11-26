export default {
  content: [
    "./templates/**/*.{html,js,htmx}",
    "./apps/**/*.{html,js}",
    "./static/**/*.{html,js}",
    "./templates/**/*.html",
    "./static/core/js/**/*.js",
    "./static/vod/**/*",
  ],
  plugins: [require("daisyui")],
  daisyui: {
    themes: ["light", "dark", "corporate"],
  },
};
