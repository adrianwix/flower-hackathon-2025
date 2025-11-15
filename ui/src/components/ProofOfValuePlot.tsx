import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell, Legend } from 'recharts';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface AccuracyResult {
  name: string;
  approach: string;
  accuracy: number;
  color: string;
  description: string;
}

interface ComparisonData {
  test_dataset: string;
  methodology: string;
  results: AccuracyResult[];
  key_insight: string;
}

const ProofOfValuePlot: React.FC = () => {
  const [data, setData] = useState<AccuracyResult[]>([
    { name: 'Competitor Global', accuracy: 68, approach: '', color: '#FF8080', description: '' },
    { name: 'Local-Only', accuracy: 75, approach: '', color: '#8884d8', description: '' },
    { name: 'Mycelium FSO', accuracy: 91, approach: '', color: '#005CA9', description: '' }
  ]);
  const [metadata, setMetadata] = useState<{ dataset: string; methodology: string; insight: string } | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchAccuracyData = async () => {
      try {
        const response = await axios.get<ComparisonData>(`${API_URL}/api/accuracy-comparison`);
        setData(response.data.results);
        setMetadata({
          dataset: response.data.test_dataset,
          methodology: response.data.methodology,
          insight: response.data.key_insight
        });
      } catch (error) {
        console.error('Error fetching accuracy comparison:', error);
        // Keep fallback data
      } finally {
        setIsLoading(false);
      }
    };

    fetchAccuracyData();
  }, []);

  if (isLoading) {
    return (
      <div style={{ textAlign: 'center', padding: '40px', color: '#666' }}>
        Loading accuracy comparison data...
      </div>
    );
  }

  return (
    <div>
      {metadata && (
        <div style={{
          marginBottom: '15px',
          padding: '12px',
          background: '#e6f2ff',
          borderRadius: '6px',
          fontSize: '12px',
          color: '#005CA9'
        }}>
          <strong>Test Dataset:</strong> {metadata.dataset}
          <br />
          <strong>Methodology:</strong> {metadata.methodology}
        </div>
      )}

      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data}>
          <XAxis
            dataKey="name"
            tick={{ fontSize: 12 }}
            interval={0}
            angle={-15}
            textAnchor="end"
            height={80}
          />
          <YAxis
            label={{ value: 'Accuracy (%)', angle: -90, position: 'insideLeft' }}
            domain={[0, 100]}
          />
          <Tooltip
            content={({ active, payload }) => {
              if (active && payload && payload.length) {
                const data = payload[0].payload as AccuracyResult;
                return (
                  <div style={{
                    background: 'white',
                    padding: '12px',
                    border: '2px solid #005CA9',
                    borderRadius: '6px',
                    boxShadow: '0 4px 8px rgba(0,0,0,0.1)'
                  }}>
                    <strong style={{ color: '#005CA9' }}>{data.name}</strong>
                    <br />
                    <span style={{ fontSize: '11px', color: '#666' }}>{data.approach}</span>
                    <br />
                    <strong style={{ fontSize: '18px', color: data.color }}>
                      {data.accuracy}% Accuracy
                    </strong>
                    <br />
                    <span style={{ fontSize: '11px', fontStyle: 'italic' }}>{data.description}</span>
                  </div>
                );
              }
              return null;
            }}
          />
          <Bar dataKey="accuracy" radius={[8, 8, 0, 0]}>
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>

      {metadata && (
        <div style={{
          marginTop: '15px',
          padding: '12px',
          background: '#d4edda',
          borderRadius: '6px',
          fontSize: '13px',
          color: '#155724',
          fontWeight: '600',
          textAlign: 'center'
        }}>
          💡 {metadata.insight}
        </div>
      )}
    </div>
  );
};

export default ProofOfValuePlot;