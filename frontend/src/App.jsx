import { useState } from 'react'

const apiBase = 'http://localhost:8000'

function App() {
  const [resumeFile, setResumeFile] = useState(null)
  const [jobDescription, setJobDescription] = useState('')
  const [skillsFile, setSkillsFile] = useState(null)
  const [skills, setSkills] = useState([])
  const [analysis, setAnalysis] = useState(null)
  const [match, setMatch] = useState(null)
  const [updatedResume, setUpdatedResume] = useState(null)
  const [activeTab, setActiveTab] = useState('upload')
  const [markdownContent, setMarkdownContent] = useState('')
  const [markdownFile, setMarkdownFile] = useState(null)

  const handleFileChange = (event) => {
    setResumeFile(event.target.files?.[0] ?? null)
  }

  const handleSkillsFileChange = async (event) => {
    const file = event.target.files?.[0]
    if (!file) {
      setSkills([])
      setSkillsFile(null)
      return
    }
    setSkillsFile(file)
    const text = await file.text()
    const parsedSkills = text.split(/[\n,]/).map((skill) => skill.trim()).filter(Boolean)
    setSkills(parsedSkills)
  }

  const parseResume = async () => {
    if (!resumeFile) return
    const formData = new FormData()
    formData.append('file', resumeFile)
    const resp = await fetch(`${apiBase}/upload-resume`, {
      method: 'POST',
      body: formData,
    })
    const result = await resp.json()
    setAnalysis(result.data)
  }

  const analyzeAndMatch = async () => {
    const resumeText = analysis?.summary || ''
    const payload = {
      resume_text: resumeText,
      job_description: jobDescription,
      skills: skills,
    }
    const resp = await fetch(`${apiBase}/match-score`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
    const result = await resp.json()
    setMatch(result.data)
  }

  const generateResume = async () => {
    const payload = {
      analysis: analysis,
      match: match,
      job_description: jobDescription,
      skills: skills,
    }
    const resp = await fetch(`${apiBase}/generate-resume`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
    const result = await resp.json()
    setUpdatedResume(result.data)
  }

  const fetchMarkdownTemplate = async () => {
    try {
      const resp = await fetch(`${apiBase}/resume-template`)
      const result = await resp.json()
      setMarkdownContent(result.template)
    } catch (error) {
      console.error('Error fetching template:', error)
    }
  }

  const convertMarkdownToDocument = async (format) => {
    try {
      const formData = new FormData()
      formData.append('markdown_content', markdownContent)
      formData.append('format', format)
      if (skills.length > 0) {
        formData.append('enhanced_skills', skills.join(', '))
      }
      
      const resp = await fetch(`${apiBase}/convert-markdown`, {
        method: 'POST',
        body: formData,
      })
      const result = await resp.json()
      
      if (result.success) {
        // Trigger download
        const link = document.createElement('a')
        link.href = `${apiBase}${result.data.file}`
        link.download = `resume.${format}`
        link.click()
      }
    } catch (error) {
      console.error('Error converting markdown:', error)
    }
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 px-4 py-8">
      <div className="mx-auto w-full max-w-6xl rounded-3xl border border-slate-800 bg-slate-900/80 p-8 shadow-2xl shadow-slate-950/40">
        <h1 className="text-4xl font-semibold text-cyan-300">AI Resume Tailor</h1>
        <p className="mt-2 max-w-2xl text-slate-400">
          Upload your resume or edit markdown to create ATS-friendly resumes with matched skills and keywords.
        </p>

        {/* Tab Navigation */}
        <div className="mt-8 flex gap-4 border-b border-slate-700">
          <button
            onClick={() => setActiveTab('upload')}
            className={`px-6 py-3 font-semibold transition ${
              activeTab === 'upload'
                ? 'border-b-2 border-cyan-400 text-cyan-300'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Upload & Analyze
          </button>
          <button
            onClick={() => { setActiveTab('markdown'); fetchMarkdownTemplate(); }}
            className={`px-6 py-3 font-semibold transition ${
              activeTab === 'markdown'
                ? 'border-b-2 border-cyan-400 text-cyan-300'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Markdown Editor
          </button>
        </div>

        {/* Upload & Analyze Tab */}
        {activeTab === 'upload' && (
          <>
            <section className="mt-8 grid gap-6 md:grid-cols-2">
              <div className="space-y-4 rounded-3xl bg-slate-950/70 p-6">
                <h2 className="text-xl font-semibold text-slate-100">Resume Upload</h2>
                <input type="file" accept=".txt,.docx,.pdf" onChange={handleFileChange} className="w-full rounded-xl border border-slate-700 bg-slate-900 px-4 py-3 text-slate-100" />
                <button
                  onClick={parseResume}
                  className="w-full rounded-2xl bg-cyan-500 px-4 py-3 font-semibold text-slate-950 hover:bg-cyan-400"
                >
                  Parse Resume
                </button>
              </div>

              <div className="space-y-4 rounded-3xl bg-slate-950/70 p-6">
                <h2 className="text-xl font-semibold text-slate-100">Job Description</h2>
                <textarea
                  value={jobDescription}
                  onChange={(e) => setJobDescription(e.target.value)}
                  rows={8}
                  className="w-full rounded-2xl border border-slate-700 bg-slate-900 px-4 py-3 text-slate-100"
                />
                <label className="block text-slate-300">Skills File (text or CSV)</label>
                <input type="file" accept=".txt,.csv" onChange={handleSkillsFileChange} className="w-full rounded-2xl border border-slate-700 bg-slate-900 px-4 py-3 text-slate-100" />
                {skills.length > 0 && (
                  <p className="text-sm text-slate-400">Loaded {skills.length} skills: {skills.slice(0, 5).join(', ')}{skills.length > 5 ? '...' : ''}</p>
                )}
                <button
                  onClick={analyzeAndMatch}
                  className="w-full rounded-2xl bg-cyan-500 px-4 py-3 font-semibold text-slate-950 hover:bg-cyan-400"
                >
                  Analyze & Match
                </button>
                <button
                  onClick={generateResume}
                  className="w-full rounded-2xl bg-green-500 px-4 py-3 font-semibold text-slate-950 hover:bg-green-400"
                >
                  Generate Updated Resume
                </button>
              </div>
            </section>

            <section className="mt-8 grid gap-6 lg:grid-cols-2">
              <div className="rounded-3xl bg-slate-950/80 p-6">
                <h2 className="text-xl font-semibold text-slate-100">Parsed Resume</h2>
                <pre className="mt-4 max-h-72 overflow-auto rounded-2xl bg-slate-900 p-4 text-sm text-slate-200">
                  {analysis ? JSON.stringify(analysis, null, 2) : 'Parsed resume data will appear here.'}
                </pre>
              </div>
              <div className="rounded-3xl bg-slate-950/80 p-6">
                <h2 className="text-xl font-semibold text-slate-100">Match Results</h2>
                <pre className="mt-4 max-h-72 overflow-auto rounded-2xl bg-slate-900 p-4 text-sm text-slate-200">
                  {match ? JSON.stringify(match, null, 2) : 'Match analysis results will appear here.'}
                </pre>
              </div>
            </section>

            {updatedResume && (
              <section className="mt-8">
                <div className="rounded-3xl bg-slate-950/80 p-6">
                  <h2 className="text-xl font-semibold text-slate-100">Updated Resume</h2>
                  <div className="mt-4 grid gap-4 md:grid-cols-2">
                    <div>
                      <h3 className="font-semibold text-slate-200">Content</h3>
                      <pre className="mt-2 max-h-72 overflow-auto rounded-2xl bg-slate-900 p-4 text-sm text-slate-200">
                        {JSON.stringify(updatedResume.updated_resume, null, 2)}
                      </pre>
                    </div>
                    <div>
                      <h3 className="font-semibold text-slate-200">Downloads</h3>
                      <div className="mt-2 space-y-2">
                        <a
                          href={`${apiBase}/download-resume?format=docx`}
                          download="resume.docx"
                          className="block rounded-2xl bg-blue-500 px-4 py-3 text-center font-semibold text-white hover:bg-blue-400"
                        >
                          Download DOCX
                        </a>
                        <a
                          href={`${apiBase}/download-resume?format=pdf`}
                          download="resume.pdf"
                          className="block rounded-2xl bg-red-500 px-4 py-3 text-center font-semibold text-white hover:bg-red-400"
                        >
                          Download PDF
                        </a>
                      </div>
                    </div>
                  </div>
                </div>
              </section>
            )}
          </>
        )}

        {/* Markdown Editor Tab */}
        {activeTab === 'markdown' && (
          <>
            <section className="mt-8">
              <div className="rounded-3xl bg-slate-950/70 p-6 space-y-4">
                <h2 className="text-xl font-semibold text-slate-100">Edit Resume (Markdown)</h2>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                      Enhanced Skills (comma-separated, will be highlighted in pink)
                    </label>
                    <input
                      type="text"
                      value={skills.join(', ')}
                      onChange={(e) => setSkills(e.target.value.split(',').map(s => s.trim()).filter(Boolean))}
                      placeholder="Python, React, FastAPI, Machine Learning"
                      className="w-full rounded-xl border border-slate-700 bg-slate-900 px-4 py-3 text-slate-100"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                      Resume Content (Markdown)
                    </label>
                    <textarea
                      value={markdownContent}
                      onChange={(e) => setMarkdownContent(e.target.value)}
                      rows={20}
                      placeholder="# Your Name
**Email:** email@example.com | **Phone:** +1 (XXX) XXX-XXXX

## Summary
Your professional summary...

## Skills
- Python, JavaScript
- React, FastAPI"
                      className="w-full rounded-2xl border border-slate-700 bg-slate-900 px-4 py-3 font-mono text-sm text-slate-100"
                    />
                  </div>
                </div>
                <div className="grid gap-2 md:grid-cols-2">
                  <button
                    onClick={() => convertMarkdownToDocument('docx')}
                    className="rounded-2xl bg-blue-500 px-4 py-3 font-semibold text-white hover:bg-blue-400"
                  >
                    Convert to DOCX
                  </button>
                  <button
                    onClick={() => convertMarkdownToDocument('pdf')}
                    className="rounded-2xl bg-red-500 px-4 py-3 font-semibold text-white hover:bg-red-400"
                  >
                    Convert to PDF
                  </button>
                </div>
              </div>
            </section>

            <section className="mt-8">
              <div className="rounded-3xl bg-slate-950/80 p-6">
                <h3 className="text-lg font-semibold text-slate-200 mb-4">Markdown Guide</h3>
                <div className="grid gap-4 md:grid-cols-2 text-sm text-slate-300">
                  <div>
                    <h4 className="font-bold text-cyan-300 mb-2">Formatting</h4>
                    <ul className="space-y-1">
                      <li><code className="bg-slate-900 px-2"># Heading 1</code></li>
                      <li><code className="bg-slate-900 px-2">## Heading 2</code></li>
                      <li><code className="bg-slate-900 px-2">**Bold Text**</code></li>
                      <li><code className="bg-slate-900 px-2">- Bullet point</code></li>
                    </ul>
                  </div>
                  <div>
                    <h4 className="font-bold text-cyan-300 mb-2">Sections</h4>
                    <ul className="space-y-1">
                      <li>Professional Summary</li>
                      <li>Skills</li>
                      <li>Experience</li>
                      <li>Education</li>
                      <li>Certifications</li>
                    </ul>
                  </div>
                </div>
              </div>
            </section>
          </>
        )}
      </div>
    </div>
  )
}

export default App
