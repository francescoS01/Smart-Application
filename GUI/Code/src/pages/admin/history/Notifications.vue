<template>
  <VaCard>
    <VaCardTitle class="flex justify-between">
      <h1 class="card-title text-secondary font-bold uppercase">Notifications</h1>
    </VaCardTitle>
    <VaCardContent class="flex flex-col gap-1">
      <div class="flex justify-between">
        <VaButtonToggle v-model="selectedPeriod" :options="periods" color="background-element" size="small" />

        <div></div>
      </div>

      <!-- Indicatore di caricamento -->
      <div v-if="isLoading" class="loading-overlay flex items-center justify-center" style="min-height: 5rem;">
        <span class="loading-text">Caricamento in corso...</span>
      </div>

      <VaDataTable 
        v-else
        class="notifications-table"
        :columns="[
          { key: 'timestamp', label: 'Date' },
          { key: 'machineID', label: 'ID machine' },
          { key: 'kpi', label: 'KPI' },
          { key: 'alertDescription', label: 'Message' },
          { key: 'severity', label: 'Status' },
        ]"
        :items="alerts"
      >
        <template #cell(alertDescription)="{ rowData }">
          <span :style="{ color: getStatusColor(rowData.severity) }">
            {{ rowData.alertDescription }}
          </span>
        </template>
        <template #cell(severity)="{ rowData }">
          <span :style="{ color: getStatusColor(rowData.severity) }">
            {{ rowData.severity }}
          </span>
        </template>
      </VaDataTable>
    </VaCardContent>
  </VaCard>
</template>

<script setup lang="ts">
import { ref, Ref, onMounted, watch } from 'vue'
import ServiceHTTP, { Alert } from '../../../api/service'

// ------------------ Variable ------------------
const selectedPeriod = ref('Today') as Ref<'Today' | 'Week' | 'Month'>
const periods = ['Today', 'Week', 'Month'].map((period) => ({ label: period, value: period }))
const alerts = ref<Alert[]>([])
const isLoading = ref(false)

// ------------------ Lifecycle Hooks ------------------
onMounted(() => {
  fetchAlerts('Today')
})
watch(selectedPeriod, (newPeriod: 'Today' | 'Week' | 'Month') => {
  fetchAlerts(newPeriod);
});


// ------------------ Methods ------------------
async function fetchAlerts(period: 'Today' | 'Week' | 'Month') {
  try {
    isLoading.value = true;
    alerts.value = [];
    const data = await ServiceHTTP.getAlert(period)
    alerts.value = data.map((alert) => ({
      ...alert,
      timestamp: formatDate(alert.timestamp),
    }))
  } catch (error) {
    console.error('Errore durante il caricamento dei KPI:', error)
  }
  finally {
    isLoading.value = false;
  }
}
</script>

<script lang="ts">
// UTILS
function formatDate(timestamp: string): string {
  const date = new Date(timestamp)
  return date.toLocaleString('it-IT', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  })
}

const getStatusColor = (status: string): string => {
  switch (status.toLowerCase()) {
    case 'low':
      return 'green'
    case 'medium':
      return 'orange'
    case 'high':
      return 'red'
    default:
      return 'black'
  }
}
</script>

<style lang="scss" scoped>
.notifications-table {
  ::v-deep(tbody) {
    tr {
      border-top: 1px solid var(--va-background-border);
    }
  }
}
</style>
