import axios from 'axios'

const API_BASE = '/api/v1'

export type ChatResponse = {
  response: string;
  agent: string;
  sources: string[];
  routing_confidence: number;
  success: boolean;
};

export type PortfolioData = {
  holdings: Holding[];
  total_value: number;
  allocation: Record<string, number>;
  last_updated: string;
  metrics?: PortfolioMetrics;
};

export type PortfolioMetrics = {
  total_holdings: number;
  diversification_score: number;
  risk_score: number;
  largest_holding: {
    symbol: string;
    value: number;
    percentage: number;
  };
  concentration_risk: number;
  sector_allocation: Record<string, number>;
  performance_metrics: {
    total_return: number;
    annualized_return: number;
    volatility: number;
    sharpe_ratio: number;
  };
};

export type Holding = {
  symbol: string;
  quantity: number;
  avg_cost: number;
};

export type QuoteResponse = {
  symbol: string;
  price: number;
  change: number;
  change_percent: number;
  currency: string;
  source: string;
  error?: string;
};

export type PortfolioSummary = {
  summary: string;
  total_value: number;
  allocation: Record<string, number>;
};

export type PortfolioPerformance = {
  total_return: number;
  annualized_return: number;
  volatility: number;
  sharpe_ratio: number;
  max_drawdown: number;
  win_rate: number;
};

export type PortfolioAllocation = {
  current_allocation: Record<string, number>;
  recommended_allocation: Record<string, number>;
  allocation_chart: Record<string, number>;
  diversification_score: number;
};

// Enhanced API functions with axios
export const apiService = {
  async sendMessage(message: string): Promise<ChatResponse> {
    const response = await axios.post(`${API_BASE}/chat`, { message });
    return response.data;
  },

  async getPortfolio(): Promise<PortfolioData> {
    const response = await axios.get(`${API_BASE}/portfolio`);
    return response.data;
  },

  async savePortfolio(portfolio: PortfolioData): Promise<void> {
    await axios.post(`${API_BASE}/portfolio`, portfolio);
  },

  async updatePortfolio(portfolio: PortfolioData): Promise<void> {
    await axios.put(`${API_BASE}/portfolio`, portfolio);
  },

  async deleteHolding(symbol: string): Promise<void> {
    await axios.delete(`${API_BASE}/portfolio/${symbol}`);
  },

  async getPortfolioPerformance(): Promise<PortfolioPerformance> {
    const response = await axios.get(`${API_BASE}/portfolio/performance`);
    return response.data;
  },

  async getPortfolioAllocation(): Promise<PortfolioAllocation> {
    const response = await axios.get(`${API_BASE}/portfolio/allocation`);
    return response.data;
  },

  async getQuote(symbol: string): Promise<QuoteResponse> {
    const response = await axios.get(`${API_BASE}/market/quote/${encodeURIComponent(symbol)}`);
    return response.data;
  },

  async getMarketSummary(symbols: string[]): Promise<Record<string, QuoteResponse>> {
    const response = await axios.post(`${API_BASE}/market/summary`, { symbols });
    return response.data;
  },

  async getPortfolioSummary(): Promise<PortfolioSummary> {
    const response = await axios.get(`${API_BASE}/portfolio/summary`);
    return response.data;
  },

  async healthCheck(): Promise<{ status: string }> {
    const response = await axios.get(`${API_BASE}/health`);
    return response.data;
  }
};
