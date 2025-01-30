<template>
  <div class="grid grid-rows-1 sm:grid-rows-2 md:grid-rows-4 gap-4">
    <DataSectionItem
      v-for="metric in dashboardMetrics"
      :key="metric.id"
      :title="metric.title"
      :value="metric.value"
      :change-text="metric.changeText"
      :up="metric.changeDirection === 'up'"
      :icon-background="metric.iconBackground"
      :icon-color="metric.iconColor"
    >
      <template #icon>
        <VaIcon :name="metric.icon" size="large" />
      </template>
    </DataSectionItem>
  </div>
</template>

<script lang="ts" setup>
import { computed } from 'vue'
import { useColors } from 'vuestic-ui'
import DataSectionItem from './DataSectionItem.vue'

interface DashboardMetric {
  id: string
  title: string
  value: string
  icon: string
  changeText: string
  changeDirection: 'up' | 'down'
  iconBackground: string
  iconColor: string
}

const { getColor } = useColors()

const dashboardMetrics = computed<DashboardMetric[]>(() => [
  {
    id: 'openInvoices',
    title: 'Large Capacity Cutting Machine 1 Working_Time_KPI ',
    value: 'Average day: 14 h',
    icon: 'info',
    changeText: '',
    changeDirection: '',
    iconBackground: getColor('info'),
    iconColor: getColor('on-info'),
  },
  {
    id: 'openInvoices',
    title: 'Large Capacity Cutting Machine 2 Power_KPI',
    value: 'Average week: 63 kWh',
    icon: 'info',
    changeText: '',
    changeDirection: '',
    iconBackground: getColor('info'),
    iconColor: getColor('on-info'),
  },
  {
    id: 'openInvoices',
    title: 'Scheduled machines maintenance',
    value: '2',
    icon: 'info',
    changeText: '',
    changeDirection: '',
    iconBackground: getColor('info'),
    iconColor: getColor('on-info'),
  },
  {
    id: 'openInvoices',
    title: 'Number of alerts  generated  this week',
    value: '10',
    icon: 'info',
    changeText: '',
    changeDirection: '',
    iconBackground: getColor('info'),
    iconColor: getColor('on-info'),
  },
])
</script>
