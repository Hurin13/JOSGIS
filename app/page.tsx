"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart"
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  AreaChart,
  Area,
} from "recharts"

const productivityData = [
  { month: "Jan", productivity: 2.5, rainfall: 180 },
  { month: "Feb", productivity: 2.8, rainfall: 220 },
  { month: "Mar", productivity: 3.2, rainfall: 160 },
  { month: "Apr", productivity: 3.5, rainfall: 90 },
  { month: "May", productivity: 3.8, rainfall: 70 },
  { month: "Jun", productivity: 3.9, rainfall: 50 },
  { month: "Jul", productivity: 3.6, rainfall: 40 },
  { month: "Aug", productivity: 3.2, rainfall: 30 },
  { month: "Sep", productivity: 2.9, rainfall: 60 },
  { month: "Oct", productivity: 2.6, rainfall: 120 },
  { month: "Nov", productivity: 2.4, rainfall: 200 },
  { month: "Dec", productivity: 2.2, rainfall: 250 },
]

const plantHealthData = [
  { month: "Jan", deadTrees: 2, plantHeight: 3.5, yellowLeaves: 12 },
  { month: "Feb", deadTrees: 1, plantHeight: 3.6, yellowLeaves: 10 },
  { month: "Mar", deadTrees: 1, plantHeight: 3.8, yellowLeaves: 8 },
  { month: "Apr", deadTrees: 2, plantHeight: 4.0, yellowLeaves: 15 },
  { month: "May", deadTrees: 1, plantHeight: 4.1, yellowLeaves: 9 },
  { month: "Jun", deadTrees: 0, plantHeight: 4.2, yellowLeaves: 5 },
]

const pestAttackData = [
  { name: "Penggerek Buah Jeruk", value: 32, color: "#ea580c" },
  { name: "Kutu Perisai", value: 28, color: "#f97316" },
  { name: "Tungau Laba-laba", value: 22, color: "#fb923c" },
  { name: "Lalat Buah", value: 14, color: "#fdba74" },
  { name: "Lainnya", value: 4, color: "#fed7aa" },
]

const varietyDistribution = [
  { variety: "Jeruk Semboro Manis", area: 40, color: "#d97706" },
  { variety: "Jeruk Semboro Asam", area: 35, color: "#f97316" },
  { variety: "Jeruk Semboro Hybrid", area: 20, color: "#fb923c" },
  { variety: "Lainnya", area: 5, color: "#fbbf24" },
]

const maintenanceData = [
  { month: "Jan", pruning: 6, fertilizing: 10, weeding: 12 },
  { month: "Feb", pruning: 5, fertilizing: 9, weeding: 14 },
  { month: "Mar", pruning: 8, fertilizing: 12, weeding: 16 },
  { month: "Apr", pruning: 10, fertilizing: 14, weeding: 18 },
  { month: "May", pruning: 8, fertilizing: 15, weeding: 20 },
  { month: "Jun", pruning: 6, fertilizing: 11, weeding: 16 },
]

const chartConfig = {
  productivity: { label: "Produktivitas (ton/ha)", color: "#ea580c" },
  rainfall: { label: "Curah Hujan (mm)", color: "#3b82f6" },
  deadTrees: { label: "Pohon Mati", color: "#ef4444" },
  plantHeight: { label: "Tinggi Tanaman (m)", color: "#22c55e" },
  yellowLeaves: { label: "Daun Menguning (%)", color: "#f59e0b" },
  pruning: { label: "Pemangkasan", color: "#d97706" },
  fertilizing: { label: "Pemupukan", color: "#f97316" },
  weeding: { label: "Penyiangan", color: "#fb923c" },
}

export default function FarmingDashboard() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 via-amber-50 to-orange-100 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        <div className="text-center mb-8 bg-gradient-to-r from-orange-600 to-orange-500 rounded-xl p-8 text-white shadow-lg">
          <div className="flex items-center justify-center gap-3 mb-2">
            <span className="text-4xl">🍊</span>
            <h1 className="text-4xl font-bold">JOSGIS</h1>
          </div>
          <p className="text-lg text-orange-100 mb-1 font-semibold">Jeruk Semboro's Geographic Information System</p>
          <p className="text-orange-50">Platform Monitoring dan Analisis Data Kebun Jeruk Semboro</p>
        </div>

        {/* Main Charts Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Productivity vs Rainfall */}
          <Card className="shadow-lg border-0 bg-white/90 backdrop-blur hover:shadow-xl transition-shadow">
            <CardHeader>
              <CardTitle className="text-orange-700 flex items-center gap-2">📊 Produktivitas vs Curah Hujan</CardTitle>
              <CardDescription>Korelasi produktivitas Jeruk Semboro dengan curah hujan bulanan</CardDescription>
            </CardHeader>
            <CardContent>
              <ChartContainer config={chartConfig} className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={productivityData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                    <XAxis dataKey="month" stroke="#6b7280" />
                    <YAxis yAxisId="left" stroke="#ea580c" />
                    <YAxis yAxisId="right" orientation="right" stroke="#3b82f6" />
                    <ChartTooltip content={<ChartTooltipContent />} />
                    <Area
                      yAxisId="left"
                      type="monotone"
                      dataKey="productivity"
                      stroke="#ea580c"
                      fill="#ea580c"
                      fillOpacity={0.2}
                      strokeWidth={3}
                    />
                    <Bar yAxisId="right" dataKey="rainfall" fill="#3b82f6" opacity={0.6} />
                  </AreaChart>
                </ResponsiveContainer>
              </ChartContainer>
            </CardContent>
          </Card>

          {/* Plant Health Metrics */}
          <Card className="shadow-lg border-0 bg-white/90 backdrop-blur hover:shadow-xl transition-shadow">
            <CardHeader>
              <CardTitle className="text-orange-700 flex items-center gap-2">🌳 Kesehatan Tanaman</CardTitle>
              <CardDescription>Monitoring kondisi kesehatan tanaman Jeruk Semboro</CardDescription>
            </CardHeader>
            <CardContent>
              <ChartContainer config={chartConfig} className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={plantHealthData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                    <XAxis dataKey="month" stroke="#6b7280" />
                    <YAxis stroke="#6b7280" />
                    <ChartTooltip content={<ChartTooltipContent />} />
                    <Line
                      type="monotone"
                      dataKey="deadTrees"
                      stroke="#ef4444"
                      strokeWidth={3}
                      dot={{ fill: "#ef4444", strokeWidth: 2, r: 4 }}
                    />
                    <Line
                      type="monotone"
                      dataKey="plantHeight"
                      stroke="#22c55e"
                      strokeWidth={3}
                      dot={{ fill: "#22c55e", strokeWidth: 2, r: 4 }}
                    />
                    <Line
                      type="monotone"
                      dataKey="yellowLeaves"
                      stroke="#f59e0b"
                      strokeWidth={3}
                      dot={{ fill: "#f59e0b", strokeWidth: 2, r: 4 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </ChartContainer>
            </CardContent>
          </Card>

          {/* Pest Attack Distribution */}
          <Card className="shadow-lg border-0 bg-white/90 backdrop-blur hover:shadow-xl transition-shadow">
            <CardHeader>
              <CardTitle className="text-orange-700 flex items-center gap-2">🐛 Distribusi Serangan Hama</CardTitle>
              <CardDescription>Jenis hama Jeruk Semboro yang paling sering menyerang</CardDescription>
            </CardHeader>
            <CardContent>
              <ChartContainer config={chartConfig} className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={pestAttackData}
                      cx="50%"
                      cy="50%"
                      outerRadius={100}
                      dataKey="value"
                      label={({ name, value }) => `${name}: ${value}%`}
                      labelLine={false}
                    >
                      {pestAttackData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <ChartTooltip content={<ChartTooltipContent />} />
                  </PieChart>
                </ResponsiveContainer>
              </ChartContainer>
            </CardContent>
          </Card>

          {/* Variety Distribution */}
          <Card className="shadow-lg border-0 bg-white/90 backdrop-blur hover:shadow-xl transition-shadow">
            <CardHeader>
              <CardTitle className="text-orange-700 flex items-center gap-2">🍊 Distribusi Varietas Jeruk</CardTitle>
              <CardDescription>Luas lahan berdasarkan varietas Jeruk Semboro</CardDescription>
            </CardHeader>
            <CardContent>
              <ChartContainer config={chartConfig} className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={varietyDistribution} layout="horizontal">
                    <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                    <XAxis type="number" stroke="#6b7280" />
                    <YAxis dataKey="variety" type="category" stroke="#6b7280" width={150} />
                    <ChartTooltip content={<ChartTooltipContent />} />
                    <Bar dataKey="area" radius={[0, 4, 4, 0]}>
                      {varietyDistribution.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </ChartContainer>
            </CardContent>
          </Card>
        </div>

        {/* Maintenance Activities */}
        <Card className="shadow-lg border-0 bg-white/90 backdrop-blur">
          <CardHeader>
            <CardTitle className="text-orange-700 flex items-center gap-2">🔧 Aktivitas Pemeliharaan</CardTitle>
            <CardDescription>Frekuensi kegiatan pemeliharaan tanaman Jeruk Semboro per bulan</CardDescription>
          </CardHeader>
          <CardContent>
            <ChartContainer config={chartConfig} className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={maintenanceData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                  <XAxis dataKey="month" stroke="#6b7280" />
                  <YAxis stroke="#6b7280" />
                  <ChartTooltip content={<ChartTooltipContent />} />
                  <Bar dataKey="pruning" fill="#d97706" radius={[2, 2, 0, 0]} />
                  <Bar dataKey="fertilizing" fill="#f97316" radius={[2, 2, 0, 0]} />
                  <Bar dataKey="weeding" fill="#fb923c" radius={[2, 2, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </ChartContainer>
          </CardContent>
        </Card>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card className="bg-gradient-to-br from-orange-600 to-orange-500 text-white shadow-lg hover:shadow-xl transition-shadow">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-orange-100 text-sm">Total Lahan</p>
                  <p className="text-3xl font-bold">28.3 Ha</p>
                </div>
                <div className="text-4xl">🌾</div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-amber-600 to-amber-500 text-white shadow-lg hover:shadow-xl transition-shadow">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-amber-100 text-sm">Rata-rata Produktivitas</p>
                  <p className="text-3xl font-bold">3.1 ton/ha</p>
                </div>
                <div className="text-4xl">📊</div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-orange-700 to-orange-600 text-white shadow-lg hover:shadow-xl transition-shadow">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-orange-100 text-sm">Jumlah Petani</p>
                  <p className="text-3xl font-bold">23</p>
                </div>
                <div className="text-4xl">👨‍🌾</div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-red-500 to-orange-500 text-white shadow-lg hover:shadow-xl transition-shadow">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-red-100 text-sm">Serangan Hama</p>
                  <p className="text-3xl font-bold">5%</p>
                </div>
                <div className="text-4xl">🐛</div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
