import React, { useState, useEffect } from 'react';
import { TopNavbar } from './components/common/TopNavbar';
import { Overview } from './pages/Overview';
import { Anomalies } from './pages/Anomalies';
import { Forecast } from './pages/Forecast';
import { CostAnalysis } from './pages/CostAnalysis';
import { Recommendations } from './pages/Recommendations';
import { api } from './services/api';

export function App() {
  const [activeTab, setActiveTab] = useState('overview');
  const [apiConnected, setApiConnected] = useState(true);
  const [selectedAnomalyIndex, setSelectedAnomalyIndex] = useState(null);
  const [activeMeta, setActiveMeta] = useState(null);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const fetchActiveMetadata = async () => {
    try {
      const meta = await api.getActiveDataset();
      setActiveMeta(meta);
      setApiConnected(true);
    } catch {
      setApiConnected(false);
    }
  };

  useEffect(() => {
    fetchActiveMetadata();
    const interval = setInterval(fetchActiveMetadata, 15000);
    return () => clearInterval(interval);
  }, []);

  const handleSelectAnomalyFromOverview = (index) => {
    setSelectedAnomalyIndex(index);
    setActiveTab('anomalies');
  };

  const handleDatasetChanged = () => {
    fetchActiveMetadata();
  };

  const handleRefresh = async () => {
    setIsRefreshing(true);
    await fetchActiveMetadata();
    setTimeout(() => setIsRefreshing(false), 600);
  };

  return (
    <div className="app-container">
      {/* Top Navigation Bar (Replaces left sidebar) */}
      <TopNavbar 
        activeTab={activeTab} 
        setActiveTab={setActiveTab} 
        apiConnected={apiConnected}
        activeMeta={activeMeta}
        onDatasetChanged={handleDatasetChanged}
        onRefresh={handleRefresh}
        isRefreshing={isRefreshing}
      />

      {/* Main Workspace Content */}
      <main style={{ flex: 1, minWidth: 0 }}>
        {activeTab === 'overview' && (
          <Overview 
            onNavigateToAnomalies={() => setActiveTab('anomalies')}
            onSelectAnomaly={handleSelectAnomalyFromOverview}
            activeMeta={activeMeta}
            onDatasetChanged={handleDatasetChanged}
          />
        )}
        {activeTab === 'anomalies' && (
          <Anomalies 
            initialSelectedId={selectedAnomalyIndex}
            onClearInitialSelected={() => setSelectedAnomalyIndex(null)}
            activeMeta={activeMeta}
            onDatasetChanged={handleDatasetChanged}
          />
        )}
        {activeTab === 'forecast' && (
          <Forecast 
            activeMeta={activeMeta}
            onDatasetChanged={handleDatasetChanged}
          />
        )}
        {activeTab === 'cost-analysis' && (
          <CostAnalysis 
            activeMeta={activeMeta}
            onDatasetChanged={handleDatasetChanged}
          />
        )}
        {activeTab === 'recommendations' && (
          <Recommendations 
            activeMeta={activeMeta}
            onDatasetChanged={handleDatasetChanged}
          />
        )}
      </main>
    </div>
  );
}

export default App;
