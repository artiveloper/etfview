import type { Metadata } from 'next'
import { Geist_Mono, Noto_Sans_KR } from 'next/font/google'

import './globals.css'
import { SiteHeader } from '@/components/site-header'
import { ThemeProvider } from '@/components/theme-provider'
import { Providers } from './providers'
import { cn } from '@/lib/utils'

export const metadata: Metadata = {
    icons: {
        icon: [
            { url: '/favicon-16x16.png', sizes: '16x16', type: 'image/png' },
            { url: '/favicon-32x32.png', sizes: '32x32', type: 'image/png' },
            { url: '/icon-512x512.png', sizes: '512x512', type: 'image/png' },
        ],
        apple: [{ url: '/apple-touch-icon.png', sizes: '180x180', type: 'image/png' }],
    },
}

const notoSansKR = Noto_Sans_KR({
    subsets: ['latin'],
    variable: '--font-sans',
})

const fontMono = Geist_Mono({
    subsets: ['latin'],
    variable: '--font-mono',
})

export default function RootLayout({
    children,
}: Readonly<{
    children: React.ReactNode
}>) {
    return (
        <html
            lang="ko"
            suppressHydrationWarning
            className={cn('antialiased', fontMono.variable, notoSansKR.variable, 'font-sans')}
        >
            <body>
                <ThemeProvider>
                    <Providers>
                        <SiteHeader />
                        {children}
                    </Providers>
                </ThemeProvider>
            </body>
        </html>
    )
}
