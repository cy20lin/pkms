import { Editor, rootCtx, defaultValueCtx } from '@milkdown/core'
import { nord } from '@milkdown/theme-nord'
import { commonmark } from '@milkdown/preset-commonmark'

async function main() {
  // 1. 從 FastAPI 拿 markdown
  const res = await fetch('/api/file')
  const { content } = await res.json()

  // 2. 建立 Milkdown editor
  const editor = await Editor.make()
    .config(ctx => {
      ctx.set(rootCtx, document.getElementById('editor')!)
      ctx.set(defaultValueCtx, content)
    })
    .use(nord)
    .use(commonmark)
    .create()

  // 3. 綁定 Save
  document.getElementById('save')!.onclick = async () => {
    const markdown = editor.action(ctx =>
      ctx.get(editor.ctx.serializerCtx)
    )

    await fetch('/api/file', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content: markdown }),
    })
  }
}

main()

