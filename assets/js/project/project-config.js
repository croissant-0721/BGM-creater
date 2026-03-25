/**
 * Tailwind CSS Configuration for Project Pages
 * 项目页面 Tailwind CSS 配置文件
 */

// Tailwind 配置
window.tailwindConfig = {
    // DaisyUI v5 配置
    daisyui: {
        themes: ["light", "dark"],
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
                // 淡入动画
                'fade-in': 'fadeIn 0.5s ease-out',
                'fade-in-up': 'fadeInUp 0.5s ease-out',
                'fade-in-down': 'fadeInDown 0.5s ease-out',

                // 滑动动画
                'slide-up': 'slideUp 0.3s ease-out',
                'slide-in-right': 'slideInRight 0.5s ease-out',
                'slide-in-left': 'slideInLeft 0.5s ease-out',

                // 缩放动画
                'scale-in': 'scaleIn 0.2s ease-out',
                'scale-out': 'scaleOut 0.3s ease-in',

                // 弹跳动画
                'bounce-slow': 'bounce 3s infinite',
                'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',

                // 旋转动画
                'spin-slow': 'spin 3s linear infinite',
            },
            keyframes: {
                fadeIn: {
                    '0%': { opacity: '0' },
                    '100%': { opacity: '1' },
                },
                fadeInUp: {
                    '0%': { opacity: '0', transform: 'translateY(20px)' },
                    '100%': { opacity: '1', transform: 'translateY(0)' },
                },
                fadeInDown: {
                    '0%': { opacity: '0', transform: 'translateY(-20px)' },
                    '100%': { opacity: '1', transform: 'translateY(0)' },
                },
                slideUp: {
                    '0%': { transform: 'translateY(10px)', opacity: '0' },
                    '100%': { transform: 'translateY(0)', opacity: '1' },
                },
                slideInRight: {
                    '0%': { transform: 'translateX(100%)', opacity: '0' },
                    '100%': { transform: 'translateX(0)', opacity: '1' },
                },
                slideInLeft: {
                    '0%': { transform: 'translateX(-100%)', opacity: '0' },
                    '100%': { transform: 'translateX(0)', opacity: '1' },
                },
                scaleIn: {
                    '0%': { transform: 'scale(0.95)', opacity: '0' },
                    '100%': { transform: 'scale(1)', opacity: '1' },
                },
                scaleOut: {
                    '0%': { transform: 'scale(1)', opacity: '1' },
                    '100%': { transform: 'scale(0.95)', opacity: '0' },
                },
            },
        },
    },
    // DaisyUI 插件已通过 CDN 加载,无需在 plugins 中声明
    plugins: [],
};

// 如果 Tailwind 已加载,应用配置
if (window.tailwind) {
    window.tailwind.config = window.tailwindConfig;
}
