import { computed, ComputedRef, ref } from 'vue'
import { useChartColors } from './useChartColors'
import { TChartData } from '../../types'

export function useChartData<T extends TChartData>(data:  T, alfa?: number): ComputedRef<T> {
  const datasetsColors = data.datasets.map((dataset) => dataset.backgroundColor as string)

  const datasetsThemesColors = datasetsColors.map(
    (colors) => useChartColors(colors, alfa)[alfa ? 'generatedHSLAColors' : 'generatedColors'],
  )

  return computed(() => {
    const datasets = data.datasets.map((dataset, idx) => ({
      ...dataset,
      backgroundColor: datasetsThemesColors[idx].value,
    }))

    return { ...data, datasets } as T
  })
}

export function useChartData2<T extends TChartData>(ref_data: ComputedRef<T>, alfa?: number): ComputedRef<T> {
  return computed(() => {
    const data = ref_data.value


    const datasetsColors = ['rgba(153,102,255,0.4)', 'rgba(75,192,192,0.4)']

    // Creiamo l'oggetto datasetsThemesColors con i colori statici
    const datasetsThemesColors = datasetsColors.map((color) =>
      ref(color) // Ogni colore viene trasformato in un Ref
    )

    const datasets = data.datasets.map((dataset, idx) => ({
      ...dataset,
      backgroundColor: datasetsThemesColors[idx].value,
    }))

    console.log('useChartData2', { ...data, datasets })
    return { ...data, datasets } as T
  })
}
