import React from 'react';
import { BrowserRouter, Routes, Route, Link, useNavigate, useParams, useLocation } from 'react-router-dom';
import AdminPanel from './components/AdminPanel';
import ClinicianPanel from './components/ClinicianPanel';
import PatientListPanel from './components/PatientListPanel';
import PatientDetailPanel from './components/PatientDetailPanel';
import HomePage from './components/HomePage';
import './App.css';

// Wrapper component for PatientListPanel with router navigation
function PatientListRoute() {
  const navigate = useNavigate();

  const handleSelectPatient = (patientId: number) => {
    navigate(`/patients/${patientId}`);
  };

  return (
    <main style={{ padding: '0', background: '#ffffff', maxWidth: '1200px', margin: '0 auto' }}>
      <PatientListPanel onSelectPatient={handleSelectPatient} />
    </main>
  );
}

// Wrapper component for PatientDetailPanel with router navigation
function PatientDetailRoute() {
  const navigate = useNavigate();
  const { patientId } = useParams<{ patientId: string }>();

  const handleBackToPatients = () => {
    navigate('/patients');
  };

  return (
    <main style={{ padding: '0', background: '#ffffff', maxWidth: '1200px', margin: '0 auto' }}>
      <PatientDetailPanel patientId={Number(patientId)} onBack={handleBackToPatients} />
    </main>
  );
}

// Wrapper component for HomePage with router navigation
function HomeRoute() {
  const navigate = useNavigate();
  return <HomePage onNavigate={(view) => navigate(`/${view}`)} />;
}

// A simple component for the tab buttons
function TabButton({ to, children }: { to: string; children: React.ReactNode }) {
  const location = useLocation();
  const isActive = location.pathname === to || (to !== '/' && location.pathname.startsWith(to));

  return (
    <Link
      to={to}
      style={{
        padding: '10px 20px',
        fontSize: '16px',
        cursor: 'pointer',
        background: 'transparent',
        color: isActive ? '#005CA9' : '#666',
        border: 'none',
        marginRight: '5px',
        fontWeight: isActive ? 'bold' : 'normal',
        transition: 'all 0.2s',
        borderBottom: isActive ? '2px solid #005CA9' : 'none',
        textDecoration: 'none',
        display: 'inline-block'
      }}
    >
      {children}
    </Link>
  );
}

function AppContent() {
  const location = useLocation();
  const navigate = useNavigate();

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', width: '100%', margin: 0, padding: 0 }}>
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '10px 20px', borderBottom: '2px solid #005CA9', background: '#ffffff', width: '100%', boxSizing: 'border-box' }}>
        <img
          src="/myceliumailogo.png"
          alt="Mycelium AI Logo"
          style={{ height: '50px', cursor: 'pointer' }}
          onClick={() => navigate('/')}
        />

        <nav style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <TabButton to="/">🏠 Home</TabButton>
          <TabButton to="/patients">📋 Patient Records</TabButton>
          <TabButton to="/clinician">🩺 Doctor Demo</TabButton>
          <TabButton to="/admin">⚙️ Admin Dashboard</TabButton>
          <div style={{ display: 'flex', alignItems: 'center', gap: '15px', marginLeft: '20px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '5px', cursor: 'pointer' }}>
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#005CA9" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                <circle cx="12" cy="7" r="4"></circle>
              </svg>
              <span style={{ fontSize: '14px', color: '#005CA9' }}>User</span>
            </div>
            <button
              style={{
                background: 'transparent',
                border: 'none',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                padding: '4px'
              }}
              title="Logout"
            >
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#005CA9" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
                <polyline points="16 17 21 12 16 7"></polyline>
                <line x1="21" y1="12" x2="9" y2="12"></line>
              </svg>
            </button>
          </div>
        </nav>
      </header>

      <div style={{ flex: 1, width: '100%', fontFamily: 'sans-serif', padding: location.pathname === '/' ? '0' : '20px', boxSizing: 'border-box' }}>
        <Routes>
          <Route path="/" element={<HomeRoute />} />
          <Route path="/patients" element={<PatientListRoute />} />
          <Route path="/patients/:patientId" element={<PatientDetailRoute />} />
          <Route path="/clinician" element={
            <main style={{ padding: '20px', background: '#ffffff', maxWidth: '1200px', margin: '0 auto' }}>
              <ClinicianPanel />
            </main>
          } />
          <Route path="/admin" element={
            <main style={{ padding: '20px', background: '#ffffff', width: '100%', maxWidth: '1200px', margin: '0 auto' }}>
              <AdminPanel />
            </main>
          } />
        </Routes>
      </div>

      <footer style={{ background: '#005CA9', color: 'white', width: '100%', boxSizing: 'border-box' }}>
        <div style={{ padding: '20px', maxWidth: '1200px', margin: '0 auto' }}>
          <div className="upper-footer" style={{ textAlign: 'center', marginBottom: '10px' }}>
            {/* Upper footer content if needed */}
          </div>
          <div className="lower-footer" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div className="copyright">© 2025 Mycelium AI</div>
            <div className="links">
              <a href="#" style={{ color: 'white', textDecoration: 'none', marginLeft: '10px' }}>Privacy Policy</a>
              <a href="#" style={{ color: 'white', textDecoration: 'none', marginLeft: '10px' }}>Cookies Policy</a>
              <a href="#" style={{ color: 'white', textDecoration: 'none', marginLeft: '10px' }}>Terms of Service</a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <AppContent />
    </BrowserRouter>
  );
}

export default App;
