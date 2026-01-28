/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                background: "#020617",
                foreground: "#f8fafc",
                primary: "#38bdf8",
                secondary: "#1e293b",
                accent: "#818cf8",
                neon: {
                    cyan: "#22d3ee",
                    indigo: "#6366f1",
                }
            },
            backgroundImage: {
                'grid-slate': "url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32' width='32' height='32' fill='none' stroke='rgb(51 65 85 / 0.15)'%3E%3Cpath d='M0 .5H31.5V32'/%3E%3C/svg%3E\")",
            }
        },
    },
    plugins: [],
}
