import axios from 'axios'
import { useToast } from 'vuestic-ui'

const Interceptor = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
  })
  
const { init } = useToast()

// Intercettore per aggiungere il Bearer Token prima di ogni richiesta
Interceptor.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken')
    if (token) {
      config.headers.Authorization = `${token}`
    }
    return config
  },
  (error) => {
    console.error('Errore richiesta:', error)
    return Promise.reject(error)
  }
)

// Intercettori per gestire le risposte
Interceptor.interceptors.response.use(
  (response) => {
    return response.data as any
  },
  (error) => {
    console.error('Errore API:', error)
    init({ message: "Errore durante la richiesta", color: 'error' })
    return Promise.reject(error)
  },
)

export default Interceptor
