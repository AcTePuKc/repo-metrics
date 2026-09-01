import fs from "node:fs"
import path from "node:path"
import React from "react"
import { renderToStaticMarkup } from "react-dom/server"
import * as simpleIcons from "simple-icons"

const root = path.resolve(path.dirname(new URL(import.meta.url).pathname), "..")
const recipesPath = path.join(root, "preview_badges.json")
const cacheDir = path.join(root, ".cache")
const cachePath = path.join(cacheDir, "icon-cache.json")

const LOCAL_ICONS = new Set(["clone", "eye", "pulse", "robot", "construction"])

const REACT_ICON_PACKS = {
  ai: () => import("react-icons/ai"),
  bi: () => import("react-icons/bi"),
  bs: () => import("react-icons/bs"),
  cg: () => import("react-icons/cg"),
  ci: () => import("react-icons/ci"),
  di: () => import("react-icons/di"),
  fa: () => import("react-icons/fa"),
  fc: () => import("react-icons/fc"),
  fi: () => import("react-icons/fi"),
  gi: () => import("react-icons/gi"),
  go: () => import("react-icons/go"),
  gr: () => import("react-icons/gr"),
  hi: () => import("react-icons/hi"),
  im: () => import("react-icons/im"),
  io: () => import("react-icons/io"),
  lia: () => import("react-icons/lia"),
  lu: () => import("react-icons/lu"),
  md: () => import("react-icons/md"),
  pi: () => import("react-icons/pi"),
  ri: () => import("react-icons/ri"),
  rx: () => import("react-icons/rx"),
  si: () => import("react-icons/si"),
  sl: () => import("react-icons/sl"),
  tb: () => import("react-icons/tb"),
  tfi: () => import("react-icons/tfi"),
  ti: () => import("react-icons/ti"),
  vsc: () => import("react-icons/vsc"),
  wi: () => import("react-icons/wi"),
}

function normalizeSimpleIcon(value) {
  return String(value).trim().toLowerCase().replace(/[^a-z0-9]/g, "")
}

function simpleIconBySlug(slug) {
  const wanted = normalizeSimpleIcon(slug)
  for (const value of Object.values(simpleIcons)) {
    if (!value || typeof value !== "object" || !value.path) continue
    if (normalizeSimpleIcon(value.slug) === wanted || normalizeSimpleIcon(value.title) === wanted) {
      return {
        viewBox: "0 0 24 24",
        paths: [value.path],
        isStroke: false,
        defaultColor: `#${value.hex}`,
      }
    }
  }
  return null
}

function reactPrefix(name) {
  let prefix = ""
  for (let i = 0; i < name.length; i += 1) {
    const char = name[i]
    if (i > 0 && char === char.toUpperCase() && char !== char.toLowerCase()) break
    prefix += char.toLowerCase()
  }
  return prefix
}

function attr(element, name) {
  const match = element.match(new RegExp(`${name}=["']([^"']+)["']`))
  return match ? match[1] : null
}

async function reactIconByName(name) {
  const loader = REACT_ICON_PACKS[reactPrefix(name)]
  if (!loader) return null
  const pack = await loader()
  const Icon = pack[name]
  if (!Icon) return null

  const svg = renderToStaticMarkup(React.createElement(Icon, { size: 24 }))
  const viewBox = attr(svg, "viewBox") || "0 0 24 24"
  const isStroke = svg.includes('fill="none"') && svg.includes('stroke="currentColor"')
  const paths = []

  for (const element of svg.match(/<path[^>]*>/g) || []) {
    if (!isStroke && /fill=["']none["']/i.test(element)) continue
    const d = attr(element, "d")
    if (d) paths.push(d)
  }

  for (const element of svg.match(/<circle[^>]*>/g) || []) {
    const cx = Number(attr(element, "cx"))
    const cy = Number(attr(element, "cy"))
    const r = Number(attr(element, "r"))
    if (Number.isFinite(cx) && Number.isFinite(cy) && Number.isFinite(r)) {
      paths.push(`M${cx-r},${cy}a${r},${r} 0 1,0 ${r*2},0a${r},${r} 0 1,0 -${r*2},0`)
    }
  }

  for (const element of svg.match(/<line[^>]*>/g) || []) {
    const x1 = attr(element, "x1"), y1 = attr(element, "y1")
    const x2 = attr(element, "x2"), y2 = attr(element, "y2")
    if ([x1, y1, x2, y2].every((value) => value !== null)) paths.push(`M${x1},${y1}L${x2},${y2}`)
  }

  for (const element of svg.match(/<poly(?:line|gon)[^>]*>/gi) || []) {
    const points = attr(element, "points")
    if (!points) continue
    const values = points.trim().split(/[\s,]+/)
    const pairs = []
    for (let i = 0; i + 1 < values.length; i += 2) pairs.push(`${values[i]},${values[i+1]}`)
    if (pairs.length >= 2) paths.push(`M${pairs.join("L")}${/^<polygon/i.test(element) ? "Z" : ""}`)
  }

  if (!paths.length) return null

  return {
    viewBox,
    paths,
    isStroke,
    strokeWidth: Number(attr(svg, "stroke-width")) || 2,
    strokeLinecap: attr(svg, "stroke-linecap") || "round",
    strokeLinejoin: attr(svg, "stroke-linejoin") || "round",
    defaultColor: "currentColor",
  }
}

async function resolveIcon(slug) {
  if (!slug || LOCAL_ICONS.has(slug)) return null
  if (slug.startsWith("lu:")) {
    const raw = slug.slice(3)
    const name = raw.startsWith("Lu") ? raw : `Lu${raw.replace(/(^|-)([a-zA-Z])/g, (_, _dash, c) => c.toUpperCase())}`
    return reactIconByName(name)
  }
  if (slug.startsWith("ri:")) return reactIconByName(slug.slice(3))
  return simpleIconBySlug(slug)
}

const recipes = fs.existsSync(recipesPath) ? JSON.parse(fs.readFileSync(recipesPath, "utf8")) : []
const requested = new Set()
for (const recipe of recipes) {
  const icon = recipe.icon || recipe.logo || recipe.brand
  if (icon && !LOCAL_ICONS.has(icon)) requested.add(icon)
}

const cache = {}
for (const slug of [...requested].sort()) {
  const resolved = await resolveIcon(slug)
  if (!resolved) {
    console.warn(`Icon not found: ${slug}`)
    continue
  }
  cache[slug] = resolved
  console.log(`Resolved icon: ${slug}`)
}

fs.mkdirSync(cacheDir, { recursive: true })
fs.writeFileSync(cachePath, `${JSON.stringify(cache, null, 2)}\n`)
console.log(`Wrote ${Object.keys(cache).length} resolved icons to ${path.relative(root, cachePath)}`)
