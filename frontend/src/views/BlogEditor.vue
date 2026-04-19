<template>
  <div class="editor-page">
    <header class="editor-header">
      <div class="editor-header-inner">
        <button class="back-btn" @click="goBack">← 返回</button>
        <h1>{{ isEdit ? '编辑文章' : '写文章' }}</h1>
        <div class="editor-actions">
          <button class="save-draft-btn" @click="saveDraft">存草稿</button>
          <button class="publish-btn" @click="publish">发布</button>
        </div>
      </div>
    </header>

    <div class="editor-body">
      <div class="editor-form">
        <input v-model="title" placeholder="文章标题" class="title-input" />

        <div class="form-row">
          <div class="form-group">
            <label>分类</label>
            <select v-model="categoryId" class="category-select">
              <option :value="null">无分类</option>
              <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
            </select>
          </div>
          <div class="form-group">
            <label>摘要</label>
            <input v-model="summary" placeholder="简短描述（可选）" class="summary-input" />
          </div>
        </div>

        <div class="editor-toolbar">
          <button class="tb-btn" @click="insertMarkdown('**', '**')" title="粗体">B</button>
          <button class="tb-btn" @click="insertMarkdown('*', '*')" title="斜体">I</button>
          <button class="tb-btn" @click="insertMarkdown('`', '`')" title="行内代码">&lt;/&gt;</button>
          <button class="tb-btn" @click="insertMarkdown('```\n', '\n```')" title="代码块">Code</button>
          <button class="tb-btn" @click="insertMarkdown('## ', '')" title="标题">H</button>
          <button class="tb-btn" @click="insertMarkdown('> ', '')" title="引用">Q</button>
          <button class="tb-btn" @click="insertMarkdown('- ', '')" title="列表">List</button>
          <button class="tb-btn" @click="insertMarkdown('[', '](url)')" title="链接">Link</button>
        </div>

        <div class="editor-area">
          <textarea
            ref="textareaRef"
            v-model="content"
            placeholder="支持 Markdown 语法，开始写作…"
            class="content-textarea"
          ></textarea>
          <div class="preview-panel" v-html="renderedPreview"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const router = useRouter()
const postId = route.params.id
const isEdit = computed(() => !!postId)

const title = ref('')
const content = ref('')
const summary = ref('')
const categoryId = ref(null)
const categories = ref([])
const textareaRef = ref(null)

async function fetchCategories() {
  try {
    const res = await axios.get('/api/blog/categories/')
    categories.value = res.data
  } catch (e) {
    console.error('获取分类失败', e)
  }
}

async function fetchPost() {
  if (!isEdit.value) return
  try {
    const res = await axios.get(`/api/blog/posts/${postId}/`)
    const post = res.data
    title.value = post.title
    content.value = post.content
    summary.value = post.summary || ''
    categoryId.value = post.category || null
  } catch (e) {
    console.error('获取文章失败', e)
  }
}

function insertMarkdown(before, after) {
  const ta = textareaRef.value
  if (!ta) return
  const start = ta.selectionStart
  const end = ta.selectionEnd
  const selected = content.value.substring(start, end)
  const replacement = before + (selected || '文本') + after
  content.value = content.value.substring(0, start) + replacement + content.value.substring(end)
  ta.focus()
  ta.selectionStart = start + before.length
  ta.selectionEnd = start + before.length + (selected || '文本').length
}

const renderedPreview = computed(() => {
  if (!content.value) return '<p style="color:#64748b">预览区域</p>'
  return window.renderMarkdown(content.value)
})

async function saveDraft() {
  const data = {
    title: title.value || '无标题',
    content: content.value,
    summary: summary.value,
    category: categoryId.value,
    is_published: false,
  }
  try {
    if (isEdit.value) {
      await axios.put(`/api/blog/posts/${postId}/`, data)
    } else {
      const res = await axios.post('/api/blog/posts/', data)
      router.replace(`/blog/${res.data.id}/edit`)
    }
    alert('草稿已保存')
  } catch (e) {
    console.error('保存失败', e)
    alert('保存失败')
  }
}

async function publish() {
  if (!title.value.trim()) { alert('请输入标题'); return }
  if (!content.value.trim()) { alert('请输入内容'); return }
  const data = {
    title: title.value.trim(),
    content: content.value,
    summary: summary.value,
    category: categoryId.value,
    is_published: true,
  }
  try {
    if (isEdit.value) {
      await axios.put(`/api/blog/posts/${postId}/`, data)
      router.push(`/blog/${postId}`)
    } else {
      const res = await axios.post('/api/blog/posts/', data)
      router.push(`/blog/${res.data.id}`)
    }
  } catch (e) {
    console.error('发布失败', e)
    alert('发布失败')
  }
}

function goBack() {
  router.push('/blog')
}

onMounted(() => {
  fetchCategories()
  if (isEdit.value) fetchPost()
})
</script>

<style scoped>
.editor-page {
  min-height: 100vh;
  color: #e6eef8;
  background: radial-gradient(ellipse at 20% 0%, rgba(255,202,40,0.06), transparent 50%),
              radial-gradient(ellipse at 80% 100%, rgba(41,98,255,0.06), transparent 50%),
              #0b1120;
}

/* ── 顶栏 ── */
.editor-header {
  background: rgba(255,255,255,0.02);
  border-bottom: 1px solid rgba(255,255,255,0.06);
  padding: 14px 0;
}
.editor-header-inner {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 48px;
  display: flex;
  align-items: center;
  gap: 16px;
}
.editor-header-inner h1 {
  margin: 0;
  font-size: 20px;
  font-weight: 700;
  flex: 1;
}
.back-btn {
  padding: 8px 16px;
  border-radius: 8px;
  background: rgba(255,255,255,0.1);
  border: 1px solid rgba(255,255,255,0.2);
  color: #fff;
  font-weight: 600;
  cursor: pointer;
}
.back-btn:hover { background: rgba(255,255,255,0.15); }
.editor-actions {
  display: flex;
  gap: 8px;
}
.save-draft-btn {
  padding: 8px 18px;
  border-radius: 8px;
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.12);
  color: #cbd5e1;
  font-weight: 600;
  cursor: pointer;
}
.save-draft-btn:hover { background: rgba(255,255,255,0.1); }
.publish-btn {
  padding: 8px 22px;
  border-radius: 8px;
  background: linear-gradient(135deg, #ffca28, #2962ff);
  color: #111827;
  font-weight: 700;
  border: none;
  cursor: pointer;
}
.publish-btn:hover { opacity: 0.85; }

/* ── 编辑区 ── */
.editor-body {
  max-width: 1400px;
  margin: 0 auto;
  padding: 28px 48px;
}
.editor-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.title-input {
  padding: 14px 18px;
  border-radius: 10px;
  border: 1px solid rgba(255,255,255,0.1);
  background: rgba(255,255,255,0.04);
  color: #fff;
  font-size: 22px;
  font-weight: 700;
}
.title-input:focus { outline: none; border-color: rgba(99,102,241,0.4); }
.title-input::placeholder { color: #475569; }

.form-row {
  display: flex;
  gap: 16px;
}
.form-group {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.form-group label {
  font-size: 12px;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.category-select {
  padding: 10px 14px;
  border-radius: 10px;
  border: 1px solid rgba(255,255,255,0.1);
  background: rgba(255,255,255,0.04);
  color: #cbd5e1;
  font-size: 14px;
}
.category-select:focus { outline: none; border-color: rgba(99,102,241,0.4); }
.category-select option { background: #1a1f2e; color: #cbd5e1; }
.summary-input {
  padding: 10px 14px;
  border-radius: 10px;
  border: 1px solid rgba(255,255,255,0.1);
  background: rgba(255,255,255,0.04);
  color: #cbd5e1;
  font-size: 14px;
}
.summary-input:focus { outline: none; border-color: rgba(99,102,241,0.4); }
.summary-input::placeholder { color: #475569; }

/* ── 工具栏 ── */
.editor-toolbar {
  display: flex;
  gap: 4px;
  padding: 8px 12px;
  border-radius: 10px 10px 0 0;
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.06);
  border-bottom: none;
}
.tb-btn {
  padding: 6px 12px;
  border-radius: 6px;
  border: none;
  background: transparent;
  color: #94a3b8;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s;
}
.tb-btn:hover { background: rgba(255,255,255,0.08); color: #e2e8f0; }

/* ── 编辑+预览 ── */
.editor-area {
  display: flex;
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 0 0 10px 10px;
  overflow: hidden;
  min-height: 500px;
}
.content-textarea {
  flex: 1;
  padding: 18px;
  border: none;
  background: rgba(255,255,255,0.02);
  color: #e2e8f0;
  font-size: 15px;
  line-height: 1.7;
  resize: none;
  font-family: 'Fira Code', 'Consolas', 'PingFang SC', 'Microsoft YaHei', monospace;
}
.content-textarea:focus { outline: none; }
.content-textarea::placeholder { color: #475569; }
.preview-panel {
  flex: 1;
  padding: 18px;
  border-left: 1px solid rgba(255,255,255,0.06);
  background: rgba(255,255,255,0.01);
  overflow-y: auto;
  font-size: 15px;
  line-height: 1.8;
  color: #cbd5e1;
}
.preview-panel :deep(h1) { font-size: 24px; font-weight: 800; color: #fff; margin: 20px 0 10px; }
.preview-panel :deep(h2) { font-size: 20px; font-weight: 700; color: #fff; margin: 16px 0 8px; }
.preview-panel :deep(h3) { font-size: 17px; font-weight: 700; color: #e2e8f0; margin: 12px 0 6px; }
.preview-panel :deep(code) {
  font-family: 'Fira Code', 'Consolas', monospace;
  background: rgba(255,255,255,0.06);
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 13px;
  color: #fbbf24;
}
.preview-panel :deep(pre) {
  background: #111827;
  border-radius: 8px;
  padding: 14px;
  overflow-x: auto;
}
.preview-panel :deep(pre code) { background: none; padding: 0; color: #e2e8f0; }
.preview-panel :deep(blockquote) {
  border-left: 3px solid #818cf8;
  padding: 8px 14px;
  background: rgba(99,102,241,0.06);
  color: #94a3b8;
  border-radius: 0 6px 6px 0;
  margin: 10px 0;
}
.preview-panel :deep(ul) { padding-left: 18px; }
.preview-panel :deep(a) { color: #818cf8; }

@media (max-width: 720px) {
  .editor-body { padding: 20px; }
  .editor-area { flex-direction: column; }
  .preview-panel { border-left: none; border-top: 1px solid rgba(255,255,255,0.06); }
  .form-row { flex-direction: column; }
  .editor-header-inner { padding: 0 20px; flex-wrap: wrap; }
}
</style>
