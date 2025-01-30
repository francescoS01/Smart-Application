import Interceptor from './interceptor'

const ServiceHTTP = {
  login(user: string, password: string): Promise<string> {
    return Interceptor.post<string>('/user/login', {}, {
      headers: {
        username: user,
        password: password
      }
    }).then((response) => {
      const token = response as unknown as string;
      if (token) {
        localStorage.setItem('authToken', token);
      }
      else{
        console.error('Error fetching token:', response);
      }
      return token;
    });
  },



  getKPI(): Promise<KPI[]> {
    return Interceptor.get('/KPI')
  },
  getMachines(KPI_id: string): Promise<GetMachines_response> {
    return Interceptor.get(`/KPI/${KPI_id}/machines`)
  },
  getMachineKPIValues(KPI_id: string, machineID: number, period: "Week"|"Month"|"Year"): Promise<GetMachineKPIValues_response> {
    let startDate = '2024-09-23';
    const endDate = '2024-09-30';
  
    switch (period) {
      case 'Week':
        startDate = '2024-09-23';
        break;
      case 'Month':
        startDate = '2024-09-01';
        break;
      case 'Year':
        startDate = '2024-01-01';
        break;
      default:
        throw new Error('Invalid period specified');
    }
    return Interceptor.get(`/KPI/${KPI_id}/${machineID}/values`, {
      headers: {
        startDate: startDate,
        endDate: endDate,
        Accept: 'application/json',
        aggregationOp: 'avg',
        aggregationInterval: 'day',
      },
    });
  },

  getMachineKPIValues_period(KPI_id: string, machineID: number, period: "Day"|"Week"|"Month"): Promise<KpiValues> {
    const startDate = '2024-01-01';
    let endDate = '2024-09-30';
    let aggregationInterval: 'day'|'week'|'month' = 'day';
  
    switch (period) {
      case 'Day':
        aggregationInterval = 'day';
        break;
      case 'Week':
        aggregationInterval = 'week';
        break;
      case 'Month':
        aggregationInterval = 'month';
        break;
      default:
        throw new Error('Invalid period specified');
    }

    return Interceptor.get(`/KPI/${KPI_id}/${machineID}/values`, {
      headers: {
        startDate: startDate,
        endDate: endDate,
        Accept: 'application/json',
        aggregationOp: 'avg',
        aggregationInterval: aggregationInterval,
      },
    }).then((response) => {
      const transformedData = response.values[0];
      return transformedData;
    })
    .catch((error) => {
      console.error('Error fetching KPI values:', error);
      throw error;
    });
  },

  getAlert(period: 'Today' | 'Week' | 'Month'): Promise<Alert[]> {
    const startDate = '2024-09-30';
    let endDate = '29/09/2024';
  
    switch (period) {
      case 'Today':
        endDate = '29/09/2024';
        break;
      case 'Week':
        endDate = '2024-09-23';
        break;
      case 'Month':
        endDate = '2024-09-01';
        break;
      default:
        throw new Error('Invalid period specified');
    }
  
    return Interceptor.get('/alert', {
      headers: {
        startDate: startDate,
        endDate: endDate,
      },
    });
  },
  

  userQuery(query: string): Promise<UserQuery_response> {
    return Interceptor.post('/ai-query', {}, {
      headers: {
        query: query
      }
    })
  },
}

export default ServiceHTTP


// -----------------------------------------------------------------
export interface KPI {
  unit: string //(es. h, kw\h, kg, ...)
  nameID: string,
  description: string,
  formula: string,
  category: "Cost Management" | "Energy and Environmental Impact" | "Overall Performance"
}
export interface KpiValues {
  startDate: string,   // es: "2024-10-14"
  endDate: string,     // es: "2024-10-19"
  value: number
}

export interface Alert {
  id: number,
  kpi: string,
  machineID: number,
  timestamp: string
  alertDescription: string,
  severity: "LOW" | "MEDIUM" | "HIGH",
}
// -----------------------------------------------------------------

// ENDPOINT ---------------------------------
// URL: /kpi
export type GetKPI_response = KPI[]

// URL: /KPI/:KPIID/machines
export interface GetMachines_response {
  names: string[];
  ids: number[];
}

// URL: /KPI/:KPIID/machineKPIValues
export interface GetMachineKPIValues_response {
  values: KpiValues[];
  code: number;
  errorMessage: string;
  unit: string
}

// URL: /alert
export type GetAlert_response = Alert[]

// URL /ai-query
export type UserQuery_response = {
  type: 'textual' | 'dashboard' | 'report',
  text: string | null,
  dashboard: { 
    x_axis_name: string,  // Name of the X-axis
    y_axis_name: string,  // Name of the Y-axis
    values: any[]  // List of values
  } | null,
  report: any | null
}