import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface StatusData {
  system_status: string;
  network_status: string;
  student_library_version: string;
  last_sync: string;
  my_specialty_proof: string;
}

interface StudentModel {
  id: string;
  name: string;
  version: string;
  specialty: string;
  status: string;
}

// Section helper component for consistent styling
const Section: React.FC<{ title: string; children: React.ReactNode }> = ({ title, children }) => (
  <div style={{
    background: 'white',
    padding: 'clamp(20px, 4vw, 30px)',
    borderRadius: '12px',
    boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
    marginBottom: 'clamp(20px, 4vw, 30px)',
    border: '1px solid #e0e0e0'
  }}>
    <h2 style={{
      color: '#005CA9',
      marginBottom: '20px',
      fontSize: 'clamp(20px, 4vw, 24px)',
      display: 'flex',
      alignItems: 'center',
      gap: '10px'
    }}>
      {title}
    </h2>
    {children}
  </div>
);

const AdminPanel: React.FC = () => {
  const [statusData, setStatusData] = useState<StatusData | null>(null);
  const [studentLibrary, setStudentLibrary] = useState<StudentModel[]>([]);
  const [isSyncing, setIsSyncing] = useState(false);
  const [syncStatus, setSyncStatus] = useState('');
  const [isTraining, setIsTraining] = useState(false);
  const [trainingLog, setTrainingLog] = useState<string[]>([]);
  const [privacyLevel, setPrivacyLevel] = useState(50);
  const [modelControl, setModelControl] = useState('balanced');

  // Fetch status and library on mount
  useEffect(() => {
    fetchStatus();
    fetchStudentLibrary();
  }, []);

  // Update privacy level in backend when slider changes
  const handlePrivacyChange = async (newLevel: number) => {
    setPrivacyLevel(newLevel);

    // Map slider (0-100) to epsilon (10.0-0.1): higher slider = higher privacy = lower epsilon
    const epsilon = 10.0 - (newLevel / 100) * 9.9;

    try {
      await axios.post(`${API_URL}/api/update-privacy`, { epsilon });
      console.log(`Privacy updated: slider=${newLevel}, epsilon=${epsilon.toFixed(2)}`);
    } catch (error) {
      console.error('Error updating privacy:', error);
    }
  };

  const fetchStatus = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/status`);
      setStatusData(response.data);
    } catch (error) {
      console.error('Error fetching status:', error);
    }
  };

  const fetchStudentLibrary = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/student-library`);
      setStudentLibrary(response.data);
    } catch (error) {
      console.error('Error fetching student library:', error);
    }
  };

  const handleSyncLibrary = async () => {
    setIsSyncing(true);
    setSyncStatus('🔄 Syncing... downloading latest Student models from network...');

    try {
      const response = await axios.post(`${API_URL}/api/sync-library`);
      setSyncStatus(`✅ Sync Complete! New Library: ${response.data.new_library_version}`);
      // Refresh both status and library after sync
      await fetchStatus();
      await fetchStudentLibrary();
    } catch (error) {
      setSyncStatus('❌ Sync failed. Please check your network connection.');
      console.error('Error syncing library:', error);
    } finally {
      setIsSyncing(false);
    }
  };

  const handleToggleModel = async (modelId: string) => {
    // Optimistically update UI
    const newStatus = studentLibrary.find(m => m.id === modelId)?.status === 'Active' ? 'Inactive' : 'Active';

    setStudentLibrary(prevLibrary =>
      prevLibrary.map(model =>
        model.id === modelId
          ? { ...model, status: newStatus }
          : model
      )
    );

    // Send to backend (fire and forget - no need to await)
    try {
      await axios.post(`${API_URL}/api/update-model-status`, null, {
        params: { model_id: modelId, status: newStatus }
      });
      console.log(`Model ${modelId} status updated to ${newStatus}`);
    } catch (error) {
      console.error('Error updating model status:', error);
      // Revert on error
      setStudentLibrary(prevLibrary =>
        prevLibrary.map(model =>
          model.id === modelId
            ? { ...model, status: model.status === 'Active' ? 'Inactive' : 'Active' }
            : model
        )
      );
    }
  };

  const handleRunDistillation = async () => {
    setIsTraining(true);
    setTrainingLog(['[1/3] Starting local "Teacher" model training... (simulated 10s job)']);

    // Simulate log progression
    setTimeout(() => {
      setTrainingLog(log => [...log, '[2/3] "Teacher" trained. Distilling "Student Model"...']);
    }, 4000);

    // Make the actual API call after 8 seconds
    setTimeout(async () => {
      try {
        const response = await axios.post(`${API_URL}/api/run-distillation`);
        setTrainingLog(log => [...log, '[3/3] FSO model creation complete.']);
        setTrainingLog(log => [...log, `✅ Contribution successful! Uploaded: ${response.data.new_student_model_id}`]);
        setTrainingLog(log => [...log, '']);
        setTrainingLog(log => [...log, '🎉 Your contribution is now part of the network! Other hospitals can benefit from your expertise.']);
      } catch (error) {
        setTrainingLog(log => [...log, '❌ Process failed. Please try again.']);
        console.error('Error running distillation:', error);
      } finally {
        setIsTraining(false);
      }
    }, 8000);
  };

  return (
    <div style={{ fontFamily: 'sans-serif', padding: '0 clamp(10px, 2vw, 0px)' }}>
      {/* Simple Title */}
      <h1 style={{
        margin: '0 0 clamp(20px, 4vw, 30px) 0',
        fontSize: 'clamp(24px, 4vw, 28px)',
        color: '#005CA9'
      }}>
        Admin Dashboard
      </h1>

      {/* Section 1: Mycelium Network Map */}
      <Section title="🌐 Mycelium Network Map">
        <div style={{
          position: 'relative',
          height: '250px',
          background: '#f8f9fa',
          borderRadius: '8px',
          border: '1px solid #dee2e6',
          marginBottom: '20px',
          overflow: 'hidden'
        }}>
          {/* Mycelium Broker (Cloud) - with pulse animation */}
          <div style={{
            position: 'absolute',
            top: '20px',
            left: '50%',
            transform: 'translateX(-50%)',
            background: '#005CA9',
            color: 'white',
            padding: '15px 25px',
            borderRadius: '10px',
            fontSize: '14px',
            fontWeight: '600',
            boxShadow: '0 4px 10px rgba(0, 92, 169, 0.3)',
            textAlign: 'center',
            minWidth: '150px',
            animation: 'pulse-node 2s ease-in-out infinite'
          }}>
            ☁️ Mycelium Broker
            <div style={{ fontSize: '11px', marginTop: '5px', opacity: 0.9 }}>Network Coordinator</div>
          </div>

          {/* Animated Data Packets on Connection Lines */}
          <div style={{
            position: 'absolute',
            top: '75px',
            left: '25%',
            width: '150px',
            height: '2px',
            background: '#005CA9',
            transform: 'rotate(-25deg)',
            transformOrigin: 'left'
          }}>
            {/* Data packet moving left to broker */}
            <div style={{
              position: 'absolute',
              top: '-4px',
              left: '0',
              width: '10px',
              height: '10px',
              background: '#28a745',
              borderRadius: '50%',
              boxShadow: '0 0 10px #28a745',
              animation: 'packet-to-broker-left 3s ease-in-out infinite'
            }} />
          </div>

          <div style={{
            position: 'absolute',
            top: '75px',
            right: '25%',
            width: '150px',
            height: '2px',
            background: '#005CA9',
            transform: 'rotate(25deg)',
            transformOrigin: 'right'
          }}>
            {/* Data packet moving right to broker */}
            <div style={{
              position: 'absolute',
              top: '-4px',
              right: '0',
              width: '10px',
              height: '10px',
              background: '#ffc107',
              borderRadius: '50%',
              boxShadow: '0 0 10px #ffc107',
              animation: 'packet-to-broker-right 3s ease-in-out infinite 1s'
            }} />
          </div>

          {/* Last Sync Label with activity indicator */}
          <div style={{
            position: 'absolute',
            top: '95px',
            left: '15%',
            fontSize: '11px',
            color: '#005CA9',
            fontWeight: '600',
            background: 'white',
            padding: '3px 8px',
            borderRadius: '4px',
            boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
            display: 'flex',
            alignItems: 'center',
            gap: '5px'
          }}>
            <span style={{
              display: 'inline-block',
              width: '6px',
              height: '6px',
              background: '#28a745',
              borderRadius: '50%',
              animation: 'blink 2s ease-in-out infinite'
            }} />
            Last Sync: {statusData?.last_sync || 'Loading...'}
          </div>

          {/* Your On-Premise Node with heartbeat */}
          <div style={{
            position: 'absolute',
            bottom: '20px',
            left: '20px',
            background: 'white',
            border: `3px solid ${statusData?.system_status === 'Operational' ? '#005CA9' : '#6c757d'}`,
            color: '#005CA9',
            padding: '15px 20px',
            borderRadius: '10px',
            fontSize: '14px',
            fontWeight: '600',
            boxShadow: '0 4px 10px rgba(0,92,169,0.2)',
            minWidth: '180px',
            animation: statusData?.system_status === 'Operational' ? 'heartbeat 2s ease-in-out infinite' : 'none'
          }}>
            🏥 Your Node
            <div style={{ fontSize: '11px', marginTop: '5px', color: '#666' }}>
              Status: {statusData?.system_status || 'Loading...'}
            </div>
            <div style={{
              marginTop: '5px',
              fontSize: '10px',
              color: statusData?.system_status === 'Operational' ? '#005CA9' : '#6c757d',
              fontWeight: '600',
              display: 'flex',
              alignItems: 'center',
              gap: '5px'
            }}>
              <span style={{
                display: 'inline-block',
                width: '8px',
                height: '8px',
                background: statusData?.system_status === 'Operational' ? '#28a745' : '#6c757d',
                borderRadius: '50%',
                animation: statusData?.system_status === 'Operational' ? 'pulse-dot 1.5s ease-in-out infinite' : 'none'
              }} />
              {statusData?.system_status === 'Operational' ? 'ONLINE' : 'OFFLINE'}
            </div>
          </div>

          {/* Peer Nodes (Network) with activity waves */}
          <div style={{
            position: 'absolute',
            bottom: '20px',
            right: '20px',
            background: 'white',
            border: '3px solid #005CA9',
            color: '#005CA9',
            padding: '15px 20px',
            borderRadius: '10px',
            fontSize: '14px',
            fontWeight: '600',
            boxShadow: '0 4px 10px rgba(0,0,0,0.1)',
            minWidth: '180px'
          }}>
            🌐 Peer Nodes
            <div style={{ fontSize: '11px', marginTop: '5px', color: '#666' }}>
              {statusData?.network_status || 'Loading...'}
            </div>
            <div style={{
              marginTop: '5px',
              fontSize: '10px',
              color: '#005CA9',
              fontWeight: '600',
              display: 'flex',
              alignItems: 'center',
              gap: '5px'
            }}>
              <span style={{
                display: 'inline-block',
                width: '8px',
                height: '8px',
                background: '#28a745',
                borderRadius: '50%',
                animation: 'pulse-dot 1.5s ease-in-out infinite 0.5s'
              }} />
              CONNECTED
            </div>
          </div>

          {/* CSS Animations */}
          <style>
            {`
              @keyframes packet-to-broker-left {
                0% { left: 0; opacity: 0; }
                10% { opacity: 1; }
                90% { opacity: 1; }
                100% { left: 100%; opacity: 0; }
              }
              
              @keyframes packet-to-broker-right {
                0% { right: 0; opacity: 0; }
                10% { opacity: 1; }
                90% { opacity: 1; }
                100% { right: 100%; opacity: 0; }
              }
              
              @keyframes pulse-node {
                0%, 100% { 
                  box-shadow: 0 4px 10px rgba(0, 92, 169, 0.3); 
                }
                50% { 
                  box-shadow: 0 4px 20px rgba(0, 92, 169, 0.6), 0 0 30px rgba(0, 92, 169, 0.3); 
                }
              }
              
              @keyframes heartbeat {
                0%, 100% { 
                  transform: scale(1); 
                }
                10% { 
                  transform: scale(1.02); 
                }
                20% { 
                  transform: scale(1); 
                }
              }
              
              @keyframes pulse-dot {
                0%, 100% { 
                  opacity: 1; 
                  transform: scale(1); 
                }
                50% { 
                  opacity: 0.3; 
                  transform: scale(0.8); 
                }
              }
              
              @keyframes blink {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.3; }
              }
            `}
          </style>
        </div>

        <button
          onClick={handleSyncLibrary}
          disabled={isSyncing}
          style={{
            padding: 'clamp(12px, 2vw, 15px) clamp(25px, 4vw, 35px)',
            background: isSyncing ? '#ccc' : '#005CA9',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            cursor: isSyncing ? 'not-allowed' : 'pointer',
            fontSize: 'clamp(14px, 2vw, 16px)',
            fontWeight: '600',
            width: '100%',
            maxWidth: '400px',
            display: 'block'
          }}
        >
          {isSyncing ? '⏳ Syncing...' : '📥 Force Sync Student Library'}
        </button>

        {syncStatus && (
          <div style={{
            marginTop: '15px',
            padding: '12px',
            background: syncStatus.includes('✅') ? '#d4edda' : '#f8f9fa',
            borderRadius: '8px',
            fontSize: '14px',
            border: `1px solid ${syncStatus.includes('✅') ? '#28a745' : '#dee2e6'}`
          }}>
            {syncStatus}
          </div>
        )}
      </Section>

      {/* Section 2: Student Library Management */}
      <Section title="📚 On-Premise Student Library Management">
        {studentLibrary.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '40px', color: '#666' }}>
            <div style={{ fontSize: '48px', marginBottom: '15px' }}>⏳</div>
            <p>Loading student library from network...</p>
          </div>
        ) : (
          <>
            <div style={{ overflowX: 'auto' }}>
              <table style={{
                width: '100%',
                borderCollapse: 'collapse',
                minWidth: '600px'
              }}>
                <thead>
                  <tr style={{ background: '#e6f2ff', borderBottom: '2px solid #005CA9' }}>
                    <th style={{ padding: '12px', textAlign: 'left', fontSize: 'clamp(12px, 2vw, 14px)' }}>Model ID</th>
                    <th style={{ padding: '12px', textAlign: 'left', fontSize: 'clamp(12px, 2vw, 14px)' }}>Specialty</th>
                    <th style={{ padding: '12px', textAlign: 'left', fontSize: 'clamp(12px, 2vw, 14px)' }}>Version</th>
                    <th style={{ padding: '12px', textAlign: 'center', fontSize: 'clamp(12px, 2vw, 14px)' }}>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {studentLibrary.map((model) => (
                    <tr key={model.id} style={{ borderBottom: '1px solid #dee2e6' }}>
                      <td style={{ padding: '12px', fontSize: 'clamp(12px, 2vw, 14px)' }}>{model.name}</td>
                      <td style={{ padding: '12px', fontSize: 'clamp(12px, 2vw, 14px)' }}>
                        <span style={{
                          background: '#fff3cd',
                          padding: '3px 8px',
                          borderRadius: '4px',
                          fontSize: '12px',
                          fontWeight: '600',
                          color: '#856404'
                        }}>
                          {model.specialty}
                        </span>
                      </td>
                      <td style={{ padding: '12px', fontSize: 'clamp(12px, 2vw, 14px)', color: '#666' }}>
                        {model.version}
                      </td>
                      <td style={{ padding: '12px', textAlign: 'center' }}>
                        <label style={{
                          position: 'relative',
                          display: 'inline-block',
                          width: '50px',
                          height: '24px',
                          cursor: 'pointer'
                        }}>
                          <input
                            type="checkbox"
                            checked={model.status === 'Active'}
                            onChange={() => handleToggleModel(model.id)}
                            style={{ display: 'none' }}
                          />
                          <span style={{
                            position: 'absolute',
                            top: 0,
                            left: 0,
                            right: 0,
                            bottom: 0,
                            background: model.status === 'Active' ? '#005CA9' : '#ccc',
                            borderRadius: '24px',
                            transition: 'all 0.3s'
                          }}>
                            <span style={{
                              position: 'absolute',
                              content: '',
                              height: '18px',
                              width: '18px',
                              left: model.status === 'Active' ? '28px' : '3px',
                              bottom: '3px',
                              background: 'white',
                              borderRadius: '50%',
                              transition: 'all 0.3s'
                            }} />
                          </span>
                        </label>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <p style={{
              marginTop: '15px',
              fontSize: 'clamp(12px, 2vw, 13px)',
              color: '#666',
              fontStyle: 'italic',
              textAlign: 'center'
            }}>
              ⚠️ Deactivated models will be excluded from all FSO Consensus Panels.
            </p>
          </>
        )}
      </Section>

      {/* Section 3: Network Contribution */}
      <Section title="🎁 Network Contribution - The 'Give-One, Get-One' Model">
        <div style={{
          background: '#f8f9fa',
          padding: '20px',
          borderRadius: '8px',
          marginBottom: '20px',
          border: '1px solid #dee2e6'
        }}>
          <h3 style={{ margin: '0 0 10px 0', color: '#005CA9', fontSize: 'clamp(16px, 2.5vw, 18px)' }}>
            💡 How It Works: "Quid Pro Quo"
          </h3>
          <p style={{ margin: 0, fontSize: 'clamp(13px, 2vw, 14px)', color: '#666', lineHeight: '1.6' }}>
            To access the network's Student Library, you must contribute your own expertise.
            Train a local "Teacher" model on your unique patient data, then use FSO to create a
            privacy-preserving "Student" model. Your Student joins the library, and everyone benefits!
          </p>
        </div>

        <button
          onClick={handleRunDistillation}
          disabled={isTraining}
          style={{
            padding: 'clamp(12px, 2vw, 15px) clamp(25px, 4vw, 35px)',
            background: isTraining ? '#6c757d' : '#005CA9',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            cursor: isTraining ? 'not-allowed' : 'pointer',
            fontSize: 'clamp(14px, 2vw, 16px)',
            fontWeight: '600',
            width: '100%',
            maxWidth: '500px',
            display: 'block',
            boxShadow: isTraining ? 'none' : '0 4px 6px rgba(0, 92, 169, 0.3)'
          }}
        >
          {isTraining ? '⏳ Training & Processing...' : '🚀 Run Local Training & FSO'}
        </button>

        {/* Live Training Log Console */}
        {trainingLog.length > 0 && (
          <div style={{
            marginTop: '20px',
            background: '#1a1a1a',
            color: '#00ff00',
            padding: 'clamp(15px, 3vw, 20px)',
            borderRadius: '8px',
            fontFamily: 'Monaco, Consolas, "Courier New", monospace',
            fontSize: 'clamp(11px, 1.8vw, 13px)',
            maxHeight: '300px',
            overflowY: 'auto',
            border: '1px solid #333',
            boxShadow: 'none'
          }}>
            <div style={{ marginBottom: '10px', color: '#00ff00', fontSize: 'clamp(12px, 2vw, 14px)' }}>
              📊 Training Console Output:
            </div>
            {trainingLog.map((log, index) => (
              <p key={index} style={{ margin: '5px 0', lineHeight: '1.5' }}>
                {log}
              </p>
            ))}
          </div>
        )}
      </Section>

      {/* Section 4: Governance & Privacy Levers */}
      <Section title="⚙️ Governance & Privacy Controls">
        <div style={{ marginBottom: '25px' }}>
          <label style={{
            display: 'block',
            marginBottom: '10px',
            fontSize: 'clamp(14px, 2vw, 16px)',
            fontWeight: '600',
            color: '#333'
          }}>
            🔒 Privacy-Accuracy Trade-off
          </label>
          <div style={{ display: 'flex', alignItems: 'center', gap: '15px', flexWrap: 'wrap' }}>
            <span style={{ fontSize: 'clamp(12px, 2vw, 14px)', color: '#666', minWidth: '100px' }}>
              Max Privacy
            </span>
            <input
              type="range"
              min="0"
              max="100"
              value={privacyLevel}
              onChange={(e) => handlePrivacyChange(Number(e.target.value))}
              style={{
                flex: 1,
                minWidth: '200px',
                accentColor: '#005CA9'
              }}
            />
            <span style={{ fontSize: 'clamp(12px, 2vw, 14px)', color: '#666', minWidth: '100px' }}>
              Max Accuracy
            </span>
          </div>
          <div style={{
            marginTop: '10px',
            textAlign: 'center',
            fontSize: 'clamp(13px, 2vw, 14px)',
            color: '#005CA9',
            fontWeight: '600'
          }}>
            Current Setting: {privacyLevel}% (
            {privacyLevel < 30 ? 'Maximum Privacy' :
              privacyLevel < 70 ? 'Balanced' :
                'Maximum Accuracy'})
          </div>
        </div>

        <div>
          <label style={{
            display: 'block',
            marginBottom: '10px',
            fontSize: 'clamp(14px, 2vw, 16px)',
            fontWeight: '600',
            color: '#333'
          }}>
            🎯 Clinical Model Control
          </label>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {['local-only', 'balanced', 'network-first'].map((option) => (
              <label
                key={option}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '10px',
                  padding: '12px',
                  background: modelControl === option ? '#e6f2ff' : '#f8f9fa',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  border: `2px solid ${modelControl === option ? '#005CA9' : '#dee2e6'}`,
                  fontSize: 'clamp(13px, 2vw, 14px)'
                }}
              >
                <input
                  type="radio"
                  value={option}
                  checked={modelControl === option}
                  onChange={(e) => setModelControl(e.target.value)}
                  style={{ accentColor: '#005CA9' }}
                />
                <span>
                  {option === 'local-only' && '🏥 Local-Only (Maximum Privacy, Lower Accuracy)'}
                  {option === 'balanced' && '⚖️ Balanced (Recommended - FSO Enabled)'}
                  {option === 'network-first' && '🌐 Network-First (Maximum Accuracy, More Collaboration)'}
                </span>
              </label>
            ))}
          </div>
        </div>
      </Section>
    </div>
  );
};

export default AdminPanel;
