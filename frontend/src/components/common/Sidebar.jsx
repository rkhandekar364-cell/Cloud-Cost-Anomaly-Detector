import React from 'react';
import { 
  BarChart3, 
  AlertTriangle, 
  TrendingUp, 
  PieChart, 
  Lightbulb, 
  Cloud,
  CheckCircle2,
  XCircle
} from 'lucide-react';

export const Sidebar = ({ activeTab, setActiveTab, apiConnected }) => {
  const navItems = [
    { id: 'overview', label: 'Overview', icon: BarChart3 },
    { id: 'anomalies', label: 'Anomalies', icon: AlertTriangle },
    { id: 'forecast', label: 'Forecast', icon: TrendingUp },
    { id: 'cost-analysis', label: 'Cost Analysis', icon: PieChart },
    { id: 'recommendations', label: 'Recommendations', icon: Lightbulb },
  ];

  return (
    <aside className="sidebar">
      {/* Brand Header */}
      <div style={{ padding: '24px 20px', borderBottom: '1px solid rgba(255,255,255,0.08)', display: 'flex', alignItems: 'center', gap: '12px' }}>
        <div style={{ width: '36px', height: '36px', borderRadius: '8px', backgroundColor: 'var(--primary-blue)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <Cloud size={20} color="#FFFFFF" />
        </div>
        <div>
          <div style={{ fontSize: '15px', fontWeight: 700, color: '#F8FAFC', letterSpacing: '-0.01em' }}>
            Cloud Cost
          </div>
          <div style={{ fontSize: '11px', color: '#94A3B8', fontWeight: 500, letterSpacing: '0.04em', textTransform: 'uppercase' }}>
            Anomaly Detector
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav style={{ padding: '16px 12px', flex: 1 }}>
        <div style={{ fontSize: '11px', fontWeight: 600, color: '#64748B', padding: '0 12px 8px 12px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
          Analytics & ML
        </div>
        <ul style={{ listStyle: 'none' }}>
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <li key={item.id} style={{ marginBottom: '4px' }}>
                <button
                  onClick={() => setActiveTab(item.id)}
                  style={{
                    width: '100%',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '12px',
                    padding: '10px 14px',
                    borderRadius: '6px',
                    border: 'none',
                    backgroundColor: isActive ? 'var(--bg-sidebar-active)' : 'transparent',
                    color: isActive ? '#FFFFFF' : '#94A3B8',
                    fontSize: '13px',
                    fontWeight: isActive ? 600 : 500,
                    cursor: 'pointer',
                    transition: 'all 0.15s ease',
                    textAlign: 'left'
                  }}
                >
                  <Icon size={18} color={isActive ? 'var(--primary-blue)' : '#94A3B8'} />
                  <span>{item.label}</span>
                </button>
              </li>
            );
          })}
        </ul>
      </nav>

      {/* Bottom System Status */}
      <div style={{ padding: '16px 20px', borderTop: '1px solid rgba(255,255,255,0.08)', backgroundColor: '#0B1120' }}>
        <div style={{ fontSize: '11px', fontWeight: 600, color: '#64748B', marginBottom: '6px', textTransform: 'uppercase' }}>
          System Status
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '12px', color: apiConnected ? '#34D399' : '#F87171' }}>
          {apiConnected ? <CheckCircle2 size={14} /> : <XCircle size={14} />}
          <span style={{ fontWeight: 500 }}>
            {apiConnected ? 'API Connected (v1.0)' : 'API Disconnected'}
          </span>
        </div>
      </div>
    </aside>
  );
};
