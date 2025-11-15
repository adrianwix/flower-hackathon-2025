import React, { useState } from 'react';

const HomePage: React.FC<{ onNavigate?: (view: string) => void }> = ({ onNavigate }) => {
  const [expandedFaq, setExpandedFaq] = useState<number | null>(null);

  const faqs = [
    {
      question: "Why a \"Federated Second Opinion\"? Isn't one \"Global Model\" simpler and better?",
      answer: "No. A single \"Global Model\" is fundamentally flawed because it suffers from the \"tyranny of the average.\" It averages away (deletes) rare, specialist knowledge from hospitals with unique data (like our Hospital C). Our FSO approach protects this specialist knowledge and presents it as a \"virtual consensus panel,\" which is safer, more robust, and more accurate for the \"hard cases\" where doctors actually need help."
    },
    {
      question: "How do you really protect my hospital's Intellectual Property (IP)? You are sharing models.",
      answer: "This is our core innovation. We never share your private, high-performance \"Teacher Model.\" That model, which represents your core IP, never leaves your firewall. Instead, we use Federated Knowledge Distillation. Your \"Teacher\" trains a new, lightweight, IP-safe \"Student Model.\" Only this \"Student\"—which has learned the knowledge but is not the IP—is contributed to the network library."
    },
    {
      question: "What data leaves my hospital? Is your \"Mycelium Broker\" (cloud server) a privacy risk or a central point of failure?",
      answer: "Absolutely zero patient data ever leaves your firewall. The diagnosis (inference) is 100% on-premise. The Mycelium Broker is only used for the offline \"sync\" of the \"Student Model Library.\" It's an \"App Store\" for models, not a router for data. It has zero involvement in the live diagnosis. Therefore, if the Broker is down, diagnoses continue to work perfectly with zero latency; the node just can't get new model updates until the Broker is back."
    },
    {
      question: "How does the system \"find\" the right specialist model so quickly? Is it sending a query?",
      answer: "It doesn't need to \"find\" it—it already has it. The FSO analysis is 100% on-premise. Your \"Mycelium Node\" (the backend) runs the patient's feature vector against the entire local \"Student Library\" (e.g., all 3, or all 30 models) simultaneously. This is computationally trivial and instant (zero-latency). The \"magic\" of our UI is that it highlights when one of those local specialist models (like \"Student_C\") produces a strong, dissenting opinion."
    },
    {
      question: "What stops a hospital from \"leeching\"—just downloading the \"Student Library\" but never contributing their own?",
      answer: "The Mycelium Broker (cloud server) enforces the network's \"quid pro quo\" (give-one, get-one) policy. To download the latest version of the \"Student Model Library\" during a sync, your node must first contribute its own trained \"Student Model\" from the last training cycle. This is an automated, fair, and sustainable business logic that ensures every member adds value."
    }
  ];
  return (
    <div style={{ fontFamily: 'sans-serif' }}>
      {/* Hero Section */}
      <div style={{ 
        position: 'relative',
        minHeight: '95vh',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        overflow: 'hidden',
        color: 'white',
        padding: 'clamp(60px, 10vw, 100px) clamp(15px, 3vw, 20px)',
        textAlign: 'center'
      }}>
        {/* Video Background */}
        <video 
          autoPlay 
          loop 
          muted 
          playsInline
          style={{ 
            position: 'absolute',
            top: '50%',
            left: '50%',
            minWidth: '100%',
            minHeight: '100%',
            width: 'auto',
            height: 'auto',
            transform: 'translate(-50%, -50%)',
            zIndex: 0,
            objectFit: 'cover'
          }}
        >
          <source src="/videoherosection.mp4" type="video/mp4" />
        </video>
        
        {/* Content */}
        <div style={{ position: 'relative', zIndex: 2, maxWidth: '1000px' }}>
          <h1 style={{ fontSize: 'clamp(40px, 7vw, 56px)', margin: '0 0 20px 0', fontWeight: '700', textShadow: '3px 3px 6px rgba(0,0,0,0.8)' }}>
            Mycelium AI
          </h1>
          <p style={{ fontSize: 'clamp(20px, 3.5vw, 28px)', margin: '0 0 30px 0', textShadow: '2px 2px 4px rgba(0,0,0,0.8)' }}>
            Federated Specialist Orchestration for Medical Imaging
          </p>
          
          <p style={{ fontSize: 'clamp(16px, 2.8vw, 20px)', margin: '0 auto 40px', lineHeight: '1.6', padding: '0 10px', textShadow: '2px 2px 4px rgba(0,0,0,0.8)' }}>
            Harness the power of distributed AI models to deliver accurate, privacy-preserving medical diagnoses. 
            Mycelium AI brings together local and specialist models in real-time, ensuring zero data leakage and maximum accuracy.
          </p>
          
          <div style={{ display: 'flex', gap: '15px', justifyContent: 'center', flexWrap: 'wrap' }}>
            <button onClick={() => onNavigate?.('clinician')} style={{ 
              padding: 'clamp(12px, 2vw, 15px) clamp(25px, 4vw, 30px)', 
              background: 'white', 
              color: '#005CA9', 
              border: 'none',
              borderRadius: '8px',
              fontWeight: '600',
              fontSize: 'clamp(14px, 2vw, 16px)',
              boxShadow: '0 4px 6px rgba(0,0,0,0.2)',
              minWidth: '120px',
              cursor: 'pointer'
            }}>
              Try Clinician Demo
            </button>
            <button onClick={() => onNavigate?.('admin')} style={{ 
              padding: 'clamp(12px, 2vw, 15px) clamp(25px, 4vw, 30px)', 
              background: 'transparent', 
              color: 'white', 
              border: '2px solid white',
              borderRadius: '8px',
              fontWeight: '600',
              fontSize: 'clamp(14px, 2vw, 16px)',
              minWidth: '120px',
              cursor: 'pointer'
            }}>
              Admin Dashboard
            </button>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div id="features" style={{ padding: 'clamp(40px, 6vw, 60px) clamp(15px, 3vw, 20px)', background: '#f8f9fa' }}>
        <h2 style={{ textAlign: 'center', fontSize: 'clamp(28px, 5vw, 36px)', marginBottom: 'clamp(30px, 5vw, 50px)', color: '#005CA9' }}>
          Why Mycelium AI?
        </h2>
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
          gap: 'clamp(20px, 3vw, 30px)',
          maxWidth: '1200px',
          margin: '0 auto'
        }}>
          <div style={{ 
            background: 'white', 
            padding: 'clamp(20px, 3vw, 30px)', 
            borderRadius: '12px',
            boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
          }}>
            <div style={{ fontSize: 'clamp(36px, 6vw, 48px)', marginBottom: '15px' }}>🔒</div>
            <h3 style={{ color: '#005CA9', marginBottom: '15px', fontSize: 'clamp(18px, 2.5vw, 20px)' }}>Privacy First</h3>
            <p style={{ color: '#666', lineHeight: '1.6' }}>
              All analysis happens on-premise. Patient data never leaves your facility. 
              Zero-leak architecture ensures GDPR, EU AI Act, and HIPAA compliance with complete data sovereignty.
            </p>
          </div>

          <div style={{ 
            background: 'white', 
            padding: '30px', 
            borderRadius: '12px',
            boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
          }}>
            <div style={{ fontSize: '48px', marginBottom: '15px' }}>⚡</div>
            <h3 style={{ color: '#005CA9', marginBottom: '15px' }}>Real-Time FSO</h3>
            <p style={{ color: '#666', lineHeight: '1.6' }}>
              Federated Specialist Orchestration runs instantly. Multiple AI models analyze 
              cases simultaneously, providing consensus or flagging for expert review in milliseconds.
            </p>
          </div>

          <div style={{ 
            background: 'white', 
            padding: '30px', 
            borderRadius: '12px',
            boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
          }}>
            <div style={{ fontSize: '48px', marginBottom: '15px' }}>🎯</div>
            <h3 style={{ color: '#005CA9', marginBottom: '15px' }}>Specialist Detection</h3>
            <p style={{ color: '#666', lineHeight: '1.6' }}>
              Access to peer specialist models trained on rare pathologies. Catch what 
              generalist models miss, without compromising on privacy or speed.
            </p>
          </div>

          <div style={{ 
            background: 'white', 
            padding: '30px', 
            borderRadius: '12px',
            boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
          }}>
            <div style={{ fontSize: '48px', marginBottom: '15px' }}>🌐</div>
            <h3 style={{ color: '#005CA9', marginBottom: '15px' }}>Federated Learning</h3>
            <p style={{ color: '#666', lineHeight: '1.6' }}>
              Benefit from global knowledge without sharing data. Models learn collaboratively 
              through FSO, improving accuracy for everyone while maintaining full privacy.
            </p>
          </div>

          <div style={{ 
            background: 'white', 
            padding: '30px', 
            borderRadius: '12px',
            boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
          }}>
            <div style={{ fontSize: '48px', marginBottom: '15px' }}>📊</div>
            <h3 style={{ color: '#005CA9', marginBottom: '15px' }}>Transparent AI</h3>
            <p style={{ color: '#666', lineHeight: '1.6' }}>
              See exactly which models contributed to each diagnosis. Full audit trail, 
              model metadata, and confidence scores for every prediction.
            </p>
          </div>

          <div style={{ 
            background: 'white', 
            padding: '30px', 
            borderRadius: '12px',
            boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
          }}>
            <div style={{ fontSize: '48px', marginBottom: '15px' }}>🏥</div>
            <h3 style={{ color: '#005CA9', marginBottom: '15px' }}>Clinical Integration</h3>
            <p style={{ color: '#666', lineHeight: '1.6' }}>
              Seamlessly integrates with existing radiology workflows. DICOM compatible, 
              PACS integration, and designed for busy clinical environments.
            </p>
          </div>
        </div>
      </div>

      {/* How It Works */}
      <div style={{ padding: 'clamp(40px, 6vw, 60px) clamp(15px, 3vw, 20px)', background: 'white' }}>
        <h2 style={{ textAlign: 'center', fontSize: 'clamp(28px, 5vw, 36px)', marginBottom: 'clamp(30px, 5vw, 50px)', color: '#005CA9' }}>
          How It Works
        </h2>
        <div style={{ maxWidth: '900px', margin: '0 auto' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '30px', marginBottom: '40px', flexWrap: 'wrap' }}>
            <div style={{ 
              background: '#005CA9', 
              color: 'white', 
              width: '60px', 
              height: '60px', 
              borderRadius: '50%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '24px',
              fontWeight: 'bold',
              flexShrink: 0
            }}>1</div>
            <div style={{ flex: 1 }}>
              <h3 style={{ color: '#005CA9', marginBottom: '10px' }}>Upload X-Ray</h3>
              <p style={{ color: '#666', lineHeight: '1.6' }}>
                Radiologist uploads patient X-ray through secure interface. Image features 
                are extracted locally without transmitting raw data.
              </p>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '30px', marginBottom: '40px', flexWrap: 'wrap' }}>
            <div style={{ 
              background: '#005CA9', 
              color: 'white', 
              width: '60px', 
              height: '60px', 
              borderRadius: '50%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '24px',
              fontWeight: 'bold',
              flexShrink: 0
            }}>2</div>
            <div style={{ flex: 1 }}>
              <h3 style={{ color: '#005CA9', marginBottom: '10px' }}>FSO Analysis</h3>
              <p style={{ color: '#666', lineHeight: '1.6' }}>
                Multiple student models (local, global, specialist) analyze the case simultaneously. 
                All processing happens on your Mycelium node - zero latency, zero leakage.
              </p>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '30px', marginBottom: '40px', flexWrap: 'wrap' }}>
            <div style={{ 
              background: '#005CA9', 
              color: 'white', 
              width: '60px', 
              height: '60px', 
              borderRadius: '50%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '24px',
              fontWeight: 'bold',
              flexShrink: 0
            }}>3</div>
            <div style={{ flex: 1 }}>
              <h3 style={{ color: '#005CA9', marginBottom: '10px' }}>Consensus or Alert</h3>
              <p style={{ color: '#666', lineHeight: '1.6' }}>
                If models agree, you get a green "Consensus Found" result. If specialist model 
                detects a rare finding, you get a red "Expert Review Flagged" alert.
              </p>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '30px', flexWrap: 'wrap' }}>
            <div style={{ 
              background: '#005CA9', 
              color: 'white', 
              width: '60px', 
              height: '60px', 
              borderRadius: '50%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '24px',
              fontWeight: 'bold',
              flexShrink: 0
            }}>4</div>
            <div style={{ flex: 1 }}>
              <h3 style={{ color: '#005CA9', marginBottom: '10px' }}>Clinical Decision</h3>
              <p style={{ color: '#666', lineHeight: '1.6' }}>
                Radiologist reviews the detailed breakdown, model metadata, and confidence scores. 
                Feedback loop ensures continuous improvement.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Stats Section */}
      <div style={{ padding: 'clamp(40px, 6vw, 60px) clamp(15px, 3vw, 20px)', background: 'linear-gradient(135deg, #005CA9 0%, #0077CC 100%)', color: 'white' }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
          <h2 style={{ textAlign: 'center', fontSize: 'clamp(28px, 5vw, 36px)', marginBottom: 'clamp(30px, 5vw, 50px)' }}>
            Trusted by Medical Professionals
          </h2>
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
            gap: 'clamp(20px, 4vw, 40px)',
            textAlign: 'center'
          }}>
            <div>
              <div style={{ fontSize: 'clamp(32px, 6vw, 48px)', fontWeight: 'bold', marginBottom: '10px' }}>100%</div>
              <div style={{ fontSize: 'clamp(14px, 2vw, 18px)', opacity: 0.9 }}>On-Premise Processing</div>
            </div>
            <div>
              <div style={{ fontSize: 'clamp(32px, 6vw, 48px)', fontWeight: 'bold', marginBottom: '10px' }}>&lt;100ms</div>
              <div style={{ fontSize: 'clamp(14px, 2vw, 18px)', opacity: 0.9 }}>Analysis Latency</div>
            </div>
            <div>
              <div style={{ fontSize: 'clamp(32px, 6vw, 48px)', fontWeight: 'bold', marginBottom: '10px' }}>3+</div>
              <div style={{ fontSize: 'clamp(14px, 2vw, 18px)', opacity: 0.9 }}>Specialist Models</div>
            </div>
            <div>
              <div style={{ fontSize: 'clamp(32px, 6vw, 48px)', fontWeight: 'bold', marginBottom: '10px' }}>EU AI Act</div>
              <div style={{ fontSize: 'clamp(14px, 2vw, 18px)', opacity: 0.9 }}>Compliant</div>
            </div>
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div id="demo" style={{ padding: 'clamp(40px, 6vw, 60px) clamp(15px, 3vw, 20px)', background: '#f8f9fa', textAlign: 'center' }}>
        <h2 style={{ fontSize: 'clamp(28px, 5vw, 36px)', marginBottom: '20px', color: '#005CA9' }}>
          Ready to Experience Mycelium AI?
        </h2>
        <p style={{ fontSize: 'clamp(16px, 2.5vw, 18px)', color: '#666', marginBottom: '40px', maxWidth: '700px', margin: '0 auto 40px', padding: '0 10px' }}>
          Explore our interactive demo to see how Federated Specialist Orchestration 
          revolutionizes medical imaging analysis.
        </p>
        <div style={{ display: 'flex', gap: '15px', justifyContent: 'center', flexWrap: 'wrap' }}>
          <button 
            onClick={() => onNavigate?.('clinician')}
            style={{ 
              padding: '15px 40px', 
              background: '#005CA9', 
              color: 'white', 
              border: 'none',
              borderRadius: '8px',
              fontWeight: '600',
              fontSize: '16px',
              cursor: 'pointer',
              boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
            }}
          >
            Try Clinician Demo
          </button>
          <button 
            onClick={() => onNavigate?.('admin')}
            style={{ 
              padding: '15px 40px', 
              background: 'white', 
              color: '#005CA9', 
              border: '2px solid #005CA9',
              borderRadius: '8px',
              fontWeight: '600',
              fontSize: '16px',
              cursor: 'pointer'
            }}
          >
            View Admin Dashboard
          </button>
        </div>
      </div>

      {/* FAQ Section */}
      <div style={{ padding: 'clamp(40px, 6vw, 60px) clamp(15px, 3vw, 20px)', background: 'white' }}>
        <h2 style={{ textAlign: 'center', fontSize: 'clamp(28px, 5vw, 36px)', marginBottom: 'clamp(30px, 5vw, 50px)', color: '#005CA9' }}>
          Frequently Asked Questions
        </h2>
        <div style={{ maxWidth: '900px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '15px' }}>
          {faqs.map((faq, index) => (
            <div 
              key={index}
              style={{ 
                border: '1px solid #dee2e6',
                borderRadius: '8px',
                overflow: 'hidden',
                background: expandedFaq === index ? '#f8f9fa' : 'white',
                transition: 'all 0.3s ease'
              }}
            >
              <div 
                onClick={() => setExpandedFaq(expandedFaq === index ? null : index)}
                style={{ 
                  padding: 'clamp(15px, 3vw, 20px)',
                  cursor: 'pointer',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  gap: '15px',
                  transition: 'background 0.2s'
                }}
                onMouseEnter={(e) => {
                  if (expandedFaq !== index) {
                    e.currentTarget.style.background = '#f8f9fa';
                  }
                }}
                onMouseLeave={(e) => {
                  if (expandedFaq !== index) {
                    e.currentTarget.style.background = 'white';
                  }
                }}
              >
                <h3 style={{ 
                  margin: 0, 
                  fontSize: 'clamp(16px, 2.5vw, 18px)', 
                  fontWeight: '600',
                  color: '#005CA9',
                  flex: 1
                }}>
                  {faq.question}
                </h3>
                <div style={{ 
                  fontSize: '24px',
                  color: '#005CA9',
                  transition: 'transform 0.3s ease',
                  transform: expandedFaq === index ? 'rotate(180deg)' : 'rotate(0deg)',
                  flexShrink: 0
                }}>
                  ▼
                </div>
              </div>
              {expandedFaq === index && (
                <div style={{ 
                  padding: '0 clamp(15px, 3vw, 20px) clamp(15px, 3vw, 20px)',
                  animation: 'fadeIn 0.3s ease'
                }}>
                  <p style={{ 
                    margin: 0,
                    fontSize: 'clamp(14px, 2vw, 16px)',
                    color: '#333',
                    lineHeight: '1.8'
                  }}>
                    {faq.answer}
                  </p>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default HomePage;