tailwind.config = {
    darkMode: 'class',
    theme: {
        extend: {
            fontFamily: {
                sans: ['Inter', 'sans-serif'],
            },
            colors: {
                kline: {
                    DEFAULT: '#002FA7',
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
                },
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
                }
            }
        }
    },
    daisyui: {
        themes: ["dark", "light"],
    },
}
