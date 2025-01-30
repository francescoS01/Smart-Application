<template>
  <h1 class="page-title font-bold">KPI</h1>
  <section class="flex flex-col gap-4">
    <!-- Sezione KPI -->
    <div class="flex flex-col lg:flex-row gap-4">
      <!-- KPI_1 -->
      <div class="flex flex-col gap-6 w-full lg:w-1/3 p-4 bg-backgroundSecondary shadow-md rounded-lg border border-gray-200">
        <div style="display: flex; flex-direction: row; justify-content: space-between">
          <!-- Titolo -->
          <h2 class="font-semibold text-2xl text-gray-800 mb-4">Cost Management KPIs</h2>
          <button
            class="p-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition duration-200 shadow-sm flex items-center justify-center"
            aria-label="Expand View"
          >
            <!-- Icona di Vuestic -->
            <va-icon name="open_in_full" class="text-xl" />
          </button>
        </div>

        <!-- Selezione KPI -->
        <div class="flex flex-col gap-3">
          <select class="p-3 border border-gray-300 rounded-lg bg-gray-50 focus:ring-2 focus:ring-blue-400 focus:outline-none" @change="onKPIChange($event?.target, 'KPI_1', machineKPI_1, IntervalKPI_1)">
            <option value="" disabled selected>Select KPI</option>
            <option v-for="kpi in data.KPI_1.list_kpi" :key="kpi.nameID" :value="kpi.nameID">
              {{ kpi.nameID }}
            </option>
          </select>
          <select class="p-3 border border-gray-300 rounded-lg bg-gray-50 focus:ring-2 focus:ring-blue-400 focus:outline-none" @change="onMachineChange($event?.target, 'KPI_1', IntervalKPI_1)" ref="machineKPI_1">
            <option value="" disabled selected>Select machine</option>
            <option v-for="machine in data.KPI_1.list_machines" :key="machine.id" :value="machine.id">
              {{ machine.name }}
            </option>
          </select>
          <select class="p-3 border border-gray-300 rounded-lg bg-gray-50 focus:ring-2 focus:ring-blue-400 focus:outline-none"  @change="onTimeIntervalChange($event?.target, 'KPI_1')" ref="IntervalKPI_1">
            <option value="" disabled selected>Select time interval</option>
            <template  v-if="data.KPI_1.selected_machine!==null">              
              <option value="Week">Week</option>
              <option value="Month">Month</option>
              <option value="Year">Year</option>
            </template >
          </select>
        </div>

        <!-- Componenti -->
        <div class="bg-gray-100 rounded-lg flex items-center justify-center border border-gray-300" v-if="!data.KPI_1.isLoading">
          <TimeKpiGraph class="w-full" />
        </div>
        <div class="bg-gray-50 rounded-lg flex items-center justify-center p-4 border border-gray-300" v-if="!data.KPI_1.isLoading">
          <TimeKpiDataSection class="flex w-full" />
        </div>

        <!-- Spinner di caricamento -->
        <div class="bg-gray-50 rounded-lg flex items-center justify-center p-4 border border-gray-300" style="min-height: 40vh;" v-if="data.KPI_1.isLoading">
          <div class="flex flex-col items-center">
            <!-- Spinner -->
            <svg 
              class="animate-spin h-8 w-8 text-gray-500" 
              xmlns="http://www.w3.org/2000/svg" 
              fill="none" 
              viewBox="0 0 24 24">
              <circle 
                class="opacity-25" 
                cx="12" 
                cy="12" 
                r="10" 
                stroke="currentColor" 
                stroke-width="4">
              </circle>
              <path 
                class="opacity-75" 
                fill="currentColor" 
                d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z">
              </path>
            </svg>
            <span class="mt-2 text-gray-600">Caricamento...</span>
          </div>
        </div>
      </div>

      <!-- KPI_2 -->
      <div class="flex flex-col gap-6 w-full lg:w-1/3 p-4 bg-backgroundSecondary shadow-md rounded-lg border border-gray-200">
        <div style="display: flex; flex-direction: row; justify-content: space-between">
          <!-- Titolo -->
          <h2 class="font-semibold text-2xl text-gray-800 mb-4">Energy and Environmental KPIs</h2>
          <button
            class="p-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition duration-200 shadow-sm flex items-center justify-center"
            aria-label="Expand View"
          >
            <!-- Icona di Vuestic -->
            <va-icon name="open_in_full" class="text-xl" />
          </button>
        </div>

        <!-- Selezione KPI -->
        <div class="flex flex-col gap-3">
          <select class="p-3 border border-gray-300 rounded-lg bg-gray-50 focus:ring-2 focus:ring-blue-400 focus:outline-none" @change="onKPIChange($event?.target, 'KPI_2', machineKPI_2, IntervalKPI_2)">
            <option value="" disabled selected>Select KPI</option>
            <option v-for="kpi in data.KPI_2.list_kpi" :key="kpi.nameID" :value="kpi.nameID">
              {{ kpi.nameID }}
            </option>
          </select>
          <select class="p-3 border border-gray-300 rounded-lg bg-gray-50 focus:ring-2 focus:ring-blue-400 focus:outline-none" @change="onMachineChange($event?.target, 'KPI_2', IntervalKPI_2)" ref="machineKPI_2">
            <option value="" disabled selected>Select machine</option>
            <option v-for="machine in data.KPI_2.list_machines" :key="machine.id" :value="machine.id">
              {{ machine.name }}
            </option>
          </select>
          <select class="p-3 border border-gray-300 rounded-lg bg-gray-50 focus:ring-2 focus:ring-blue-400 focus:outline-none"  @change="onTimeIntervalChange($event?.target, 'KPI_2')" ref="IntervalKPI_2">
            <option value="" disabled selected>Select time interval</option>
            <template  v-if="data.KPI_2.selected_machine!==null">              
              <option value="Week">Week</option>
              <option value="Month">Month</option>
              <option value="Year">Year</option>
            </template >
          </select>
        </div>

        <!-- Componenti -->
        <div class="bg-gray-100 rounded-lg flex items-center justify-center border border-gray-300" v-if="!data.KPI_2.isLoading">
          <EnergyKpiGraph class="w-full" />
        </div>
        <div class="bg-gray-50 rounded-lg flex items-center justify-center p-4 border border-gray-300" v-if="!data.KPI_2.isLoading">
          <EnergyKpiDataSection class="flex w-full" />
        </div>

        <!-- Spinner di caricamento -->
        <div class="bg-gray-50 rounded-lg flex items-center justify-center p-4 border border-gray-300" style="min-height: 40vh;" v-if="data.KPI_2.isLoading">
          <div class="flex flex-col items-center">
            <!-- Spinner -->
            <svg 
              class="animate-spin h-8 w-8 text-gray-500" 
              xmlns="http://www.w3.org/2000/svg" 
              fill="none" 
              viewBox="0 0 24 24">
              <circle 
                class="opacity-25" 
                cx="12" 
                cy="12" 
                r="10" 
                stroke="currentColor" 
                stroke-width="4">
              </circle>
              <path 
                class="opacity-75" 
                fill="currentColor" 
                d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z">
              </path>
            </svg>
            <span class="mt-2 text-gray-600">Caricamento...</span>
          </div>
        </div>
      </div>

      <!-- KPI_£ -->
      <div class="flex flex-col gap-6 w-full lg:w-1/3 p-4 bg-backgroundSecondary shadow-md rounded-lg border border-gray-200">
        <div style="display: flex; flex-direction: row; justify-content: space-between">
          <!-- Titolo -->
          <h2 class="font-semibold text-2xl text-gray-800 mb-4">Overall Performance KPIs</h2>
          <button
            class="p-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition duration-200 shadow-sm flex items-center justify-center"
            aria-label="Expand View"
          >
            <!-- Icona di Vuestic -->
            <va-icon name="open_in_full" class="text-xl" />
          </button>
        </div>

        <!-- Selezione KPI -->
        <div class="flex flex-col gap-3">
          <select class="p-3 border border-gray-300 rounded-lg bg-gray-50 focus:ring-2 focus:ring-blue-400 focus:outline-none" @change="onKPIChange($event?.target, 'KPI_3', machineKPI_3, IntervalKPI_3)">
            <option value="" disabled selected>Select KPI</option>
            <option v-for="kpi in data.KPI_3.list_kpi" :key="kpi.nameID" :value="kpi.nameID">
              {{ kpi.nameID }}
            </option>
          </select>
          <select class="p-3 border border-gray-300 rounded-lg bg-gray-50 focus:ring-2 focus:ring-blue-400 focus:outline-none" @change="onMachineChange($event?.target, 'KPI_3', IntervalKPI_3)" ref="machineKPI_3">
            <option value="" disabled selected>Select machine</option>
            <option v-for="machine in data.KPI_3.list_machines" :key="machine.id" :value="machine.id">
              {{ machine.name }}
            </option>
          </select>
          <select class="p-3 border border-gray-300 rounded-lg bg-gray-50 focus:ring-2 focus:ring-blue-400 focus:outline-none"  @change="onTimeIntervalChange($event?.target, 'KPI_3')" ref="IntervalKPI_3">
            <option value="" disabled selected>Select time interval</option>
            <template  v-if="data.KPI_3.selected_machine!==null">              
              <option value="Week">Week</option>
              <option value="Month">Month</option>
              <option value="Year">Year</option>
            </template >
          </select>
        </div>

        <!-- Componenti -->
        <div class="bg-gray-100 rounded-lg flex items-center justify-center border border-gray-300" v-if="!data.KPI_3.isLoading">
          <ProductionKpiGraph class="w-full" />
        </div>
        <div class="bg-gray-50 rounded-lg flex items-center justify-center p-4 border border-gray-300" v-if="!data.KPI_3.isLoading">
          <ProductionKpiDataSection class="flex w-full" />
        </div>

        <!-- Spinner di caricamento -->
        <div class="bg-gray-50 rounded-lg flex items-center justify-center p-4 border border-gray-300" style="min-height: 40vh;" v-if="data.KPI_3.isLoading">
          <div class="flex flex-col items-center">
            <!-- Spinner -->
            <svg 
              class="animate-spin h-8 w-8 text-gray-500" 
              xmlns="http://www.w3.org/2000/svg" 
              fill="none" 
              viewBox="0 0 24 24">
              <circle 
                class="opacity-25" 
                cx="12" 
                cy="12" 
                r="10" 
                stroke="currentColor" 
                stroke-width="4">
              </circle>
              <path 
                class="opacity-75" 
                fill="currentColor" 
                d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z">
              </path>
            </svg>
            <span class="mt-2 text-gray-600">Caricamento...</span>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script lang="ts" setup>
import { onMounted, ref } from 'vue'
import EnergyKpiGraph from './components/EnergyKpiGraph.vue'
import ProductionKpiGraph from './components/ProductionKpiGraph.vue'
import TimeKpiGraph from './components/TimeKpiGraph.vue'
import EnergyKpiDataSection from './components/EnergyKpiDataSection.vue'
import ProductionKpiDataSection from './components/ProductionKpiDataSection.vue'
import TimeKpiDataSection from './components/TimeKpiDataSection.vue'
import { useKpiStore } from '../../../stores/kpi'
import ServiceHTTP, { GetMachines_response, KPI, KpiValues } from '../../../api/service'



// ------------------ Lifecycle Hooks ------------------
onMounted(() => {
  fetchKPI()
})

// ------------------ Variable ------------------
const machineKPI_1 = ref<HTMLSelectElement | null>(null);
const machineKPI_2 = ref<HTMLSelectElement | null>(null);
const machineKPI_3 = ref<HTMLSelectElement | null>(null);
const IntervalKPI_1 = ref<HTMLSelectElement | null>(null);
const IntervalKPI_2 = ref<HTMLSelectElement | null>(null);
const IntervalKPI_3 = ref<HTMLSelectElement | null>(null);
const store = useKpiStore()
const data = ref<Data>({
  KPI_1: { list_kpi: [], isLoading: false, showGraph: false, selected_kpi: null, list_machines: [], selected_machine: null, graph_values: [], unit_of_measure: '', average_day: { startDate: '', endDate: '', value: 0 }, average_week: { startDate: '', endDate: '', value: 0 }, average_month: { startDate: '', endDate: '', value: 0 } },
  KPI_2: { list_kpi: [], isLoading: false, showGraph: false, selected_kpi: null, list_machines: [], selected_machine: null, graph_values: [], unit_of_measure: '', average_day: { startDate: '', endDate: '', value: 0 }, average_week: { startDate: '', endDate: '', value: 0 }, average_month: { startDate: '', endDate: '', value: 0 } },
  KPI_3: { list_kpi: [], isLoading: false, showGraph: false, selected_kpi: null, list_machines: [], selected_machine: null, graph_values: [], unit_of_measure: '', average_day: { startDate: '', endDate: '', value: 0 }, average_week: { startDate: '', endDate: '', value: 0 }, average_month: { startDate: '', endDate: '', value: 0 } }
})

// ------------------ Methods ------------------
// Funzione per caricare i KPI
async function fetchKPI() {
  try {
    const response = await ServiceHTTP.getKPI()
    data.value = categorizeKpi(response)
  } catch (error) {
    console.error('Error fetching KPIs:', error)
  }
}

async function onKPIChange(kpi: EventTarget | null, category: KPI_category, machine: HTMLSelectElement | null, interval: HTMLSelectElement | null) {
  const kpi_id = (kpi as HTMLSelectElement)?.value
  if (machine && machine.value){ machine.value = ""; }
  if (interval && interval.value){ interval.value = ""; }
  data.value[category] = { ...data.value[category], showGraph: false, selected_kpi: kpi_id, list_machines: [], selected_machine: null, graph_values: [], unit_of_measure: '', average_day: { startDate: '', endDate: '', value: 0 }, average_week: { startDate: '', endDate: '', value: 0 }, average_month: { startDate: '', endDate: '', value: 0 } }
  try {
    const response = await ServiceHTTP.getMachines(kpi_id);
    data.value[category].list_machines = formatResponseMachine(response);
  } catch (error) {
    console.error('Error fetching KPIs machine:', error)
  }
}
async function onMachineChange(machine: EventTarget | null, category: KPI_category, interval: HTMLSelectElement | null) {
  const machine_id = Number((machine as HTMLSelectElement)?.value)
  if (interval && interval.value){ interval.value = ""; }
  data.value[category] = { ...data.value[category], showGraph: true, isLoading: false, selected_machine: machine_id, graph_values: [], average_day: { startDate: '', endDate: '', value: 0 }, average_week: { startDate: '', endDate: '', value: 0 }, average_month: { startDate: '', endDate: '', value: 0 } }
}
async function onTimeIntervalChange(interval: EventTarget | null, category: KPI_category) {
  const interval_id = (interval as HTMLSelectElement)?.value as "Week"|"Month"|"Year"
  const kpi_id = data.value[category].selected_kpi || 'undefined' 
  const machine_id = data.value[category].selected_machine || 0
  data.value[category] = { ...data.value[category], isLoading: true, showGraph: true, selected_machine: machine_id, graph_values: [], average_day: { startDate: '', endDate: '', value: 0 }, average_week: { startDate: '', endDate: '', value: 0 }, average_month: { startDate: '', endDate: '', value: 0 } }
  try {
    const [response, response_day, response_week, response_year] = await Promise.all([
      ServiceHTTP.getMachineKPIValues(kpi_id, machine_id, interval_id),
      ServiceHTTP.getMachineKPIValues_period(kpi_id, machine_id, 'Day'),
      ServiceHTTP.getMachineKPIValues_period(kpi_id, machine_id, 'Week'),
      ServiceHTTP.getMachineKPIValues_period(kpi_id, machine_id, 'Month'),
    ])
    data.value[category].graph_values = response.values
    data.value[category].average_day = response_day
    data.value[category].average_week = response_week
    data.value[category].average_month = response_year

    store.KPI_setValues(category, data.value[category].graph_values, response.unit, response_day.value, response_week.value, response_year.value)
  } catch (error) {
    console.error('Error fetching KPIs machine:', error)
  }
  finally {
    data.value[category].isLoading = false
  }
}
</script>

<script lang="ts">
// INTERFACES
interface DataCategory {
  showGraph: boolean
  isLoading: boolean
  list_kpi: KPI[]
  selected_kpi: string | null
  list_machines: {
    id: number
    name: string
  }[]
  selected_machine: number | null
  graph_values: KpiValues[]
  unit_of_measure: string
  average_day: KpiValues
  average_week: KpiValues
  average_month: KpiValues
}
interface Data {
  KPI_1: DataCategory
  KPI_2: DataCategory
  KPI_3: DataCategory
}
type KPI_category = 'KPI_1' | 'KPI_2' | 'KPI_3'

// UTILS
export function categorizeKpi(kpiList: KPI[]): Data {
  const init_data: Data = {
    KPI_1: { list_kpi: [], isLoading: false, showGraph: false, selected_kpi: null, list_machines: [], selected_machine: null, graph_values: [], unit_of_measure: '', average_day: { startDate: '', endDate: '', value: 0}, average_week:{ startDate: '', endDate: '', value: 0}, average_month:{ startDate: '', endDate: '', value: 0} },
    KPI_2: { list_kpi: [], isLoading: false, showGraph: false, selected_kpi: null, list_machines: [], selected_machine: null, graph_values: [], unit_of_measure: '', average_day:{ startDate: '', endDate: '', value: 0}, average_week:{ startDate: '', endDate: '', value: 0}, average_month:{ startDate: '', endDate: '', value: 0} },
    KPI_3: { list_kpi: [], isLoading: false, showGraph: false, selected_kpi: null, list_machines: [], selected_machine: null, graph_values: [], unit_of_measure: '', average_day:{ startDate: '', endDate: '', value: 0}, average_week:{ startDate: '', endDate: '', value: 0}, average_month:{ startDate: '', endDate: '', value: 0} },
  }

  kpiList.forEach((kpi) => {
    switch (kpi.category) {
      case "Cost Management":
        init_data.KPI_1.list_kpi.push(kpi);
        break;
      case "Energy and Environmental Impact":
        init_data.KPI_2.list_kpi.push(kpi);
        break;
      case "Overall Performance":
        init_data.KPI_3.list_kpi.push(kpi);
        break;
      default:
        console.error(`KPI has an invalid category: ${kpi.category}`);
    }
  });

  return init_data;
}
export function formatResponseMachine(response: GetMachines_response): DataCategory['list_machines'] {
  const { names, ids } = response;

  return names.map((name, index) => ({
    id: ids[index],
    name: name
  }));
}
export function convertObjectKeys(key: KPI['category']): KPI_category {
 const keyMap = {
    'Cost Management': 'KPI_1',
    'Energy and Environmental Impact': 'KPI_2',
    'Overall Performance': 'KPI_3'
  }
  return keyMap[key] as KPI_category
}
</script>

<style scoped></style>
