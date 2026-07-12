#!/usr/bin/env node

import { cpSync, existsSync, mkdirSync, readdirSync, readFileSync, rmSync, writeFileSync } from 'node:fs'
import { execFileSync } from 'node:child_process'
import { dirname, join, relative, resolve } from 'node:path'

const root = resolve(import.meta.dirname, '..')
const portalDir = join(root, 'portal')
const generatedDir = join(portalDir, 'generated')
const marp = join(root, 'presentaciones', 'node_modules', '.bin', 'marp')
const slidev = join(root, 'presentaciones', 'node_modules', '.bin', 'slidev')

if (!existsSync(marp) || !existsSync(slidev)) {
  throw new Error('Faltan dependencias de presentaciones. Ejecuta: npm install --prefix presentaciones')
}

rmSync(generatedDir, { recursive: true, force: true })
mkdirSync(generatedDir, { recursive: true })

function slugify(value) {
  return value
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
}

function frontmatter(file) {
  const text = readFileSync(file, 'utf8')
  const block = text.match(/^---\s*\n([\s\S]*?)\n---/m)?.[1] ?? ''
  const get = (key) => block.match(new RegExp(`^${key}:\\s*(.+)$`, 'm'))?.[1]?.trim().replace(/^['"]|['"]$/g, '')
  const heading = text.match(/^#\s+(.+)$/m)?.[1]?.trim()
  return {
    title: get('title') || heading || file.split('/').pop().replace(/\.md$/, ''),
    description: get('description') || '',
  }
}

function run(command, args, options) {
  execFileSync(command, args, { stdio: 'inherit', ...options })
}

const catalog = []
for (const collection of ['presentaciones', 'talleres']) {
  const collectionDir = join(root, collection)
  for (const item of readdirSync(collectionDir, { withFileTypes: true })) {
    if (!item.isDirectory() || item.name === 'node_modules') continue
    const projectDir = join(collectionDir, item.name)
    const projectSlug = slugify(`${collection}-${item.name}`)

    const slidevDir = join(projectDir, 'slidev')
    const slidevEntry = join(slidevDir, 'slides.md')
    if (existsSync(slidevEntry)) {
      const outputDir = join(generatedDir, 'slidev', projectSlug)
      const portalBase = `/generated/slidev/${projectSlug}/`
      mkdirSync(dirname(outputDir), { recursive: true })
      run(slidev, [
        'build',
        'slides.md',
        '--out',
        outputDir,
        '--base',
        portalBase,
        '--router-mode',
        'hash',
      ], { cwd: slidevDir })
      const meta = frontmatter(slidevEntry)
      catalog.push({
        id: `${projectSlug}-slidev`,
        title: meta.title,
        description: meta.description,
        type: 'slidev',
        collection,
        source: relative(root, slidevEntry),
        url: `generated/slidev/${projectSlug}/index.html`,
      })
    }

    for (const file of readdirSync(projectDir).filter((name) => name.endsWith('.md')).sort()) {
      const markdown = join(projectDir, file)
      const theme = join(projectDir, 'assets', 'css', 'theme.css')
      if (!existsSync(theme)) continue
      const fileSlug = slugify(`${collection}-${item.name}-${file.replace(/\.md$/, '')}`)
      const outputDir = join(generatedDir, 'marp', fileSlug)
      mkdirSync(outputDir, { recursive: true })
      run(marp, [markdown, '--theme', theme, '--allow-local-files', '--html', '-o', join(outputDir, 'index.html')], { cwd: root })
      const assets = join(projectDir, 'assets')
      if (existsSync(assets)) cpSync(assets, join(outputDir, 'assets'), { recursive: true, dereference: true })
      const meta = frontmatter(markdown)
      catalog.push({
        id: `${fileSlug}-marp`,
        title: meta.title,
        description: meta.description,
        type: 'marp',
        collection,
        source: relative(root, markdown),
        url: `generated/marp/${fileSlug}/index.html`,
      })
    }
  }
}

catalog.sort((a, b) => a.title.localeCompare(b.title, 'es'))
writeFileSync(join(portalDir, 'catalog.json'), `${JSON.stringify({ generatedAt: new Date().toISOString(), presentations: catalog }, null, 2)}\n`)
console.log(`Portal generado: ${catalog.length} presentaciones`)
