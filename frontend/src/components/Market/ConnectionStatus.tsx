import React from 'react';
import { ConnectionStatus } from '../hooks/useWebSocket';

interface ConnectionStatusProps {
  status: ConnectionStatus;
  showLabel?: boolean;
}

export function ConnectionStatusIndicator({ status, showLabel = true }: ConnectionStatusProps) {
  const getStatusConfig = () => {
    switch (status) {
      case 'connected':
        return {
          bgColor: 'bg-green-500',
          textColor: 'text-green-700',
          label: 'Live',
          dotClass: 'animate-pulse',
        };
      case 'connecting':
        return {
          bgColor: 'bg-yellow-500',
          textColor: 'text-yellow-700',
          label: 'Connecting...',
          dotClass: 'animate-bounce',
        };
      case 'disconnected':
        return {
          bgColor: 'bg-gray-400',
          textColor: 'text-gray-700',
          label: 'Offline',
          dotClass: '',
        };
      case 'error':
        return {
          bgColor: 'bg-red-500',
          textColor: 'text-red-700',
          label: 'Error',
          dotClass: 'animate-pulse',
        };
      default:
        return {
          bgColor: 'bg-gray-400',
          textColor: 'text-gray-700',
          label: 'Unknown',
          dotClass: '',
        };
    }
  };

  const config = getStatusConfig();

  return (
    <div className={`flex items-center gap-2 px-3 py-1 rounded-full ${config.bgColor} bg-opacity-20`}>
      <div className={`w-2 h-2 rounded-full ${config.bgColor} ${config.dotClass}`} />
      {showLabel && <span className={`text-sm font-medium ${config.textColor}`}>{config.label}</span>}
    </div>
  );
}

interface ConnectionStatusBadgeProps {
  status: ConnectionStatus;
}

export function ConnectionStatusBadge({ status }: ConnectionStatusBadgeProps) {
  const getStatusColor = () => {
    switch (status) {
      case 'connected':
        return 'bg-green-100 text-green-800 border-green-300';
      case 'connecting':
        return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      case 'disconnected':
        return 'bg-gray-100 text-gray-800 border-gray-300';
      case 'error':
        return 'bg-red-100 text-red-800 border-red-300';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  const getStatusLabel = () => {
    switch (status) {
      case 'connected':
        return '🔴 Live';
      case 'connecting':
        return '🟡 Connecting...';
      case 'disconnected':
        return '⚫ Offline';
      case 'error':
        return '❌ Error';
      default:
        return '❓ Unknown';
    }
  };

  return (
    <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium border ${getStatusColor()}`}>
      {getStatusLabel()}
    </span>
  );
}
