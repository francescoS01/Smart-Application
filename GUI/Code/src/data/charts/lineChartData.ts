import { TLineChartData } from '../types'

export const lineChartData: TLineChartData = {
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
  ],
  datasets: [
    {
      label: 'Monthly Earnings',
      backgroundColor: 'rgba(75,192,192,0.4)',
      data: [10, 35, 140, 70, 50, 40, 75, 55, 30, 51, 25, 100], // Random values
    },
  ],
}

// TIME KPI DATA
export const timeKPIData: TLineChartData = {
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
      label: 'Working Time',
      backgroundColor: 'rgba(75,192,192,0.4)',
      data: [100, 120, 110, 90, 95, 115, 130, 140, 125, 110, 105, 100],
    },
    {
      label: 'Working Time prediction',
      borderColor: 'rgba(75,192,192,0.4)',
      borderDash: [5, 5],
      data: [null, null, null, null, null, null, null, null, null, null, null, 100, 110, 125, 115, 110],
    },
  ],
}

// PRODUCTION KPI DATA
export const productionKPIData: TLineChartData = {
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
      label: 'Cycles',
      backgroundColor: 'rgba(54,162,235,0.4)',
      data: [2000, 2200, 2500, 2400, 2300, 2200, 2400, 2500, 2600, 2700, 2900, 3000],
    },
    {
      label: 'Cycles prediction',
      borderColor: 'rgba(75,192,192,0.4)',
      borderDash: [5, 5],
      data: [null, null, null, null, null, null, null, null, null, null, null, 3000, 3000, 3100, 3000, 3200],
    },
  ],
}

// ENERGY KPI DATA
export const energyKPIData: TLineChartData = {
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
      label: 'Consumption',
      backgroundColor: 'rgba(153,102,255,0.4)',
      data: [120, 140, 160, 180, 150, 170, 180, 190, 200, 220, 230, 230],
    },
    {
      label: 'Consumption prediction',
      borderColor: 'rgba(75,192,192,0.4)',
      borderDash: [5, 5],
      data: [null, null, null, null, null, null, null, null, null, null, null, 230, 230, 230, 240, 250],
    },
  ],
}
