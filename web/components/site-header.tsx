// 사이트 상단 브랜드 헤더 — 로고타입을 홈 링크로 렌더링한다.
import Image from 'next/image'
import Link from 'next/link'

export function SiteHeader() {
    return (
        <header className="border-b">
            <div className="mx-auto flex h-14 max-w-7xl items-center px-4 sm:px-6 lg:px-8">
                <Link href="/" aria-label="etfy 홈" className="flex h-full items-center">
                    <Image
                        src="/logo.png"
                        alt="etfy"
                        width={588}
                        height={245}
                        priority
                        className="h-8 w-auto dark:hidden"
                    />
                    <Image
                        src="/logo-dark.png"
                        alt="etfy"
                        width={588}
                        height={245}
                        priority
                        className="hidden h-8 w-auto dark:block"
                    />
                </Link>
            </div>
        </header>
    )
}
