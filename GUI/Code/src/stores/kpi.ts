import { defineStore } from 'pinia'
import { KpiValues } from '../api/service'
import { reactive } from 'vue'

// Tipizzazione per i dati del grafico
export interface TLineChartData {
  labels: string[]
  datasets: Array<{
    label: string
    backgroundColor?: string
    borderColor?: string
    borderDash?: number[]
    data: (number | null)[]
  }>
}
export interface KPI_store {
  unit: string | null,
  values: TLineChartData,
  averageDay: number,
  averageWeek: number,
  averageMonth: number,
}

export const useKpiStore = defineStore({
  id: 'kpi',
  state: () => ({
    KPI_1: reactive<KPI_store>({
      unit: MOCK.unit,
      values: {
        labels: MOCK.values.labels,
        datasets: MOCK.values.datasets,
      },
      averageDay: MOCK.averageDay,
      averageWeek: MOCK.averageWeek,
      averageMonth: MOCK.averageMonth
    }),

    KPI_2: reactive<KPI_store>({
      unit: MOCK.unit,
      values: {
        labels: MOCK.values.labels,
        datasets: MOCK.values.datasets,
      },
      averageDay: MOCK.averageDay,
      averageWeek: MOCK.averageWeek,
      averageMonth: MOCK.averageMonth
    }),

    KPI_3: reactive<KPI_store>({
      unit: MOCK.unit,
      values: {
        labels: MOCK.values.labels,
        datasets: MOCK.values.datasets,
      },
      averageDay: MOCK.averageDay,
      averageWeek: MOCK.averageWeek,
      averageMonth: MOCK.averageMonth
    }),
  }),
  getters: {
    getKPI_1: (state): KPI_store => state.KPI_1,
    getKPI_2: (state): KPI_store => state.KPI_2,
    getKPI_3: (state): KPI_store => state.KPI_3,
  },
  actions: {
    KPI_setValues(category: ('KPI_1' | 'KPI_2' | 'KPI_3'), values: KpiValues[], unit: string, 
                  averageDay: number, averageWeek: number, averageMonth: number) {
      let labels: string[] = []
      let data: number[] = []

      values.forEach((value) => {
        labels.push(value.startDate)
        data.push( parseFloat(value.value.toFixed(2)) )
      })

      const database: TLineChartData = {
        labels: labels,
        datasets: [
          {
            label: '',
            data: data,
            backgroundColor: 'rgba(54,162,235,0.4)',
          },
        ],
      };

      if (category === 'KPI_1') {
        this.KPI_1.values = database;
        this.KPI_1.unit = unit;
        this.KPI_1.averageDay = parseFloat(averageDay.toFixed(2));
        this.KPI_1.averageWeek = parseFloat(averageWeek.toFixed(2));
        this.KPI_1.averageMonth = parseFloat(averageMonth.toFixed(2));
      }
      if (category === 'KPI_2') {
        this.KPI_2.values = database;
        this.KPI_2.unit = unit;
        this.KPI_2.averageDay = parseFloat(averageDay.toFixed(2));
        this.KPI_2.averageWeek = parseFloat(averageWeek.toFixed(2));
        this.KPI_2.averageMonth = parseFloat(averageMonth.toFixed(2));
      }
      if (category === 'KPI_3') {
        this.KPI_3.values = database;
        this.KPI_3.unit = unit;
        this.KPI_3.averageDay = parseFloat(averageDay.toFixed(2));
        this.KPI_3.averageWeek = parseFloat(averageWeek.toFixed(2));
        this.KPI_3.averageMonth = parseFloat(averageMonth.toFixed(2));
      }
    }
  },
})


const MOCK: KPI_store = {
  unit: 'kW/h',
  values: {
    labels: [
      'January',
      'February',
      'March',
      'April',
      'May',
      'June',
      'July',
      'August',
      'September',
      'October',
      'November',
      'December',
      'January',
      'February',
      'March',
      'April',
    ],
    datasets: [
      {
        label: '',
        backgroundColor: 'rgba(153,102,255,0.4)',
        data: [120, 140, 160, 200, 150, 170, 180, 190, 170, 220, 230, 230],
      },
      {
        label: '',
        borderColor: 'rgba(75,192,192,0.4)',
        borderDash: [5, 5],
        data: [null, null, null, null, null, null, null, null, null, null, null, 230, 230, 230, 240, 250],
      },
    ],
  },
  averageDay: 5,
  averageWeek: 42,
  averageMonth: 157,
}
