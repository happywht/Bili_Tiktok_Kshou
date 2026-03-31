import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { Layout } from './components/layout/Layout'
import HomePage from './pages/HomePage'
import SearchPage from './pages/SearchPage'
import SummarizePage from './pages/SummarizePage'
import DigestPage from './pages/DigestPage'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<HomePage />} />
          <Route path="search" element={<SearchPage />} />
          <Route path="summarize" element={<SummarizePage />} />
          <Route path="digest" element={<DigestPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App
