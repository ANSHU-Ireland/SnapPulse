'use client'

import { useState, useEffect } from 'react'
import useSWR from 'swr'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js'
import { Line } from 'react-chartjs-2'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
)

const fetcher = (url: string) => fetch(url).then((res) => res.json())

export default function Dashboard() {
  const [selectedSnap, setSelectedSnap] = useState('firefox')
  const [selectedChannel, setSelectedChannel] = useState('stable')

  const { data: snapStats, error: statsError } = useSWR(
    `${process.env.NEXT_PUBLIC_API_URL}/stats/${selectedSnap}/${selectedChannel}`,
    fetcher,
    { refreshInterval: 5000 }
  )

  const { data: trendingData, error: trendingError } = useSWR(
    `${process.env.NEXT_PUBLIC_API_URL}/trending`,
    fetcher,
    { refreshInterval: 30000 }
  )

  // Mock chart data for downloads over time
  const chartData = {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
    datasets: [
      {
        label: 'Downloads',
        data: [65000, 72000, 68000, 85000, 92000, 105000],
        borderColor: 'rgb(75, 192, 192)',
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
        tension: 0.4,
      },
    ],
  }

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: `${selectedSnap} Downloads Over Time`,
      },
    },
    scales: {
      y: {
        beginAtZero: true,
      },
    },
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <h1 className="text-3xl font-bold text-gray-900">SnapPulse</h1>
              <span className="ml-2 px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded-full">
                Dashboard
              </span>
            </div>
            <div className="flex space-x-4">
              <select
                value={selectedSnap}
                onChange={(e) => setSelectedSnap(e.target.value)}
                className="border border-gray-300 rounded-md px-3 py-2"
              >
                <option value="firefox">Firefox</option>
                <option value="discord">Discord</option>
                <option value="code">VS Code</option>
                <option value="spotify">Spotify</option>
              </select>
              <select
                value={selectedChannel}
                onChange={(e) => setSelectedChannel(e.target.value)}
                className="border border-gray-300 rounded-md px-3 py-2"
              >
                <option value="stable">Stable</option>
                <option value="candidate">Candidate</option>
                <option value="beta">Beta</option>
                <option value="edge">Edge</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-blue-500 rounded-md flex items-center justify-center">
                    <span className="text-white text-sm font-medium">DL</span>
                  </div>
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">
                      Total Downloads
                    </dt>
                    <dd className="text-lg font-medium text-gray-900">
                      {snapStats?.download_total?.toLocaleString() || 'Loading...'}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-green-500 rounded-md flex items-center justify-center">
                    <span className="text-white text-sm font-medium">★</span>
                  </div>
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">
                      Rating
                    </dt>
                    <dd className="text-lg font-medium text-gray-900">
                      {snapStats?.rating || 'N/A'}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-yellow-500 rounded-md flex items-center justify-center">
                    <span className="text-white text-sm font-medium">v</span>
                  </div>
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">
                      Version
                    </dt>
                    <dd className="text-lg font-medium text-gray-900">
                      {snapStats?.version || 'N/A'}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-purple-500 rounded-md flex items-center justify-center">
                    <span className="text-white text-sm font-medium">📈</span>
                  </div>
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">
                      Trending Score
                    </dt>
                    <dd className="text-lg font-medium text-gray-900">
                      {snapStats?.trending_score || 'N/A'}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Charts and Trending */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Download Chart */}
          <div className="lg:col-span-2 bg-white p-6 rounded-lg shadow">
            <h2 className="text-lg font-medium text-gray-900 mb-4">
              Download Trends
            </h2>
            <Line data={chartData} options={chartOptions} />
          </div>

          {/* Trending Snaps */}
          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-lg font-medium text-gray-900 mb-4">
              Trending Snaps
            </h2>
            <div className="space-y-3">
              {trendingData?.trending?.map((snap: any, index: number) => (
                <div key={snap.name} className="flex items-center justify-between">
                  <div className="flex items-center">
                    <span className="w-6 h-6 bg-blue-100 text-blue-800 rounded-full flex items-center justify-center text-xs font-medium mr-3">
                      {index + 1}
                    </span>
                    <span className="text-sm font-medium text-gray-900">
                      {snap.name}
                    </span>
                  </div>
                  <div className="text-right">
                    <div className="text-sm text-green-600 font-medium">
                      +{snap.downloads_growth}%
                    </div>
                    <div className="text-xs text-gray-500">
                      ★ {snap.rating}
                    </div>
                  </div>
                </div>
              )) || <div>Loading trending data...</div>}
            </div>
          </div>
        </div>

        {/* Additional Snap Details */}
        {snapStats && (
          <div className="mt-8 bg-white shadow rounded-lg">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-lg font-medium text-gray-900">
                {selectedSnap} Details
              </h2>
            </div>
            <div className="px-6 py-4">
              <dl className="grid grid-cols-1 gap-x-4 gap-y-6 sm:grid-cols-2">
                <div>
                  <dt className="text-sm font-medium text-gray-500">Publisher</dt>
                  <dd className="mt-1 text-sm text-gray-900">{snapStats.publisher}</dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500">Confinement</dt>
                  <dd className="mt-1 text-sm text-gray-900">{snapStats.confinement}</dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500">Grade</dt>
                  <dd className="mt-1 text-sm text-gray-900">{snapStats.grade}</dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500">Last Updated</dt>
                  <dd className="mt-1 text-sm text-gray-900">
                    {new Date(snapStats.last_updated).toLocaleDateString()}
                  </dd>
                </div>
              </dl>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
