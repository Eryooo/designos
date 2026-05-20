#!/usr/bin/env node
import { execFileSync } from 'child_process'
import { fileURLToPath } from 'url'
import { join, dirname } from 'path'
import { existsSync } from 'fs'

const __dirname = dirname(fileURLToPath(import.meta.url))
const pkgRoot = join(__dirname, '..')
const installScript = join(pkgRoot, 'install.sh')

if (!existsSync(installScript)) {
  console.error('✗ install.sh not found in package')
  process.exit(1)
}

try {
  execFileSync('bash', [installScript], {
    stdio: 'inherit',
    env: { ...process.env, LOCAL_SOURCE: pkgRoot }
  })
} catch (e) {
  process.exit(e.status || 1)
}
