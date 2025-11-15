import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = 'http://127.0.0.1:8000';

interface Patient {
  id: number;
  first_name: string;
  last_name: string;
  age: number | null;
  sex: string | null;
  needs_review: boolean;
  pending_reviews: number;
  last_follow_up_date: string | null;
}

interface PatientListPanelProps {
  onSelectPatient: (patientId: number) => void;
}

const PatientListPanel: React.FC<PatientListPanelProps> = ({ onSelectPatient }) => {
  const [patients, setPatients] = useState<Patient[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadPatients();
  }, []);

  const loadPatients = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await axios.get(`${API_URL}/patients`);
      setPatients(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load patients');
      console.error('Error loading patients:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return 'N/A';
    return new Date(dateStr).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  return (
    <div style={{ fontFamily: 'sans-serif', maxWidth: '1200px', margin: '0 auto', padding: '20px' }}>
      {/* Header */}
      <div style={{ 
        background: 'linear-gradient(135deg, #005CA9 0%, #0077CC 100%)', 
        color: 'white', 
        padding: '20px', 
        borderRadius: '8px',
        marginBottom: '20px'
      }}>
        <h1 style={{ margin: '0 0 10px 0', fontSize: '28px' }}>📋 Patient Review Dashboard</h1>
        <p style={{ margin: 0, opacity: 0.9 }}>Review and manage patient X-ray examinations</p>
      </div>

      {/* Error Display */}
      {error && (
        <div style={{ 
          margin: '20px 0', 
          padding: '15px', 
          background: '#f8d7da', 
          color: '#721c24',
          borderRadius: '6px',
          border: '1px solid #f5c6cb'
        }}>
          ❌ {error}
        </div>
      )}

      {/* Loading State */}
      {isLoading && (
        <div style={{ textAlign: 'center', padding: '40px', color: '#666' }}>
          <div style={{ fontSize: '40px', marginBottom: '10px' }}>⏳</div>
          Loading patients...
        </div>
      )}

      {/* Patient List */}
      {!isLoading && patients.length === 0 && !error && (
        <div style={{ 
          textAlign: 'center', 
          padding: '60px', 
          background: '#f8f9fa',
          borderRadius: '8px',
          color: '#666'
        }}>
          <div style={{ fontSize: '48px', marginBottom: '15px' }}>📁</div>
          <h3 style={{ margin: '0 0 10px 0' }}>No Patients Found</h3>
          <p>Add patients through the system to begin reviewing cases.</p>
        </div>
      )}

      {!isLoading && patients.length > 0 && (
        <div style={{ background: 'white', borderRadius: '8px', overflow: 'hidden', boxShadow: '0 2px 8px rgba(0,0,0,0.1)' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ background: '#e6f2ff', borderBottom: '2px solid #005CA9' }}>
                <th style={{ padding: '15px', textAlign: 'left', fontWeight: '600' }}>Patient</th>
                <th style={{ padding: '15px', textAlign: 'left', fontWeight: '600' }}>Age</th>
                <th style={{ padding: '15px', textAlign: 'left', fontWeight: '600' }}>Sex</th>
                <th style={{ padding: '15px', textAlign: 'left', fontWeight: '600' }}>Review Status</th>
                <th style={{ padding: '15px', textAlign: 'left', fontWeight: '600' }}>Last Follow-up</th>
                <th style={{ padding: '15px', textAlign: 'center', fontWeight: '600' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {patients.map((patient) => (
                <tr 
                  key={patient.id} 
                  style={{ 
                    borderBottom: '1px solid #dee2e6',
                    transition: 'background 0.2s',
                    cursor: 'pointer'
                  }}
                  onMouseEnter={(e) => e.currentTarget.style.background = '#f8f9fa'}
                  onMouseLeave={(e) => e.currentTarget.style.background = 'white'}
                >
                  <td style={{ padding: '15px' }}>
                    <div style={{ fontWeight: '500', color: '#005CA9' }}>
                      {patient.first_name} {patient.last_name}
                    </div>
                    <div style={{ fontSize: '12px', color: '#666', marginTop: '2px' }}>
                      ID: {patient.id}
                    </div>
                  </td>
                  <td style={{ padding: '15px', color: '#333' }}>
                    {patient.age || 'N/A'}
                  </td>
                  <td style={{ padding: '15px', color: '#333' }}>
                    {patient.sex || 'N/A'}
                  </td>
                  <td style={{ padding: '15px' }}>
                    {patient.needs_review ? (
                      <span style={{ 
                        display: 'inline-block',
                        padding: '4px 12px',
                        background: '#fff3cd',
                        color: '#856404',
                        borderRadius: '12px',
                        fontSize: '13px',
                        fontWeight: '500'
                      }}>
                        ⚠️ {patient.pending_reviews} Pending
                      </span>
                    ) : (
                      <span style={{ 
                        display: 'inline-block',
                        padding: '4px 12px',
                        background: '#d4edda',
                        color: '#155724',
                        borderRadius: '12px',
                        fontSize: '13px',
                        fontWeight: '500'
                      }}>
                        ✓ Reviewed
                      </span>
                    )}
                  </td>
                  <td style={{ padding: '15px', color: '#333' }}>
                    {formatDate(patient.last_follow_up_date)}
                  </td>
                  <td style={{ padding: '15px', textAlign: 'center' }}>
                    <button
                      onClick={() => onSelectPatient(patient.id)}
                      style={{
                        padding: '8px 16px',
                        background: '#005CA9',
                        color: 'white',
                        border: 'none',
                        borderRadius: '6px',
                        cursor: 'pointer',
                        fontSize: '14px',
                        fontWeight: '500',
                        transition: 'background 0.2s'
                      }}
                      onMouseEnter={(e) => e.currentTarget.style.background = '#004a8a'}
                      onMouseLeave={(e) => e.currentTarget.style.background = '#005CA9'}
                    >
                      View Details →
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Summary Stats */}
      {!isLoading && patients.length > 0 && (
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
          gap: '15px', 
          marginTop: '20px' 
        }}>
          <div style={{ 
            background: 'white', 
            padding: '20px', 
            borderRadius: '8px',
            boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
            textAlign: 'center'
          }}>
            <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#005CA9' }}>
              {patients.length}
            </div>
            <div style={{ fontSize: '14px', color: '#666', marginTop: '5px' }}>
              Total Patients
            </div>
          </div>
          <div style={{ 
            background: 'white', 
            padding: '20px', 
            borderRadius: '8px',
            boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
            textAlign: 'center'
          }}>
            <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#dc3545' }}>
              {patients.filter(p => p.needs_review).length}
            </div>
            <div style={{ fontSize: '14px', color: '#666', marginTop: '5px' }}>
              Need Review
            </div>
          </div>
          <div style={{ 
            background: 'white', 
            padding: '20px', 
            borderRadius: '8px',
            boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
            textAlign: 'center'
          }}>
            <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#28a745' }}>
              {patients.reduce((sum, p) => sum + p.pending_reviews, 0)}
            </div>
            <div style={{ fontSize: '14px', color: '#666', marginTop: '5px' }}>
              Total Pending Reviews
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PatientListPanel;
