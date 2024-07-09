import React, { useState, useMemo } from 'react';
import axios from 'axios';
import { ChevronUp, ChevronDown } from 'lucide-react';

function App() {
  const [wedgeSize, setWedgeSize] = useState('12.8mm');
  const [extendedDistance, setExtendedDistance] = useState('');
  const [compressedDistance, setCompressedDistance] = useState('');
  const [lockedDistance, setLockedDistance] = useState('');
  const [lockStatus, setLockStatus] = useState('unlocked');
  const [results, setResults] = useState(null);
  const [columnsOrder, setColumnsOrder] = useState([]);
  const [retainerClearanceDistance, setRetainerClearanceDistance] = useState('-0.4');
  const [extendedWedgeAnnulusClearance, setExtendedWedgeAnnulusClearance] = useState('-0.2');
  const [sortConfig, setSortConfig] = useState({ key: null, direction: 'ascending' });

  const API_BASE_URL = 'http://flask-env.eba-n6brhipk.us-east-2.elasticbeanstalk.com/';

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post(`${API_BASE_URL}/api/find_combinations`, {
        extendedDistance,
        compressedDistance,
        lockedDistance,
        lockStatus,
        wedgeSize,
        retainerClearanceDistance,
        extendedWedgeAnnulusClearance,
      });
      setResults(response.data);
      setColumnsOrder(response.data.columns_order);
      // Reset sorting when new results are fetched
      setSortConfig({ key: null, direction: 'ascending' });
    } catch (error) {
      console.error('Error fetching results:', error);
    }
  };

  const formatColumnName = (key) => {
    return key.replace('Ball to Ball', 'B2B');
  };

  const getColorStyle = (key, value) => {
    if (key === 'Extended Wedge Annulus Clearance') {
      if (value >= 0.16) return { backgroundColor: 'rgb(0, 255, 0)' };
      const normalizedValue = Math.max(0, Math.min(1, (value + 0.4) / 0.56));
      const red = Math.floor(255 * (1 - normalizedValue));
      const green = Math.floor(255 * normalizedValue);
      return { backgroundColor: `rgb(${red}, ${green}, 0)` };
    } else if (key === 'Retainer Clearance Distance') {
      if (value >= 0.45) return { backgroundColor: 'rgb(0, 255, 0)' };
      const normalizedValue = Math.max(0, Math.min(1, (value + 0.2) / 0.65));
      const red = Math.floor(255 * (1 - normalizedValue));
      const green = Math.floor(255 * normalizedValue);
      return { backgroundColor: `rgb(${red}, ${green}, 0)` };
    }
    return {};
  };

  const sortedData = useMemo(() => {
    if (!results) return [];
    const allData = [...results.larger, results.closest, ...results.smaller];
    if (!sortConfig.key) return allData;

    return [...allData].sort((a, b) => {
      if (a[sortConfig.key] < b[sortConfig.key]) {
        return sortConfig.direction === 'ascending' ? -1 : 1;
      }
      if (a[sortConfig.key] > b[sortConfig.key]) {
        return sortConfig.direction === 'ascending' ? 1 : -1;
      }
      return 0;
    });
  }, [results, sortConfig]);

  const requestSort = (key) => {
    let direction = 'ascending';
    if (sortConfig.key === key && sortConfig.direction === 'ascending') {
      direction = 'descending';
    }
    setSortConfig({ key, direction });
  };

  const SortableHeader = ({ column }) => (
    <th
      key={column}
      className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer"
      onClick={() => requestSort(column)}
    >
      <div className="flex items-center">
        {formatColumnName(column)}
        {sortConfig.key === column && (
          <span className="ml-1">
            {sortConfig.direction === 'ascending' ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
          </span>
        )}
      </div>
    </th>
  );

  const ResultTable = ({ data }) => (
    <div className="overflow-x-auto">
      <table className="min-w-full bg-white border border-gray-300">
        <thead>
          <tr className="bg-gray-100">
            {columnsOrder.map((key) => (
              <SortableHeader key={key} column={key} />
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((item, index) => (
            <tr 
              key={index} 
              className={`${index % 2 === 0 ? 'bg-gray-50' : 'bg-white'} ${item === results.closest ? 'bg-yellow-200' : ''}`}
            >
              {columnsOrder.map((key) => (
                <td 
                  key={key} 
                  className="px-4 py-2 whitespace-nowrap text-sm text-gray-900"
                  style={getColorStyle(key, item[key])}
                >
                  {typeof item[key] === 'number' ? item[key].toFixed(4) : item[key]}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Capsule Selector</h1>
      <form onSubmit={handleSubmit} className="mb-6">
        <div className="mb-4">
          <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="wedgeSize">
            Wedge Size:
          </label>
          <select
            id="wedgeSize"
            value={wedgeSize}
            onChange={(e) => setWedgeSize(e.target.value)}
            className="shadow border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
          >
            <option value="12.8mm">12.8mm</option>
            <option value="17mm">17mm</option>
          </select>
        </div>
        <div className="mb-4">
          <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="extendedDistance">
            Extended Distance:
          </label>
          <input
            id="extendedDistance"
            type="number"
            value={extendedDistance}
            onChange={(e) => setExtendedDistance(e.target.value)}
            className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
            step="0.01"
          />
        </div>
        <div className="mb-4">
          <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="compressedDistance">
            Compressed Distance:
          </label>
          <input
            id="compressedDistance"
            type="number"
            value={compressedDistance}
            onChange={(e) => setCompressedDistance(e.target.value)}
            className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
            step="0.01"
          />
        </div>
        <div className="mb-4">
          <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="lockedDistance">
            Locked Distance:
          </label>
          <input
            id="lockedDistance"
            type="number"
            value={lockedDistance}
            onChange={(e) => setLockedDistance(e.target.value)}
            className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
            step="0.01"
          />
        </div>
        <div className="mb-4">
          <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="lockStatus">
            Normally Locked/Unlocked:
          </label>
          <select
            id="lockStatus"
            value={lockStatus}
            onChange={(e) => setLockStatus(e.target.value)}
            className="shadow border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
          >
            <option value="unlocked">Unlocked</option>
            <option value="locked">Locked</option>
          </select>
        </div>
        <div className="mb-4">
          <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="retainerClearanceDistance">
            Retainer Clearance Distance (Minimum):
          </label>
          <input
            id="retainerClearanceDistance"
            type="number"
            value={retainerClearanceDistance}
            onChange={(e) => setRetainerClearanceDistance(e.target.value)}
            className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
            step="0.01"
          />
        </div>
        <div className="mb-4">
          <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="extendedWedgeAnnulusClearance">
            Extended Wedge Annulus Clearance (Minimum):
          </label>
          <input
            id="extendedWedgeAnnulusClearance"
            type="number"
            value={extendedWedgeAnnulusClearance}
            onChange={(e) => setExtendedWedgeAnnulusClearance(e.target.value)}
            className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
            step="0.01"
          />
        </div>
        <button 
          type="submit" 
          className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
        >
          Find Combinations
        </button>
      </form>
      
      {results && (
        <div>
          <h2 className="text-xl font-bold mb-4">Results</h2>
          <p className="mb-2">The highlighted row (yellow) is the closest match to your input. Click on column headers to sort.</p>
          <ResultTable data={sortedData} />
        </div>
      )}
    </div>
  );
}

export default App;