import React from 'react';
import { AlertCircle, RefreshCw } from 'lucide-react';

export class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo);
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null });
  };

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: '16px', backgroundColor: '#2A1A1A', border: '1px solid #FF6B5C', borderRadius: '8px', color: '#FF6B5C', fontSize: '13px', margin: '12px 0' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px', fontWeight: 700 }}>
            <AlertCircle size={16} />
            <span>Unable to open Data Source panel.</span>
          </div>
          <button 
            className="btn btn-sm" 
            onClick={this.handleReset}
            style={{ backgroundColor: '#FF6B5C', color: '#FFFFFF', borderColor: '#FF6B5C' }}
          >
            <RefreshCw size={12} />
            <span>Retry</span>
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}
