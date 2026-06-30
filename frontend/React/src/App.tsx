
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './layouts/Layout';
import Landing from './pages/Landing';
import DashboardHome from './pages/DashboardHome';
import CandidateSearch from './pages/CandidateSearch';
import CandidateProfile from './pages/CandidateProfile';
import Copilot from './pages/Copilot';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public Landing Page */}
        <Route path="/" element={<Landing />} />
        
        {/* Authenticated / App Layout */}
        <Route path="/" element={<Layout />}>
          <Route path="app" element={<DashboardHome />} />
          <Route path="search" element={<CandidateSearch />} />
          <Route path="candidate/:id" element={<CandidateProfile />} />
          <Route path="copilot" element={<Copilot />} />
        </Route>
        
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
