// git commit 시 PRD 갱신이 필요한 경로가 스테이징됐는데 PRD.md가 빠졌으면 리마인드하는 PreToolUse hook
import { readFileSync } from 'node:fs'
import { execSync } from 'node:child_process'

// hook은 stdout에 JSON을 내면 그 additionalContext가 Claude에 주입된다. 아무것도 안 내면 조용히 통과.
function pass(payload) {
    if (payload) process.stdout.write(JSON.stringify(payload))
    process.exit(0)
}

let input
try {
    input = JSON.parse(readFileSync(0, 'utf8') || '{}')
} catch {
    pass(null)
}

const command = input?.tool_input?.command ?? ''
// git commit 이 아닌 Bash 호출은 즉시 통과 (매 Bash 호출마다 발동하므로 빨리 빠져나간다)
if (!/\bgit\s+commit\b/.test(command)) pass(null)

const cwd = input?.cwd || process.cwd()

let staged = []
try {
    staged = execSync('git diff --cached --name-only', { cwd, encoding: 'utf8' })
        .split('\n')
        .map((line) => line.trim())
        .filter(Boolean)
} catch {
    pass(null)
}

if (staged.length === 0 || staged.includes('PRD.md')) pass(null)

// PRD가 낡을 수 있는 경로 → PRD 섹션 매핑
const triggers = [
    { re: /^collector\/supabase\/migrations\//, section: '3절 데이터 모델' },
    { re: /^collector\/src\/etf_collector\/(scheduler|jobs)\//, section: '4절 데이터 수집' },
    { re: /^collector\/src\/etf_collector\/config\.py$/, section: '4절 데이터 수집(스케줄)' },
    { re: /^web\/(domain|components)\/etf\//, section: '5절 사용자 기능' },
    { re: /^web\/app\//, section: '5절 사용자 기능' },
]

const hits = []
for (const file of staged) {
    const t = triggers.find((trigger) => trigger.re.test(file))
    if (t) hits.push({ file, section: t.section })
}

if (hits.length === 0) pass(null)

const files = [...new Set(hits.map((h) => h.file))].slice(0, 8).join('\n  ')
const sections = [...new Set(hits.map((h) => h.section))].join(', ')

pass({
    hookSpecificOutput: {
        hookEventName: 'PreToolUse',
        additionalContext:
            'PRD 갱신 리마인더: 이번 커밋에 제품 명세에 영향 줄 수 있는 파일이 스테이징됐지만 PRD.md는 빠졌습니다.\n' +
            `  ${files}\n` +
            `이 변경이 기능·데이터 모델·스케줄을 바꾼다면 PRD.md(${sections})와 9절 변경 이력 표를 갱신해 같이 커밋하세요. ` +
            '단순 리팩터·버그수정 등 제품 명세에 영향이 없으면 그대로 진행해도 됩니다.',
    },
})
