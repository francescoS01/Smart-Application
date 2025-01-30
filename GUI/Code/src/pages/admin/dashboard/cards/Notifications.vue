<template>
  <VaCard>
    <VaCardTitle class="flex justify-between">
      <h1 class="card-title text-secondary font-bold uppercase">Notifications</h1>
    </VaCardTitle>
    <VaCardContent class="flex flex-col gap-1">
      <div class="flex justify-between">
        <!-- <VaButtonToggle v-model="selectedPeriod" :options="periods" color="background-element" size="small" /> -->
        <div></div>
        <VaButton preset="primary" size="small" @click="redirectTo('history')"> View all </VaButton>
      </div>

      <VaDataTable
        class="notifications-table"
        :columns="[
          { key: 'date', label: 'Date' },
          // { key: 'hour', label: 'Hour' },
          { key: 'id_machine', label: 'Id_Machine' },
          { key: 'kpi', label: 'Kpi' },
          { key: 'message', label: 'Message' },
          { key: 'status', label: 'Status' },
        ]"
        :items="filteredData"
      >
      <template #cell(status)="{ rowData }">
        <span :style="{ color: getStatusColor(rowData.status) }">
          {{ rowData.status }}
        </span>
      </template>

      </VaDataTable>
    </VaCardContent>
  </VaCard>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { ref, Ref, computed } from 'vue'

const router = useRouter()
const selectedPeriod = ref('Today') as Ref<'Today' | 'Week' | 'Month'>
const periods = ['Today', 'Week', 'Month'].map((period) => ({ label: period, value: period }))

function redirectTo(routeName: string) {
  router.push({ name: routeName }).catch((err) => {
    // Gestione degli errori (opzionale), ad esempio rotta inesistente
    if (err.name !== 'NavigationDuplicated') {
      console.error(err)
    }
  })
}

// Funzione per filtrare le notifiche in base al periodo selezionato
const filteredData = computed(() => {
  if (selectedPeriod.value === 'Today') {
    return alerts.value.slice(0, 4)
  } else if (selectedPeriod.value === 'Week') {
    return alerts.value.slice(0, 9)
  } else if (selectedPeriod.value === 'Month') {
    return alerts.value
  }
  return []
})

const alerts = ref([
  {
    id: 1,
    date: '23/01/2000, 09:22:01',
    id_machine: '3',
    kpi: "good_cycles",
    message: 'Machine overheated',
    status: 'LOW',
  },
  {
    id: 2,
    date: '23/01/2000, 07:50:03',
    id_machine: '2',
    kpi: "bad_cycles",
    message: 'Sensor malfunction detected',
    status: 'MEDIUM',
  },
  {
    id: 3,
    date: '23/01/2000, 07:41:25',
    id_machine: '7',
    kpi: "power",
    message: 'Low oil pressure',
    status: 'LOW',
  },
  {
    id: 4,
    date: '23/01/2000, 00:43:12',
    id_machine: '5',
    kpi: "power",
    message: 'Critical component failure',
    status: 'HIGH',
  },
  {
    id: 5,
    date: '2024-11-19',
    hour: '14:00',
    id_machine: 'Machine A',
    message: 'Low machine utilization rate',
    status: 'low',
  },
  {
    id: 6,
    date: '2024-11-18',
    hour: '09:00',
    machine: 'Machine E',
    message: 'High temperature detected',
    status: 'High',
  },
  { id: 7, date: '2024-11-18', hour: '11:45', machine: 'Machine F', message: 'Low lubricant levels', status: 'High' },
  {
    id: 8,
    date: '2024-11-18',
    hour: '15:20',
    machine: 'Machine G',
    message: 'Unusual vibration patterns',
    status: 'low',
  },
  {
    id: 9,
    date: '2024-11-17',
    hour: '07:15',
    machine: 'Machine H',
    message: 'Sensor calibration required',
    status: 'low',
  },
  {
    id: 10,
    date: '2024-11-17',
    hour: '13:30',
    machine: 'Machine I',
    message: 'Power fluctuations detected',
    status: 'low',
  },
  { id: 11, date: '2024-11-17', hour: '19:45', machine: 'Machine J', message: 'Unexpected shutdown', status: 'low' },
  {
    id: 12,
    date: '2024-11-16',
    hour: '10:10',
    machine: 'Machine K',
    message: 'Network connectivity issue',
    status: 'Medium',
  },
  {
    id: 13,
    date: '2024-11-16',
    hour: '14:50',
    machine: 'Machine L',
    message: 'Coolant leakage detected',
    status: 'low',
  },
  {
    id: 14,
    date: '2024-11-15',
    hour: '08:00',
    machine: 'Machine M',
    message: 'Filter replacement needed',
    status: 'Medium',
  },
  { id: 15, date: '2024-11-15', hour: '12:35', machine: 'Machine N', message: 'Abnormal noise levels', status: 'High' },
])

// Funzione per determinare il colore in base allo stato
const getStatusColor = (status: string): string => {
  switch (status) {
    case 'LOW':
      return 'green' // Colore verde per stato Low
    case 'MEDIUM':
      return 'orange' // Colore arancione per stato Medium
    case 'HIGH':
      return 'red' // Colore rosso per stato High
    default:
      return 'black' // Colore di default se lo stato è sconosciuto
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
