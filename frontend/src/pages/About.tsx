export default function About() {
  return (
    <div className="space-y-6">
      <div className="text-center space-y-2">
        <h1 className="text-3xl sm:text-4xl font-bold text-gray-900 dark:text-gray-100">
          About
        </h1>
        <p className="text-lg text-gray-600 dark:text-gray-400">
          Learn more about the Finnie AI Financial Assistant
        </p>
      </div>

      <div className="card">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-4">
          Finnie
        </h2>
        <p className="text-gray-700 dark:text-gray-300 mb-4">
          Capstone project: <strong>Applied Agentic AI for SWEs</strong> — democratizing financial literacy through intelligent conversational AI.
        </p>

        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">
          Data flow
        </h3>
        <p className="text-gray-700 dark:text-gray-300 mb-4">
          <code className="bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded text-sm">User Query → Workflow Router → Appropriate Agent(s) → RAG Retrieval → LLM Processing → Response → UI</code>
        </p>

        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">
          Agents
        </h3>
        <ul className="space-y-2 text-gray-700 dark:text-gray-300">
          <li className="flex items-center gap-2">
            <span className="font-medium">Finance Q&A</span>
            <span className="text-gray-500 dark:text-gray-400">— general financial education</span>
          </li>
          <li className="flex items-center gap-2">
            <span className="font-medium">Portfolio Analysis</span>
            <span className="text-gray-500 dark:text-gray-400">— allocation and diversification</span>
          </li>
          <li className="flex items-center gap-2">
            <span className="font-medium">Market Analysis</span>
            <span className="text-gray-500 dark:text-gray-400">— real-time quotes and trends</span>
          </li>
          <li className="flex items-center gap-2">
            <span className="font-medium">Goal Planning</span>
            <span className="text-gray-500 dark:text-gray-400">— retirement and savings goals</span>
          </li>
          <li className="flex items-center gap-2">
            <span className="font-medium">News Synthesizer</span>
            <span className="text-gray-500 dark:text-gray-400">— financial news</span>
          </li>
          <li className="flex items-center gap-2">
            <span className="font-medium">Tax Education</span>
            <span className="text-gray-500 dark:text-gray-400">— IRAs, 401(k)s, capital gains</span>
          </li>
        </ul>

        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">
          Tech
        </h3>
        <p className="text-gray-700 dark:text-gray-300 mb-4">
          LangChain, RAG (Chroma), FastAPI backend, React frontend. LLM: OpenAI or Gemini (set API key in backend .env).
        </p>

        <p className="text-sm text-gray-500 dark:text-gray-400 italic">
          This is for educational purposes only. Not financial advice.
        </p>
      </div>
    </div>
  )
}
