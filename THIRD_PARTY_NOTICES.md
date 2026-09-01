# Third-party notices

## ShieldCN

The local SVG presentation layer in this repository adapts visual design tokens, badge configuration ideas, and styling concepts from ShieldCN:

- Project: https://github.com/jal-co/shieldcn
- Copyright (c) 2026 Justin Levine
- License: MIT

The ShieldCN source is not vendored wholesale. This repository uses its own renderer tailored to repository traffic badges and charts.

Generated SVG assets have no runtime dependency on ShieldCN or any external badge or icon service. Some optional icons are resolved from third-party npm packages at build time by GitHub Actions and embedded into the generated SVG output.

MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

## Simple Icons

Badge recipes may resolve brand icons from Simple Icons at build time. The resulting SVG path data can be embedded directly into generated badge assets.

- Project: https://github.com/simple-icons/simple-icons
- Project license: CC0 1.0 Universal

Simple Icons notes that CC0 for the project does not imply that every individual brand icon is itself CC0. Individual icons may have separate copyright, trademark, licensing, or brand-guideline requirements. Where applicable, users should consult the license and brand-guideline metadata published by Simple Icons and the relevant brand owner.

Use of a brand icon in a generated badge does not imply affiliation with, sponsorship by, or endorsement from the corresponding brand owner.

## React Icons

Badge recipes may resolve icons from React Icons at build time, including Lucide shorthand such as `lu:Construction` and explicit React Icons identifiers such as `ri:FaRobot`. The resolved SVG path data can be embedded directly into generated badge assets.

- Project: https://github.com/react-icons/react-icons
- React Icons package copyright: Copyright 2018 kamijin_fanta <kamijin@live.jp>
- React Icons package license: MIT

React Icons aggregates icons from many upstream icon projects. Its own license explicitly notes that the icons come from other projects and that the license of each original icon project should be checked accordingly. Generated assets that include such icon path data therefore remain subject to the applicable upstream icon license where relevant.

MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
