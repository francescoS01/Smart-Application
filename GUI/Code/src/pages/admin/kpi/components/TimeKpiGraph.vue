<template>
  <VaCard>
    <VaCardTitle>
      <h1 class="card-title text-tag text-secondary font-bold uppercase py-2">Graph</h1>
    </VaCardTitle>
    <VaCardContent>
      <div class="p-1 rounded absolute right-4 top-4" style="background-color: #4caf50">
        <VaIcon name="schedule" color="#fff" size="large" />
      </div>
      <div class="w-full flex items-center">
        <VaChart :data="chartData" type="line" :options="options" />
      </div>
    </VaCardContent>
  </VaCard>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { VaCard } from 'vuestic-ui'
import VaChart from '../../../../components/va-charts/VaChart.vue'
import { useChartData2 } from '../../../../data/charts/composables/useChartData'
import { ChartOptions } from 'chart.js'
import { useKpiStore } from '../../../../stores/kpi';

const store = useKpiStore()
const KPI_1_data = computed(() => store.getKPI_1.values)
const KPI_1_unit = computed(() => store.getKPI_1.unit || '')
const chartData = useChartData2(KPI_1_data)


const options: ChartOptions<'line'> = {
  scales: {
    x: {
      display: true,
      grid: {
        display: true, // Disable X-axis grid lines ("net")
      },
    },
    y: {
      display: true,
      grid: {
        display: true, // Disable Y-axis grid lines ("net")
      },
      ticks: {
        display: true,
        callback: function (value) {
          return `${value} (${KPI_1_unit.value})`
        },
      },
    },
  },
  interaction: {
    intersect: false,
    mode: 'index',
  },
  plugins: {
    legend: {
      display: true,
    },
    tooltip: {
      enabled: true,
      callbacks: {
        title: (tooltipItems) => {
          return `Title: ${tooltipItems[0].label}`
        },
        label: (tooltipItem) => {
          const value = tooltipItem.raw
          return `Value: ${value} (${KPI_1_unit.value})`
        },
      },
    },
  },
}
</script>
