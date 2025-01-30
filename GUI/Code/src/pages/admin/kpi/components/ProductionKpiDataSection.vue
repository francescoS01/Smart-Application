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
import DataSectionItem from '../../dashboard/DataSectionItem.vue'
import { useKpiStore } from '../../../../stores/kpi';

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
const store = useKpiStore()
const KPI_3_data = computed(() => store.getKPI_3)

const dashboardMetrics = computed<DashboardMetric[]>(() => [
  {
    id: 'openInvoices',
    title: 'Average day',
    value: `${KPI_3_data.value.averageDay} (${KPI_3_data.value.unit || ''})`,
    icon: 'info',
    changeText: '',
    changeDirection: '',
    iconBackground: getColor('info'),
    iconColor: getColor('on-success'),
  },  
  {
    id: 'openInvoices',
    title: 'Average week',
    value: `${KPI_3_data.value.averageWeek} (${KPI_3_data.value.unit || ''})`,
    icon: 'info',
    changeText: '',
    changeDirection: '',
    iconBackground: getColor('info'),
    iconColor: getColor('on-success'),
  },
  {
    id: 'openInvoices',
    title: 'Average Month',
    value: `${KPI_3_data.value.averageMonth} (${KPI_3_data.value.unit || ''})`,
    icon: 'info',
    changeText: '',
    changeDirection: '',
    iconBackground: getColor('info'),
    iconColor: getColor('on-success'),
  },
])
</script>
