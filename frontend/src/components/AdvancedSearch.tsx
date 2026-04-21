import React, { useState, useMemo, useCallback } from 'react';
import { X, Search, ChevronDown } from 'lucide-react';

interface FilterConfig {
  name: string;
  type: 'checkbox' | 'range' | 'select' | 'search';
  label: string;
  options?: { value: string; label: string }[];
  min?: number;
  max?: number;
  step?: number;
}

interface SearchResult<T = any> {
  id: string;
  title: string;
  category: string;
  relevance: number;
  tags: string[];
  data: T;
}

interface AdvancedSearchProps<T = any> {
  data: T[];
  filters: FilterConfig[];
  onResultsChange?: (results: SearchResult<T>[]) => void;
  searchFields?: string[]; // Fields to search in
}

/**
 * Advanced Search & Filter Component
 *
 * Features:
 * - Full-text search across multiple fields
 * - Multi-filter support (checkbox, range, select)
 * - Real-time filtering with debouncing
 * - Filter persistence
 * - Result relevance scoring
 */
export const AdvancedSearch: React.FC<AdvancedSearchProps> = ({
  data = [],
  filters = [],
  onResultsChange,
  searchFields = ['title', 'description']
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [activeFilters, setActiveFilters] = useState<Record<string, any>>({});
  const [showFilters, setShowFilters] = useState(false);
  const [expandedFilter, setExpandedFilter] = useState<string | null>(null);

  // Calculate search relevance score
  const calculateRelevance = useCallback((item: Record<string, any>, query: string): number => {
    if (!query) return 0;

    let relevance = 0;
    const queryLower = query.toLowerCase();

    searchFields.forEach((field) => {
      const value = item[field]?.toString().toLowerCase();
      if (!value) return;

      // Exact match gets highest score
      if (value === queryLower) relevance += 100;
      // Starts with query
      else if (value.startsWith(queryLower)) relevance += 50;
      // Contains query
      else if (value.includes(queryLower)) relevance += 25;
      // Word boundary match
      else if (new RegExp(`\\b${queryLower}`).test(value)) relevance += 15;
    });

    return relevance;
  }, [searchFields]);

  // Filter and search data
  const results = useMemo(() => {
    let filtered = [...data];

    // Apply text search
    if (searchQuery.trim()) {
      filtered = filtered
        .map((item) => ({
          item,
          relevance: calculateRelevance(item, searchQuery)
        }))
        .filter(({ relevance }) => relevance > 0)
        .sort((a, b) => b.relevance - a.relevance)
        .map(({ item, relevance }) => ({
          id: item.id,
          title: item.title,
          category: item.category,
          relevance,
          tags: item.tags || [],
          data: item
        }));
    } else {
      filtered = filtered.map((item) => ({
        id: item.id,
        title: item.title,
        category: item.category,
        relevance: 100,
        tags: item.tags || [],
        data: item
      }));
    }

    // Apply additional filters
    Object.entries(activeFilters).forEach(([filterName, filterValue]) => {
      const filterConfig = filters.find((f) => f.name === filterName);
      if (!filterConfig) return;

      if (filterConfig.type === 'checkbox') {
        if (filterValue && filterValue.length > 0) {
          filtered = filtered.filter((item) =>
            filterValue.includes(item.data[filterName])
          );
        }
      } else if (filterConfig.type === 'range') {
        const [min, max] = filterValue || [filterConfig.min, filterConfig.max];
        filtered = filtered.filter((item) => {
          const value = item.data[filterName];
          return value >= min && value <= max;
        });
      } else if (filterConfig.type === 'select') {
        if (filterValue) {
          filtered = filtered.filter((item) => item.data[filterName] === filterValue);
        }
      }
    });

    return filtered;
  }, [data, searchQuery, activeFilters, filters, calculateRelevance]);

  const handleFilterChange = useCallback((filterName: string, value: unknown) => {
    setActiveFilters((prev) => ({
      ...prev,
      [filterName]: value
    }));
  }, []);

  const clearFilters = useCallback(() => {
    setActiveFilters({});
    setSearchQuery('');
  }, []);

  // Notify parent of results change
  React.useEffect(() => {
    onResultsChange?.(results);
  }, [results, onResultsChange]);

  const activeFilterCount = Object.values(activeFilters).filter(
    (v) => v && (typeof v === 'string' || (Array.isArray(v) && v.length > 0))
  ).length;

  return (
    <div className="w-full bg-white rounded-lg shadow-md p-6">
      {/* Search Bar */}
      <div className="mb-6">
        <div className="relative">
          <Search className="absolute left-3 top-3 text-gray-400 w-5 h-5" />
          <input
            type="text"
            placeholder="Search holdings, categories, topics..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          {searchQuery && (
            <button
              onClick={() => setSearchQuery('')}
              className="absolute right-3 top-3 text-gray-400 hover:text-gray-600"
            >
              <X className="w-5 h-5" />
            </button>
          )}
        </div>
      </div>

      {/* Filter Toggle */}
      <div className="flex items-center justify-between mb-4">
        <button
          onClick={() => setShowFilters(!showFilters)}
          className="flex items-center gap-2 px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg transition"
        >
          <span className="text-sm font-semibold">Filters</span>
          {activeFilterCount > 0 && (
            <span className="ml-2 px-2 py-0.5 bg-blue-500 text-white text-xs rounded-full">
              {activeFilterCount}
            </span>
          )}
          <ChevronDown
            className={`w-4 h-4 transition ${showFilters ? 'rotate-180' : ''}`}
          />
        </button>

        {activeFilterCount > 0 && (
          <button
            onClick={clearFilters}
            className="text-sm text-blue-600 hover:text-blue-800 underline"
          >
            Clear All
          </button>
        )}
      </div>

      {/* Filters Panel */}
      {showFilters && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6 p-4 bg-gray-50 rounded-lg">
          {filters.map((filter) => (
            <FilterInput
              key={filter.name}
              filter={filter}
              value={activeFilters[filter.name]}
              onChange={(value) => handleFilterChange(filter.name, value)}
              isExpanded={expandedFilter === filter.name}
              onToggleExpand={() =>
                setExpandedFilter(expandedFilter === filter.name ? null : filter.name)
              }
            />
          ))}
        </div>
      )}

      {/* Results */}
      <div className="mt-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-800">
            Results <span className="text-sm text-gray-500">({results.length})</span>
          </h3>
        </div>

        {results.length > 0 ? (
          <div className="space-y-3">
            {results.map((result) => (
              <div
                key={result.id}
                className="p-4 border border-gray-200 rounded-lg hover:shadow-md transition"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h4 className="font-semibold text-gray-900">{result.title}</h4>
                    <p className="text-sm text-gray-600 mt-1">{result.category}</p>
                    {result.tags.length > 0 && (
                      <div className="flex gap-2 mt-2">
                        {result.tags.map((tag: string) => (
                          <span
                            key={tag}
                            className="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded"
                          >
                            {tag}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                  {result.relevance < 100 && (
                    <div className="text-right ml-4">
                      <div className="w-12 h-12 rounded-full bg-gradient-to-br from-blue-400 to-blue-600 flex items-center justify-center text-white text-sm font-bold">
                        {Math.round(result.relevance / 10)}
                      </div>
                      <p className="text-xs text-gray-500 mt-1">Relevance</p>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-12 text-gray-500">
            <Search className="w-12 h-12 mx-auto mb-4 text-gray-400" />
            <p>No results found</p>
            <p className="text-sm">Try adjusting your search or filters</p>
          </div>
        )}
      </div>
    </div>
  );
};

interface FilterInputProps<T = any> {
  filter: FilterConfig;
  value: T;
  onChange: (value: T) => void;
  isExpanded: boolean;
  onToggleExpand: () => void;
}

const FilterInput: React.FC<FilterInputProps> = ({
  filter,
  value,
  onChange,
  isExpanded,
  onToggleExpand
}) => {
  if (filter.type === 'checkbox' && filter.options) {
    return (
      <div className="border border-gray-200 rounded-lg p-3 bg-white">
        <button
          onClick={onToggleExpand}
          className="w-full flex items-center justify-between text-sm font-semibold text-gray-900 mb-2"
        >
          {filter.label}
          <ChevronDown
            className={`w-4 h-4 transition ${isExpanded ? 'rotate-180' : ''}`}
          />
        </button>

        {isExpanded && (
          <div className="space-y-2 mt-3">
            {filter.options.map((option) => (
              <label key={option.value} className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={(value || []).includes(option.value)}
                  onChange={(e) => {
                    const newValue = e.target.checked
                      ? [...(value || []), option.value]
                      : (value || []).filter((v: string) => v !== option.value);
                    onChange(newValue.length > 0 ? newValue : undefined);
                  }}
                  className="w-4 h-4 rounded"
                />
                <span className="text-sm text-gray-700">{option.label}</span>
              </label>
            ))}
          </div>
        )}
      </div>
    );
  }

  if (filter.type === 'range') {
    const [min, max] = value || [filter.min, filter.max];
    return (
      <div className="border border-gray-200 rounded-lg p-3 bg-white">
        <p className="text-sm font-semibold text-gray-900 mb-3">{filter.label}</p>
        <div className="space-y-3">
          <div>
            <label className="text-xs text-gray-600">Min: {min}</label>
            <input
              type="range"
              min={filter.min}
              max={filter.max}
              step={filter.step || 1}
              value={min}
              onChange={(e) => onChange([Number(e.target.value), max])}
              className="w-full"
            />
          </div>
          <div>
            <label className="text-xs text-gray-600">Max: {max}</label>
            <input
              type="range"
              min={filter.min}
              max={filter.max}
              step={filter.step || 1}
              value={max}
              onChange={(e) => onChange([min, Number(e.target.value)])}
              className="w-full"
            />
          </div>
        </div>
      </div>
    );
  }

  if (filter.type === 'select' && filter.options) {
    return (
      <div className="border border-gray-200 rounded-lg p-3 bg-white">
        <label className="text-sm font-semibold text-gray-900 block mb-2">
          {filter.label}
        </label>
        <select
          value={value || ''}
          onChange={(e) => onChange(e.target.value || undefined)}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
        >
          <option value="">All</option>
          {filter.options.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      </div>
    );
  }

  return null;
};

export default AdvancedSearch;
