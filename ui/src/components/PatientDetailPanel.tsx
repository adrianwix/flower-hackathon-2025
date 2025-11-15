import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface MLPrediction {
  binary_prediction: {
    pathology: string;
    probability: number;
    predicted_label: boolean;
  } | null;
  multi_label_predictions: {
    [key: string]: {
      probability: number;
      predicted_label: boolean;
    };
  };
}

interface DoctorLabels {
  [key: string]: {
    is_present: boolean;
    comment: string | null;
    labeled_at: string;
  };
}

interface ImageData {
  id: number;
  filename: string;
  view_position: string | null;
  reviewed_at: string | null;
  is_pending: boolean;
  ml_predictions: MLPrediction;
  doctor_labels: DoctorLabels;
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
  const [editingImage, setEditingImage] = useState<number | null>(null);
  const [editingLabels, setEditingLabels] = useState<{ [key: string]: boolean }>({});
  const [editingComment, setEditingComment] = useState<string>('');
  const [isSaving, setIsSaving] = useState(false);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [uploadReason, setUploadReason] = useState('');
  const [uploadViewPosition, setUploadViewPosition] = useState('');
  const [isUploading, setIsUploading] = useState(false);

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

  const handleQuickConfirm = async (imageId: number, mlPredictions: MLPrediction) => {
    setIsSaving(true);
    try {
      const labels: { [key: string]: boolean } = {};

      // Convert ML predictions to doctor labels
      Object.entries(mlPredictions.multi_label_predictions).forEach(([pathology, pred]) => {
        labels[pathology] = pred.predicted_label;
      });

      await axios.put(`${API_URL}/patients/images/${imageId}/labels`, {
        labels,
        comment: 'Confirmed by doctor'
      });

      // Reload patient data
      await loadPatientDetails();
      alert('✅ Labels confirmed successfully!');
    } catch (err: any) {
      console.error('Error confirming labels:', err);
      alert('❌ Failed to confirm labels: ' + (err.response?.data?.detail || err.message));
    } finally {
      setIsSaving(false);
    }
  };

  const handleStartEdit = (imageId: number, mlPredictions: MLPrediction, doctorLabels: DoctorLabels) => {
    setEditingImage(imageId);

    // Initialize with existing doctor labels if available, otherwise use ML predictions
    const labels: { [key: string]: boolean } = {};

    if (Object.keys(doctorLabels).length > 0) {
      // Use existing doctor labels
      Object.entries(doctorLabels).forEach(([pathology, label]) => {
        labels[pathology] = label.is_present;
      });
      // Get first comment if available
      const firstComment = Object.values(doctorLabels).find(l => l.comment)?.comment || '';
      setEditingComment(firstComment);
    } else {
      // Use ML predictions
      Object.entries(mlPredictions.multi_label_predictions).forEach(([pathology, pred]) => {
        labels[pathology] = pred.predicted_label;
      });
      setEditingComment('');
    }

    setEditingLabels(labels);
  };

  const handleCancelEdit = () => {
    setEditingImage(null);
    setEditingLabels({});
    setEditingComment('');
  };

  const handleSaveEdit = async (imageId: number) => {
    setIsSaving(true);
    try {
      await axios.put(`${API_URL}/patients/images/${imageId}/labels`, {
        labels: editingLabels,
        comment: editingComment || null
      });

      // Reset editing state
      setEditingImage(null);
      setEditingLabels({});
      setEditingComment('');

      // Reload patient data
      await loadPatientDetails();
      alert('✅ Labels saved successfully!');
    } catch (err: any) {
      console.error('Error saving labels:', err);
      alert('❌ Failed to save labels: ' + (err.response?.data?.detail || err.message));
    } finally {
      setIsSaving(false);
    }
  };

  const handleUploadExam = async () => {
    if (!uploadFile) {
      alert('Please select a file to upload');
      return;
    }

    setIsUploading(true);
    try {
      const formData = new FormData();
      formData.append('file', uploadFile);
      if (uploadReason) formData.append('reason', uploadReason);
      if (uploadViewPosition) formData.append('view_position', uploadViewPosition);

      await axios.post(`${API_URL}/patients/${patientId}/exams`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      // Reset modal state
      setShowUploadModal(false);
      setUploadFile(null);
      setUploadReason('');
      setUploadViewPosition('');

      // Reload patient data
      await loadPatientDetails();
      alert('✅ Exam uploaded and processed successfully!');
    } catch (err: any) {
      console.error('Error uploading exam:', err);
      alert('❌ Failed to upload exam: ' + (err.response?.data?.detail || err.message));
    } finally {
      setIsUploading(false);
    }
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
        marginBottom: '20px',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        <div>
          <h1 style={{ margin: '0 0 15px 0', fontSize: '28px' }}>
            👤 {patient.first_name && patient.last_name
              ? `${patient.first_name} ${patient.last_name}`
              : `Patient ${patient.id}`}
          </h1>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '15px', fontSize: '14px' }}>
            <div><strong>Patient ID:</strong> {patient.id}</div>
            <div><strong>Age:</strong> {patient.age || 'N/A'}</div>
            <div><strong>Sex:</strong> {patient.sex || 'N/A'}</div>
            <div><strong>Total Exams:</strong> {patient.exams.length}</div>
          </div>
        </div>
        <button
          onClick={() => setShowUploadModal(true)}
          style={{
            padding: '12px 24px',
            background: 'white',
            color: '#005CA9',
            border: 'none',
            borderRadius: '6px',
            cursor: 'pointer',
            fontSize: '16px',
            fontWeight: '600',
            transition: 'all 0.2s',
            boxShadow: '0 2px 8px rgba(0,0,0,0.2)'
          }}
          onMouseEnter={(e) => e.currentTarget.style.transform = 'scale(1.05)'}
          onMouseLeave={(e) => e.currentTarget.style.transform = 'scale(1)'}
        >
          ➕ Upload New Exam
        </button>
      </div>

      {/* Upload Modal */}
      {showUploadModal && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(0,0,0,0.5)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000
        }}>
          <div style={{
            background: 'white',
            borderRadius: '8px',
            padding: '30px',
            maxWidth: '500px',
            width: '90%',
            boxShadow: '0 4px 20px rgba(0,0,0,0.3)'
          }}>
            <h2 style={{ margin: '0 0 20px 0', color: '#005CA9' }}>📤 Upload New X-ray Exam</h2>

            <div style={{ marginBottom: '15px' }}>
              <label style={{ display: 'block', marginBottom: '5px', fontWeight: '500' }}>
                X-ray Image *
              </label>
              <input
                type="file"
                accept="image/png,image/jpeg"
                onChange={(e) => setUploadFile(e.target.files?.[0] || null)}
                style={{
                  width: '100%',
                  padding: '10px',
                  border: '1px solid #dee2e6',
                  borderRadius: '4px'
                }}
              />
            </div>

            <div style={{ marginBottom: '15px' }}>
              <label style={{ display: 'block', marginBottom: '5px', fontWeight: '500' }}>
                Reason for Exam
              </label>
              <input
                type="text"
                value={uploadReason}
                onChange={(e) => setUploadReason(e.target.value)}
                placeholder="e.g., Follow-up, Routine check"
                style={{
                  width: '100%',
                  padding: '10px',
                  border: '1px solid #dee2e6',
                  borderRadius: '4px'
                }}
              />
            </div>

            <div style={{ marginBottom: '20px' }}>
              <label style={{ display: 'block', marginBottom: '5px', fontWeight: '500' }}>
                View Position
              </label>
              <select
                value={uploadViewPosition}
                onChange={(e) => setUploadViewPosition(e.target.value)}
                style={{
                  width: '100%',
                  padding: '10px',
                  border: '1px solid #dee2e6',
                  borderRadius: '4px'
                }}
              >
                <option value="">Select position...</option>
                <option value="PA">PA (Posteroanterior)</option>
                <option value="AP">AP (Anteroposterior)</option>
                <option value="Lateral">Lateral</option>
                <option value="Other">Other</option>
              </select>
            </div>

            <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end' }}>
              <button
                onClick={() => {
                  setShowUploadModal(false);
                  setUploadFile(null);
                  setUploadReason('');
                  setUploadViewPosition('');
                }}
                disabled={isUploading}
                style={{
                  padding: '10px 20px',
                  background: '#6c757d',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  cursor: isUploading ? 'not-allowed' : 'pointer',
                  opacity: isUploading ? 0.5 : 1
                }}
              >
                Cancel
              </button>
              <button
                onClick={handleUploadExam}
                disabled={!uploadFile || isUploading}
                style={{
                  padding: '10px 20px',
                  background: '#005CA9',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  cursor: !uploadFile || isUploading ? 'not-allowed' : 'pointer',
                  opacity: !uploadFile || isUploading ? 0.5 : 1
                }}
              >
                {isUploading ? '⏳ Uploading...' : '📤 Upload & Process'}
              </button>
            </div>
          </div>
        </div>
      )}

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
          <p>Upload a new exam to get started.</p>
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
                background: '#005CA9',
                color: 'white',
                padding: '15px',
                borderBottom: '2px solid #004a8a'
              }}>
                <h3 style={{ margin: '0 0 10px 0' }}>
                  📅 Exam #{exam.id} - {formatDate(exam.exam_datetime)}
                </h3>
                {exam.reason && (
                  <div style={{ fontSize: '14px' }}>
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
                            transition: 'background 0.2s',
                            color: '#333'
                          }}
                          onClick={() => setExpandedImage(expandedImage === image.id ? null : image.id)}
                          onMouseEnter={(e) => e.currentTarget.style.background = '#e9ecef'}
                          onMouseLeave={(e) => e.currentTarget.style.background = '#f8f9fa'}
                        >
                          <div>
                            <strong style={{ color: '#333' }}>🖼️ {image.filename}</strong>
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
                            {/* X-ray Image Display */}
                            <div style={{ marginBottom: '20px', textAlign: 'center' }}>
                              <img
                                src={`${API_URL}/patients/images/${image.id}`}
                                alt={image.filename}
                                style={{
                                  maxWidth: '100%',
                                  maxHeight: '500px',
                                  borderRadius: '8px',
                                  boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
                                  border: '1px solid #dee2e6'
                                }}
                                onError={(e) => {
                                  const target = e.target as HTMLImageElement;
                                  target.style.display = 'none';
                                  const parent = target.parentElement;
                                  if (parent) {
                                    parent.innerHTML = '<div style="padding: 40px; background: #f8f9fa; color: #666; border-radius: 8px;">📷 Image could not be loaded</div>';
                                  }
                                }}
                              />
                            </div>

                            {/* ML Predictions */}
                            {Object.keys(image.ml_predictions.multi_label_predictions).length > 0 && (
                              <div style={{ marginBottom: '15px' }}>
                                <h4 style={{ margin: '0 0 10px 0', color: '#005CA9', fontSize: '15px' }}>
                                  🤖 AI Predictions (Top 3)
                                </h4>
                                <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                                  <thead>
                                    <tr style={{ background: '#f8f9fa', borderBottom: '2px solid #dee2e6' }}>
                                      <th style={{ padding: '8px', textAlign: 'left', fontSize: '13px', color: '#333' }}>Pathology</th>
                                      <th style={{ padding: '8px', textAlign: 'left', fontSize: '13px', color: '#333' }}>Probability</th>
                                      <th style={{ padding: '8px', textAlign: 'left', fontSize: '13px', color: '#333' }}>Prediction</th>
                                    </tr>
                                  </thead>
                                  <tbody>
                                    {Object.entries(image.ml_predictions.multi_label_predictions)
                                      .sort(([, a], [, b]) => b.probability - a.probability)
                                      .slice(0, 3)
                                      .map(([pathology, pred]) => (
                                        <tr key={pathology} style={{ borderBottom: '1px solid #dee2e6' }}>
                                          <td style={{ padding: '8px', fontSize: '14px', color: '#333' }}>{pathology}</td>
                                          <td style={{ padding: '8px', fontSize: '14px' }}>
                                            <span style={{
                                              fontWeight: pred.probability > 0.5 ? 'bold' : 'normal',
                                              color: pred.probability > 0.5 ? '#dc3545' : '#333'
                                            }}>
                                              {formatProbability(pred.probability)}
                                            </span>
                                          </td>
                                          <td style={{ padding: '8px', fontSize: '14px', color: '#333' }}>
                                            {pred.predicted_label ? '✓ Yes' : '✗ No'}
                                          </td>
                                        </tr>
                                      ))}
                                  </tbody>
                                </table>
                              </div>
                            )}

                            {/* Doctor Labels Section */}
                            <div style={{ marginBottom: '15px' }}>
                              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                                <h4 style={{ margin: 0, color: '#28a745', fontSize: '15px' }}>
                                  👨‍⚕️ Doctor Review
                                </h4>
                                {editingImage !== image.id && (
                                  <div style={{ display: 'flex', gap: '10px' }}>
                                    {image.is_pending && Object.keys(image.ml_predictions.multi_label_predictions).length > 0 && (
                                      <button
                                        onClick={() => handleQuickConfirm(image.id, image.ml_predictions)}
                                        disabled={isSaving}
                                        style={{
                                          padding: '6px 12px',
                                          background: '#28a745',
                                          color: 'white',
                                          border: 'none',
                                          borderRadius: '4px',
                                          cursor: isSaving ? 'not-allowed' : 'pointer',
                                          fontSize: '13px',
                                          fontWeight: '500'
                                        }}
                                      >
                                        ✓ Quick Confirm ML Labels
                                      </button>
                                    )}
                                    <button
                                      onClick={() => handleStartEdit(image.id, image.ml_predictions, image.doctor_labels)}
                                      disabled={isSaving}
                                      style={{
                                        padding: '6px 12px',
                                        background: '#007bff',
                                        color: 'white',
                                        border: 'none',
                                        borderRadius: '4px',
                                        cursor: isSaving ? 'not-allowed' : 'pointer',
                                        fontSize: '13px',
                                        fontWeight: '500'
                                      }}
                                    >
                                      ✏️ Edit Labels
                                    </button>
                                  </div>
                                )}
                              </div>

                              {editingImage === image.id ? (
                                // Edit Mode
                                <div style={{
                                  padding: '15px',
                                  background: '#f8f9fa',
                                  border: '2px solid #007bff',
                                  borderRadius: '6px'
                                }}>
                                  <h5 style={{ margin: '0 0 10px 0', fontSize: '14px', color: '#333' }}>Edit Pathology Labels</h5>
                                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginBottom: '15px' }}>
                                    {Object.keys(image.ml_predictions.multi_label_predictions).map((pathology) => (
                                      <label key={pathology} style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
                                        <input
                                          type="checkbox"
                                          checked={editingLabels[pathology] || false}
                                          onChange={(e) => setEditingLabels({
                                            ...editingLabels,
                                            [pathology]: e.target.checked
                                          })}
                                          style={{ width: '18px', height: '18px', cursor: 'pointer' }}
                                        />
                                        <span style={{ fontSize: '14px', color: '#333' }}>{pathology}</span>
                                        {image.ml_predictions.multi_label_predictions[pathology]?.predicted_label !== editingLabels[pathology] && (
                                          <span style={{ fontSize: '12px', color: '#856404', fontStyle: 'italic' }}>
                                            (Modified from AI)
                                          </span>
                                        )}
                                      </label>
                                    ))}
                                  </div>

                                  <div style={{ marginBottom: '15px' }}>
                                    <label style={{ display: 'block', marginBottom: '5px', fontSize: '14px', fontWeight: '500', color: '#333' }}>
                                      Comment (optional)
                                    </label>
                                    <textarea
                                      value={editingComment}
                                      onChange={(e) => setEditingComment(e.target.value)}
                                      placeholder="Add any comments or notes..."
                                      rows={3}
                                      style={{
                                        width: '100%',
                                        padding: '8px',
                                        border: '1px solid #dee2e6',
                                        borderRadius: '4px',
                                        fontSize: '14px',
                                        fontFamily: 'inherit'
                                      }}
                                    />
                                  </div>

                                  <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end' }}>
                                    <button
                                      onClick={handleCancelEdit}
                                      disabled={isSaving}
                                      style={{
                                        padding: '8px 16px',
                                        background: '#6c757d',
                                        color: 'white',
                                        border: 'none',
                                        borderRadius: '4px',
                                        cursor: isSaving ? 'not-allowed' : 'pointer',
                                        fontSize: '14px'
                                      }}
                                    >
                                      Cancel
                                    </button>
                                    <button
                                      onClick={() => handleSaveEdit(image.id)}
                                      disabled={isSaving}
                                      style={{
                                        padding: '8px 16px',
                                        background: '#28a745',
                                        color: 'white',
                                        border: 'none',
                                        borderRadius: '4px',
                                        cursor: isSaving ? 'not-allowed' : 'pointer',
                                        fontSize: '14px',
                                        fontWeight: '500'
                                      }}
                                    >
                                      {isSaving ? '⏳ Saving...' : '💾 Save Labels'}
                                    </button>
                                  </div>
                                </div>
                              ) : (
                                // View Mode
                                <div>
                                  {Object.keys(image.doctor_labels).length > 0 ? (
                                    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                                      {Object.entries(image.doctor_labels).map(([pathology, label]) => (
                                        <div
                                          key={pathology}
                                          style={{
                                            padding: '10px',
                                            background: label.is_present ? '#d4edda' : '#f8d7da',
                                            border: `1px solid ${label.is_present ? '#c3e6cb' : '#f5c6cb'}`,
                                            borderRadius: '4px',
                                            fontSize: '14px',
                                            color: '#333'
                                          }}
                                        >
                                          <div>
                                            <strong>{pathology}:</strong> {label.is_present ? '✓ Present' : '✗ Not Present'}
                                            {image.ml_predictions.multi_label_predictions[pathology] &&
                                              image.ml_predictions.multi_label_predictions[pathology].predicted_label !== label.is_present && (
                                                <span style={{ marginLeft: '8px', fontSize: '12px', fontStyle: 'italic', color: '#856404' }}>
                                                  (Override from AI: {image.ml_predictions.multi_label_predictions[pathology].predicted_label ? 'Yes' : 'No'})
                                                </span>
                                              )}
                                          </div>
                                          {label.comment && (
                                            <div style={{ marginTop: '5px', fontSize: '13px', fontStyle: 'italic', color: '#555' }}>
                                              Comment: {label.comment}
                                            </div>
                                          )}
                                        </div>
                                      ))}
                                    </div>
                                  ) : (
                                    <div style={{
                                      padding: '15px',
                                      background: '#fff3cd',
                                      border: '1px solid #ffc107',
                                      borderRadius: '4px',
                                      textAlign: 'center',
                                      color: '#856404',
                                      fontSize: '14px'
                                    }}>
                                      ⚠️ No doctor review yet. Click "Quick Confirm" to accept AI predictions or "Edit Labels" to customize.
                                    </div>
                                  )}
                                </div>
                              )}
                            </div>
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
