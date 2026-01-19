/**
 * Tailwind CSS Configuration for Billing Pages
 * 账单页面 Tailwind CSS 配置文件
 * 可以在 HTML 中通过 <script> 标签引入
 */

// Tailwind 配置
window.tailwindConfig = {
    // DaisyUI v5 配置
    daisyui: {
        themes: ["light", "dark", "corporate", "business"],
        darkTheme: "dark",
        base: true,
        styled: true,
        utils: true,
    },
    darkMode: 'class',
    theme: {
        extend: {
            fontFamily: {
                sans: ['Inter', 'ui-sans-serif', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'Helvetica Neue', 'Arial', 'sans-serif'],
            },
            colors: {
                brand: {
                    50: '#E8EEFF',
                    100: '#C4D4FF',
                    200: '#9DB6FF',
                    300: '#7599FF',
                    400: '#4D7CFF',
                    500: '#2560FF',
                    600: '#002FA7',
                    700: '#002687',
                    800: '#001D67',
                    900: '#001447',
                    950: '#000a1f',
                }
            },
            animation: {
                'fade-in': 'fadeIn 0.3s ease-out',
                'slide-up': 'slideUp 0.3s ease-out',
                'scale-in': 'scaleIn 0.2s ease-out',
            },
            keyframes: {
                fadeIn: {
                    '0%': { opacity: '0' },
                    '100%': { opacity: '1' },
                },
                slideUp: {
                    '0%': { transform: 'translateY(10px)', opacity: '0' },
                    '100%': { transform: 'translateY(0)', opacity: '1' },
                },
                scaleIn: {
                    '0%': { transform: 'scale(0.95)', opacity: '0' },
                    '100%': { transform: 'scale(1)', opacity: '1' },
                },
            },
        },
    },
    // DaisyUI 插件已通过 CDN 加载,无需在 plugins 中声明
    plugins: [],
};

// 如果 Tailwind 已加载，应用配置
if (window.tailwind) {
    window.tailwind.config = window.tailwindConfig;
}
