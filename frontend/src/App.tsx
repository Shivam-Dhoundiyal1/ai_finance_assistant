import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Chat from './pages/Chat'
import Portfolio from './pages/Portfolio'
import Market from './pages/Market'
import About from './pages/About'

export default function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Chat />} />
        <Route path="/portfolio" element={<Portfolio />} />
        <Route path="/market" element={<Market />} />
        <Route path="/about" element={<About />} />
      </Routes>
    </Layout>
  )
}
