import { Geist_Mono, Noto_Sans_KR } from 'next/font/google'

import './globals.css'
import { ThemeProvider } from '@/components/theme-provider'
import { Providers } from './providers'
import { cn } from '@/lib/utils'

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
                    <Providers>{children}</Providers>
                </ThemeProvider>
            </body>
        </html>
    )
}
