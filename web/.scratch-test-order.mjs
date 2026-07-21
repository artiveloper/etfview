import { createClient } from '@supabase/supabase-js'
import fs from 'fs'

const env = fs.readFileSync('.env.local', 'utf8')
const url = env.match(/NEXT_PUBLIC_SUPABASE_URL=(.*)/)[1].trim()
const key = env.match(/NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY=(.*)/)[1].trim()

const supabase = createClient(url, key)

const query = supabase
  .from('etf')
  .select('short_code, etf_quote(net_asset_total)', { count: 'exact' })
  .is('delisted_at', null)
  .order('net_asset_total', { referencedTable: 'etf_quote', ascending: false, nullsFirst: false })
  .order('short_code', { ascending: true })
  .range(0, 9)

const { data, error } = await query
if (error) console.error(error)
console.log(JSON.stringify(data, null, 2))
