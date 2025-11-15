import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = 'http://127.0.0.1:8000';

interface ImageData {
  id: number;
  filename: string;
  view_position: string | null;
  created_at: string;
  reviewed_at: string | null;
  ml_predictions: Array<{
    pathology: string;
    probability: number;
  }>;
  doctor_labels: Array<{
    pathology: string;
    is_present: boolean;
    comment: string | null;
  }>;
}

interface ExamData {
  id: number;
  exam_datetime: string;
  reason: string | null;
  images: ImageData[];
}

interface PatientDetail {
  id: number;
  first_name: string;
  last_name: string;
  age: number | null;
  sex: string | null;
  exams: ExamData[];
}

interface PatientDetailPanelProps {
  patientId: number;
  onBack: () => void;
}

const PatientDetailPanel: React.FC<PatientDetailPanelProps> = ({ patientId, onBack }) => {
  const [patient, setPatient] = useState<PatientDetail | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedImage, setExpandedImage] = useState<number | null>(null);

  useEffect(() => {
    loadPatientDetails();
  }, [patientId]);

  const loadPatientDetails = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await axios.get(`${API_URL}/patients/${patientId}`);
      setPatient(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load patient details');
      console.error('Error loading patient details:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatProbability = (prob: number) => {
    return `${(prob * 100).toFixed(1)}%`;
  };

  if (isLoading) {
    return (
      <div style={{ textAlign: 'center', padding: '60px', color: '#666' }}>
        <div style={{ fontSize: '40px', marginBottom: '10px' }}>⏳</div>
        Loading patient details...
      </div>
    );
  }

  if (error || !patient) {
    return (
      <div style={{ padding: '20px' }}>
        <button
          onClick={onBack}
          style={{
            padding: '10px 20px',
            background: '#005CA9',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            cursor: 'pointer',
            marginBottom: '20px'
          }}
        >
          ← Back to Patient List
        </button>
        <div style={{ 
          padding: '20px', 
          background: '#f8d7da', 
          color: '#721c24',
          borderRadius: '6px'
        }}>
          ❌ {error || 'Patient not found'}
        </div>
      </div>
    );
  }

  return (
    <div style={{ fontFamily: 'sans-serif', maxWidth: '1200px', margin: '0 auto', padding: '20px' }}>
      {/* Back Button */}
      <button
        onClick={onBack}
        style={{
          padding: '10px 20px',
          background: '#6c757d',
          color: 'white',
          border: 'none',
          borderRadius: '6px',
          cursor: 'pointer',
          marginBottom: '20px',
          fontSize: '14px',
          fontWeight: '500',
          transition: 'background 0.2s'
        }}
        onMouseEnter={(e) => e.currentTarget.style.background = '#5a6268'}
        onMouseLeave={(e) => e.currentTarget.style.background = '#6c757d'}
      >
        ← Back to Patient List
      </button>

      {/* Patient Header */}
      <div style={{ 
        background: 'linear-gradient(135deg, #005CA9 0%, #0077CC 100%)', 
        color: 'white', 
        padding: '25px', 
        borderRadius: '8px',
        marginBottom: '20px'
      }}>
        <h1 style={{ margin: '0 0 15px 0', fontSize: '28px' }}>
          👤 {patient.first_name} {patient.last_name}
        </h1>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '15px', fontSize: '14px', opacity: 0.95 }}>
          <div><strong>Patient ID:</strong> {patient.id}</div>
          <div><strong>Age:</strong> {patient.age || 'N/A'}</div>
          <div><strong>Sex:</strong> {patient.sex || 'N/A'}</div>
          <div><strong>Total Exams:</strong> {patient.exams.length}</div>
        </div>
      </div>

      {/* Exams List */}
      {patient.exams.length === 0 ? (
        <div style={{ 
          textAlign: 'center', 
          padding: '60px', 
          background: '#f8f9fa',
          borderRadius: '8px',
          color: '#666'
        }}>
          <div style={{ fontSize: '48px', marginBottom: '15px' }}>📋</div>
          <h3 style={{ margin: '0 0 10px 0' }}>No Exams Found</h3>
          <p>No examination records available for this patient.</p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          {patient.exams.map((exam) => (
            <div 
              key={exam.id}
              style={{ 
                background: 'white', 
                borderRadius: '8px', 
                overflow: 'hidden',
                boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
              }}
            >
              {/* Exam Header */}
              <div style={{ 
                background: '#e6f2ff', 
                padding: '15px', 
                borderBottom: '2px solid #005CA9'
              }}>
                <h3 style={{ margin: '0 0 10px 0', color: '#005CA9' }}>
                  📅 Exam #{exam.id} - {formatDate(exam.exam_datetime)}
                </h3>
                {exam.reason && (
                  <div style={{ fontSize: '14px', color: '#666' }}>
                    <strong>Reason:</strong> {exam.reason}
                  </div>
                )}
              </div>

              {/* Images */}
              <div style={{ padding: '20px' }}>
                {exam.images.length === 0 ? (
                  <div style={{ textAlign: 'center', padding: '20px', color: '#666' }}>
                    No images available for this exam.
                  </div>
                ) : (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
                    {exam.images.map((image) => (
                      <div 
                        key={image.id}
                        style={{ 
                          border: '1px solid #dee2e6',
                          borderRadius: '6px',
                          overflow: 'hidden'
                        }}
                      >
                        {/* Image Header */}
                        <div 
                          style={{ 
                            background: '#f8f9fa',
                            padding: '12px',
                            cursor: 'pointer',
                            display: 'flex',
                            justifyContent: 'space-between',
                            alignItems: 'center',
                            transition: 'background 0.2s'
                          }}
                          onClick={() => setExpandedImage(expandedImage === image.id ? null : image.id)}
                          onMouseEnter={(e) => e.currentTarget.style.background = '#e9ecef'}
                          onMouseLeave={(e) => e.currentTarget.style.background = '#f8f9fa'}
                        >
                          <div>
                            <strong>🖼️ {image.filename}</strong>
                            {image.view_position && (
                              <span style={{ marginLeft: '10px', color: '#666', fontSize: '13px' }}>
                                ({image.view_position})
                              </span>
                            )}
                            {image.reviewed_at ? (
                              <span style={{ 
                                marginLeft: '10px',
                                padding: '2px 8px',
                                background: '#d4edda',
                                color: '#155724',
                                borderRadius: '10px',
                                fontSize: '12px'
                              }}>
                                ✓ Reviewed
                              </span>
                            ) : (
                              <span style={{ 
                                marginLeft: '10px',
                                padding: '2px 8px',
                                background: '#fff3cd',
                                color: '#856404',
                                borderRadius: '10px',
                                fontSize: '12px'
                              }}>
                                ⚠️ Pending Review
                              </span>
                            )}
                          </div>
                          <span style={{ fontSize: '18px' }}>
                            {expandedImage === image.id ? '🔽' : '▶️'}
                          </span>
                        </div>

                        {/* Expanded Image Details */}
                        {expandedImage === image.id && (
                          <div style={{ padding: '15px', background: 'white' }}>
                            {/* ML Predictions */}
                            {image.ml_predictions.length > 0 && (
                              <div style={{ marginBottom: '15px' }}>
                                <h4 style={{ margin: '0 0 10px 0', color: '#005CA9', fontSize: '15px' }}>
                                  🤖 AI Predictions
                                </h4>
                                <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                                  <thead>
                                    <tr style={{ background: '#f8f9fa', borderBottom: '2px solid #dee2e6' }}>
                                      <th style={{ padding: '8px', textAlign: 'left', fontSize: '13px' }}>Pathology</th>
                                      <th style={{ padding: '8px', textAlign: 'left', fontSize: '13px' }}>Probability</th>
                                    </tr>
                                  </thead>
                                  <tbody>
                                    {image.ml_predictions.map((pred, idx) => (
                                      <tr key={idx} style={{ borderBottom: '1px solid #dee2e6' }}>
                                        <td style={{ padding: '8px', fontSize: '14px' }}>{pred.pathology}</td>
                                        <td style={{ padding: '8px', fontSize: '14px' }}>
                                          <span style={{ 
                                            fontWeight: pred.probability > 0.5 ? 'bold' : 'normal',
                                            color: pred.probability > 0.5 ? '#dc3545' : '#333'
                                          }}>
                                            {formatProbability(pred.probability)}
                                          </span>
                                        </td>
                                      </tr>
                                    ))}
                                  </tbody>
                                </table>
                              </div>
                            )}

                            {/* Doctor Labels */}
                            {image.doctor_labels.length > 0 && (
                              <div>
                                <h4 style={{ margin: '0 0 10px 0', color: '#28a745', fontSize: '15px' }}>
                                  👨‍⚕️ Doctor Review
                                </h4>
                                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                                  {image.doctor_labels.map((label, idx) => (
                                    <div 
                                      key={idx}
                                      style={{ 
                                        padding: '10px',
                                        background: label.is_present ? '#d4edda' : '#f8d7da',
                                        border: `1px solid ${label.is_present ? '#c3e6cb' : '#f5c6cb'}`,
                                        borderRadius: '4px',
                                        fontSize: '14px'
                                      }}
                                    >
                                      <div>
                                        <strong>{label.pathology}:</strong> {label.is_present ? '✓ Present' : '✗ Not Present'}
                                      </div>
                                      {label.comment && (
                                        <div style={{ marginTop: '5px', fontSize: '13px', fontStyle: 'italic' }}>
                                          Comment: {label.comment}
                                        </div>
                                      )}
                                    </div>
                                  ))}
                                </div>
                              </div>
                            )}

                            {image.ml_predictions.length === 0 && image.doctor_labels.length === 0 && (
                              <div style={{ textAlign: 'center', padding: '20px', color: '#666', fontSize: '14px' }}>
                                No predictions or labels available yet.
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default PatientDetailPanel;
