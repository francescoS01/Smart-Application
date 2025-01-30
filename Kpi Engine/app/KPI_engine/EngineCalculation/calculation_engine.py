import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

import numpy as np
from lark import Lark, Transformer
import numexpr as ne
from py_expression_eval import Parser
import json
import datetime

from typing import Union

from Database.Database_interface import DBConnection
from Knowledge_base.knowledge_base_interface import KnowledgeBaseInterface

class CalculationEngine:
    
    """
    @class CalculationEngine
    @brief Descrizione di CalculationEngine

    This class demonstrates detailed documentation for Python.
    """
    #Class that represent a calculator, that can be a complex_KPI or an alert
    class Calculator:
    
        __calculus_parser = Parser()
        
        def __init__(self, name, description, expression, final_type, KPIs, base_functions, complex_KPIs):
            
            self.__name = name
            self.__description = description
            self.__expression = expression
            self.__final_type = final_type
            self.__KPIs = list(KPIs)
            self.__complex_KPIs = list(complex_KPIs)

            self.__base_functions = {Function: lambda x: CalculationEngine._base_functions_dict[Function](x) for Function in base_functions}
            
        def __call__(self, machine: str, start_date: str, end_date: str, aggregation: str) -> Union[float, bool, list[float], list[bool]]:
            
            #Taking information from DB
            KPIs, timestamp_series = DBConnection.retrieve_data_db(machine, self.__KPIs, aggregation, (start_date, end_date))
            
            #Prepare variable for py_expression_eval compiler
            complex_KPIs = {Function: CalculationEngine._complex_KPIs_dict[Function](machine, start_date, end_date)["values"] for Function in self.__complex_KPIs}
            
            #Calculate final value
            Calculation = CalculationEngine.Calculator.__calculus_parser.parse(self.__expression).evaluate(KPIs | complex_KPIs | self.__base_functions)
            
            #Prepare value format
            if(isinstance(Calculation, np.ndarray)): Calculation = Calculation.tolist()
            
            #Return result, with value and temporal range associated
            return {
                "time": None if type(Calculation) != list else  DBConnection.get_time_range(timestamp_series, start_date, end_date),
                "values": Calculation
            }
    
        def segment_calculation(self, machine: int, ranges: tuple[str], aggregation: str) -> list:
            """
            Args:
                machine (str): machine identification
                ranges (tuple[str]): more couples of time range

            Returns:
                value
                
            It is expected that expression return a value and ranges are sorted
            """
            
            #print("aggregation ", aggregation)
            
            if(not KnowledgeBaseInterface.check_kpi_availability(machine, self.__KPIs)): raise ValueError(f"for machine {machine}, not all KPIs are aviable")
            
            Finish = datetime.datetime.strptime(ranges[-1][1], "%Y-%m-%d %H:%M:%S").date() + datetime.timedelta(days = 1)
            KPIs, timestamp_series = DBConnection.retrieve_data_db(machine, self.__KPIs, aggregation, (ranges[0][0], Finish.strftime("%Y-%m-%d %H:%M:%S")))
            
            #print(datetime.datetime.strptime(start, "%Y-%m-%d %H:%M:%S").date())
            
            new_ranges = [[datetime.datetime.strptime(start, "%Y-%m-%d %H:%M:%S").date(), datetime.datetime.strptime(end, "%Y-%m-%d %H:%M:%S").date()] for start, end in ranges]
            timestamp_series_date = [datetime.datetime.strptime(i, "%Y-%m-%d %H:%M:%S").date() for i in timestamp_series]
            
            print(f"TIME SERIES DATE: {timestamp_series_date}")
            
            #Find appropriate indexes for segmentation
            i = 0
            r = 0
            
            Indexes = []
            
            Inside = False
            
            First = None
            
            while(i < len(timestamp_series_date) and r < len(ranges)*2):
                
                if(new_ranges[r//2][r%2] <= timestamp_series_date[i]):
                    if(Inside):
                        if(new_ranges[r//2][r%2] == timestamp_series_date[i]): Indexes.append((First, i))
                        if(new_ranges[r//2][r%2] < timestamp_series_date[i]): Indexes.append((First, i-1))
                        
                    else: First = i
                        
                    Inside = not Inside
                    
                    r += 1
                
                else: i += 1
                
            if(Inside): Indexes.append((First, i-1))
            
            print(Indexes)

            Result = dict()
            Result["range"] = []
            Result["value"] = []
            
            for start, end in Indexes:
                
                base_KPIs = dict()
                
                Null = False
                
                #print(KPIs.keys())
                
                for base_kpi in KPIs.keys():
                    
                    Extraction = KPIs[base_kpi][start: end] if(start != end) else np.array([KPIs[base_kpi][start]])
                    if(None in Extraction):
                        #print(f"None in {base_kpi}")
                        Null = True
                        break
                    
                    base_KPIs[base_kpi] = Extraction
                
                if(Null): Calculation = []
                
                else:
                    
                    #print(start, end)
                    
                    complex_KPIs = {Function: CalculationEngine._complex_KPIs_dict[Function](machine, timestamp_series(start), timestamp_series(end))["values"] for Function in self.__complex_KPIs}

                    try: Calculation = CalculationEngine.Calculator.__calculus_parser.parse(self.__expression).evaluate(self.__base_functions | base_KPIs | complex_KPIs)
                    except TypeError: Calculation = []
                
                Result["range"].append((timestamp_series[start], timestamp_series[end]))
                Result["value"].append(Calculation)
                
            return Result

        def get_name(self) -> str:
            return self.__name
        
        def get_description(self) -> str:
            return self.__description
        
        def get_expression(self) -> str:
            return self.__expression
        
        def get_KPIs(self) -> list[str]:
            return list(self.__KPIs)
        
        def get_complex_KPIs(self):
            return list(self.__complex_KPIs)
        
        def get_result_type(self) -> type:
            return self.__final_type
        
        def get_base_functions(self) -> list[str]:
            return list(self.__base_functions.keys())
        
    #Dictionary of all base functions
    _base_functions_dict = {
        "max": lambda x: max(x),
        "min": lambda x: min(x),
        "sum": lambda x: sum(x),
        "avg": lambda x: np.mean(x),
        "var": lambda x: np.var(x),
    }

    _complex_KPIs_dict = dict()  #Dict of all complex KPIs created
    __alert_dict = dict()        #Dict of all alerts created
    
    _total_calculators = dict()    #Dict of all calculators
    
    #Update parsing (for everytime some alert or complex KPIs are added or removed)
    def _update_parser() -> None:
        
        #Update total calculators
        CalculationEngine._total_calculators = CalculationEngine._complex_KPIs_dict | CalculationEngine.__alert_dict
        
        #Prepare string for parser
        base_functions_dict_prepare = f"/{'/ | /'.join([base_fun for base_fun in CalculationEngine._base_functions_dict.keys()])}/"
        calculators_prepare = f"/{'/ | /'.join([fun for fun in CalculationEngine._total_calculators.keys()])}/"
        
        #Updare parser
        CalculationEngine.__parser = Lark( f"""                         
                %import common.NUMBER
                %import common.WS
                %ignore WS
                    
                ?start: l0                  -> base

                ?l0: l1 "<" l1              -> le
                | l1 ">" l1                 -> ge
                | l1 "=" l1                 -> eq
                | l1 "!=" l1                -> neq
                | l1 ">=" l1                -> leq
                | l1 "<=" l1                -> geq
                | l1                        -> base

                ?l1: l1 "+" l2              -> add
                | l1 "-" l2                 -> sub
                | l2                        -> base

                ?l2: l2 "*" l3              -> mul
                | l2 "/" l3                 -> div
                | l3                        -> base

                ?l3: "-" l3                 -> inverse_sign
                | "(" l1 ")"                -> brackets
                | base_function "(" l1 ")"  -> apply_base_function
                | l3 "^" l1                 -> pow
                | calculators               -> apply_calculators
                | kpi_name                  -> kpi
                | NUMBER                    -> number 
                
                base_function:     {base_functions_dict_prepare}
                kpi_name:          /[a-z_]+/
                calculators:       {calculators_prepare}
                
                """,
                
            start="start")
    
    #Filter aviable base KPI names
    def __filter_available_KPIs(KPIs_list: list[str]) -> list[str]:
        available_kpis = KnowledgeBaseInterface.get_base_kpis()
        return [kpi for kpi in KPIs_list if kpi in available_kpis]
    
    #Filter aviable base function names
    def __filter_available_base_functions_dict(base_functions_list:list[str]) -> list[str]:
        base_functions = [i for i in CalculationEngine._base_functions_dict.keys()]
        return list(filter(lambda x: x in base_functions, base_functions_list))
    
    #Filter aviable calculator names
    def __filter_available_complex_KPIs(calculators_list: list[str]) -> list[str]:
        calculators = [i for i in CalculationEngine._total_calculators.keys()]
        return list(filter(lambda x: x in calculators, calculators_list))
    
    #Get a new creation
    def __get_new_creation(name, description: str, expression: str, Type: type) -> Calculator:
        
        #Deviate calculus between adding function and alert situation
        if(float in Type and list in Type):
            dict = CalculationEngine._complex_KPIs_dict
            first_message = f"bool value, not a scalar or list"
            
        if(bool in Type):
            dict = CalculationEngine.__alert_dict
            first_message = f"scalar or list value, not a bool"
            
        expression = CalculationEngine.__prepare_formula_base_kpi(expression)
        
        #Compile
        try: parsing_tree = CalculationEngine.__parser.parse(expression)
        except Exception as e: raise SyntaxError(f"Compiler is stopped here: {expression[:e.pos_in_stream+1]}<<<")
        
        #Extract the information about expression
        try: result_checking = CalculationEngine.GeneralChecking().transform(parsing_tree)
        except Exception as e: raise TypeError(e.orig_exc)
        
        #Check if type of expression is equals to excepted type
        if(result_checking["type"] not in Type): raise TypeError(f"This expression {expression} gives a {first_message}")
        
        #Check if this calculator doesn't call itself
        if(name in result_checking["calculators"]): raise ValueError(f"This creation cannot call itself")
        
        #Check if every base KPI is aviable
        #check_KPIs_aviable = CalculationEngine.__filter_available_KPIs(result_checking["KPIs"])
        #if(len(check_KPIs_aviable) != len(result_checking["KPIs"])): raise SyntaxError(f"The simply KPIs {', '.join(list(set(result_checking['KPIs']).difference(set(check_KPIs_aviable))))} are not aviables")

        #Check if every base function is aviable
        check_base_functions_aviable = CalculationEngine.__filter_available_base_functions_dict(result_checking["base_functions"])
        if(len(check_base_functions_aviable) != len(result_checking["base_functions"])): raise ValueError(f"The base functions {', '.join(list(set(result_checking['base_functions']).difference(set(check_base_functions_aviable))))} are not aviables")
        
        #Check if every complex KPI is aviable
        check_complex_KPIs_aviable = CalculationEngine.__filter_available_complex_KPIs(result_checking["calculators"])
        if(len(check_complex_KPIs_aviable) != len(result_checking["calculators"])): raise ValueError(f"The complex KPIs {', '.join(list(set(result_checking['calculators']).difference(set(check_complex_KPIs_aviable))))} are not aviables")
        
        return dict, CalculationEngine.Calculator(name, description, expression, result_checking["type"], result_checking["KPIs"], check_base_functions_aviable, check_complex_KPIs_aviable)
        
    #Add calculator
    def __add_calculator(name, description: str, expression: str, Type: type) -> bool:
        
        #Deviate calculus between adding function and alert situation
        if(float in Type and list in Type and name in CalculationEngine._complex_KPIs_dict.keys() or
           bool in Type and name in CalculationEngine.__alert_dict.keys()): return False
        
        name_dict, Creation = CalculationEngine.__get_new_creation(name, description, expression, Type)
        
        #Add the calculator to the dictionary
        name_dict[name] = Creation
        
        return True
    
    def __prepare_formula_base_kpi(expression):
        
        complex_KPIs = KnowledgeBaseInterface.get_complex_kpis()
        
        complex_KPIs = {kpi["nameID"]: kpi["formula"] for kpi in complex_KPIs}
        
        original_string = None
        
        while(original_string != expression):
            
            original_string = str(expression)
        
            for kpi in complex_KPIs.keys():
                expression = expression.replace(kpi, complex_KPIs[kpi])
        
        return expression
    
    #@class per descrivere la classe.
    #@param per descrivere i parametri del metodo.
    #@return per descrivere il valore restituito.
    #@brief per una descrizione breve.
    def direct_calculation_KPI(machine: int, formula: str, start_date: str, end_date: str, aggregation: str) -> Union[float, list[float]]:
        """
        @param: machine, formula, temporal range (start_date, end_date)
        Compile, check and calculate complex KPI
        
        @return: value of complex KPI
        """
        return CalculationEngine.__get_new_creation("", "", formula, [float, list])[1](machine, start_date, end_date, aggregation)
    
    def direct_calculation_alert(machine: int, formula: str, start_date: str, end_date: str, aggregation: str) -> Union[float, list[float]]:
        """
        @param: machine, formula, temporal range (start_date, end_date)
        Compile, check and calculate alert
        
        @return: value of alert
        """
        return CalculationEngine.__get_new_creation("", "", formula, [bool])[1](machine, start_date, end_date, aggregation)
    
    def direct_segmented_calculation_KPI(machine: int, formula: str, ranges: tuple[str], aggregation) -> Union[float, list[float]]:
        """
        @param: machine, formula, temporal range (start_date, end_date)
        Compile, check and calculate complex KPI
        
        @return: value of complex KPI
        """
        return CalculationEngine.__get_new_creation("", "", formula, [float, list])[1].segment_calculation(machine, ranges, aggregation)
    
    def direct_segmented_calculation_alert(machine: int, formula: str, ranges: tuple[str], aggregation: str) -> Union[float, list[float]]:
        """
        @param: machine, formula, temporal range (start_date, end_date)
        Compile, check and calculate alert
        
        @return: value of alert
        """
        return CalculationEngine.__get_new_creation("", "", formula, [bool])[1].segment_calculation(machine, ranges, aggregation)
    
    def add_complex_KPI(name: str, description: str, expression: str) -> bool:
        if(name in CalculationEngine._complex_KPIs_dict.keys()): return False
        CalculationEngine.__add_calculator(name, description, expression, [float, list])
        CalculationEngine._update_parser()
        return True
    
    def remove_complex_KPI(name: str) -> bool:
        if(name not in CalculationEngine._complex_KPIs_dict.keys()): return False
        del CalculationEngine._complex_KPIs_dict[name]
        CalculationEngine._update_parser()
        return True
    
    def get_complex_KPI(name: str) -> Union[None, Calculator]:
        try: return CalculationEngine._complex_KPIs_dict[name]
        except: return None
    
    def add_alert(name: str, description: str, expression: str) -> bool:
        return CalculationEngine.__add_calculator(name, description, expression, [bool])
    
    def remove_alert(name: str) -> bool: 
        if(name not in CalculationEngine.__alert_dict.keys()): return False
        del CalculationEngine.__alert_dict[name]  
        return True
    
    def get_alert(name: str) -> Union[None, Calculator]:
        try: return CalculationEngine.__alert_dict[name]
        except: return None
        
    def get_alert_names() -> list[str]:
        return [i for i in CalculationEngine.__alert_dict.keys()]
    
    def get_complex_KPI_names() -> list[str]:
        return [i for i in CalculationEngine._complex_KPIs_dict.keys()]
    
    #Save a copy, to a json file, where every complex_KPI and alerts are saved inside the engine
    def save_state(path = "") -> None:
        
        states = dict()
        
        states["complex_KPIs"] = [[x.get_name(), x.get_description(), x.get_expression(), x.get_result_type().__name__, x.get_KPIs(), x.get_base_functions(), x.get_complex_KPIs()] for x in CalculationEngine._complex_KPIs_dict.values()]
        states["Alerts"] =       [[x.get_name(), x.get_description(), x.get_expression(), x.get_result_type().__name__, x.get_KPIs(), x.get_base_functions(), x.get_complex_KPIs()] for x in CalculationEngine.__alert_dict.values()]

        if(path == ""): path = "kpi_engine_state.json"
        else:           path = f"{path}\\kpi_engine_state.json"
        
        json.dump(states, open(path, "w"), indent = 4)
    
    #Load a json file, where every complex_KPI and alerts are saved and these complex_KPIs / alerts must be load inside the engine   
    def load_state(path = "") -> None:
        
        if(path == ""): path = "kpi_engine_state.json"
        else:           path = f"{path}\\kpi_engine_state.json"
        
        states = json.load(open(path, "r"))
        
        #Check if every base function are in calculation engine   
        for state in states["complex_KPIs"] + states["Alerts"]:
            
            #Check base_function aviable
            if(len(set(state[6]).difference(set(CalculationEngine._complex_KPIs_dict.keys()))) > 0): raise ValueError("This state is not compatible with this engine (base functions presence in the state errors)")
        
        CalculationEngine._complex_KPIs_dict.clear()
        CalculationEngine.__alert_dict.clear()
        
        types_map = {
            "float": float,
            "list": list,
            "bool": bool
        }
        
        for name, description, expr, type_result, KPIs, base_functions, complex_KPIs in states["complex_KPIs"]:
            CalculationEngine._complex_KPIs_dict[name] = CalculationEngine.Calculator(name, description, expr, types_map[type_result],
                                                                                      KPIs, base_functions, complex_KPIs)
        
        for name, description, expr, type_result, KPIs, base_functions, complex_KPIs in states["Alerts"]:
            CalculationEngine.__alert_dict[name] = CalculationEngine.Calculator(name, description, expr, types_map[type_result],
                                                                                      KPIs, base_functions, complex_KPIs)
    
    #Every node pass a dict with: own type, all sub kpi name, all sub functions
    #Type float represents scalar and series (for conventional choice)
    class GeneralChecking(Transformer):

        def base(self, args: dict) -> dict:
            return args[0]
        
        def __base_operation(self, args: dict, Type: type) -> dict:
 
            return {
                "type": Type,
                "KPIs": args[0]["KPIs"] + args[1]["KPIs"],
                "base_functions": args[0]["base_functions"] + args[1]["base_functions"],
                "calculators": args[0]["calculators"] + args[1]["calculators"],
                "Zero": False
            }
              
        def le(self, args: dict) -> dict:
            return self.__base_operation(args, bool)
            
        def ge(self, args: dict) -> dict:
            return self.__base_operation(args, bool)
            
        def eq(self, args: dict) -> dict:
            return self.__base_operation(args, bool)
            
        def neq(self, args: dict) -> dict:
            return self.__base_operation(args, bool)
            
        def leq(self, args: dict) -> dict:
            return self.__base_operation(args, bool)
            
        def geq(self, args: dict) -> dict:
            return self.__base_operation(args, bool)        

        def add(self, args: dict) -> dict:
            return self.__base_operation(args, float)

        def sub(self, args: dict) -> dict:
            return self.__base_operation(args, float)

        def mul(self, args: dict) -> dict:
            return self.__base_operation(args, float)

        def div(self, args: dict) -> dict:
            if(args[1]["Zero"]): raise TypeError("You cannot do a division by 0") 
            return self.__base_operation(args, float)

        def pow(self, args: dict) -> dict:
            return self.__base_operation(args, float)

        def inverse_sign(self, args: dict) -> dict:
            return args[0]

        def kpi(self, args: dict) -> dict:
            
            return {
                "type": list,
                "KPIs": [args[0].children[0].value],
                "base_functions": [],
                "calculators": [],
                "Zero": False
            }

        def number(self, args: dict) -> dict:
            
            return {
                "type": float,
                "KPIs": [],
                "base_functions": [],
                "calculators": [],
                "Zero": float(args[0].value) == 0
                }
                         
        def apply_base_function(self, args: dict) -> dict:
            
            return {
                "type": float,
                "KPIs": args[1]["KPIs"],
                "base_functions": args[1]["base_functions"] + [args[0].children[0].value],
                "calculators": args[1]["calculators"],
                "Zero": False
            }
            
        def apply_calculators(self, args: dict) -> dict:
            
            return {
                "type": CalculationEngine._complex_KPIs_dict[args[0].children[0].value].get_result_type(),
                "KPIs": [],
                "base_functions": [],
                "calculators": [args[0].children[0].value],
                "Zero": False
            }
            
        def brackets(self, args: dict) -> dict:
            return args[0]

#Prepare compiler for engine KPI
CalculationEngine._update_parser()

#Ranges = [('2024-05-01 00:00:00', '2024-05-05 00:00:00'), ('2024-05-06 00:00:00', '2024-05-12 00:00:00'), ('2024-05-13 00:00:00', '2024-05-19 00:00:00'), ('2024-05-20 00:00:00', '2024-05-26 00:00:00'), ('2024-05-27 00:00:00', '2024-06-02 00:00:00'), ('2024-06-03 00:00:00', '2024-06-09 00:00:00'), ('2024-06-10 00:00:00', '2024-06-16 00:00:00'), ('2024-06-17 00:00:00', '2024-06-23 00:00:00'),
           #('2024-06-24 00:00:00', '2024-06-30 00:00:00'), ('2024-07-01 00:00:00', '2024-07-07 00:00:00'), ('2024-07-08 00:00:00', '2024-07-14 00:00:00'), ('2024-07-15 00:00:00', '2024-07-21 00:00:00'), ('2024-07-22 00:00:00', '2024-07-28 00:00:00'), ('2024-07-29 00:00:00', '2024-08-04 00:00:00'), ('2024-08-05 00:00:00', '2024-08-11 00:00:00'), ('2024-08-12 00:00:00', '2024-08-18 00:00:00'), ('2024-08-19 00:00:00', '2024-08-25 00:00:00'),
           #('2024-08-26 00:00:00', '2024-09-01 00:00:00'), ('2024-09-02 00:00:00', '2024-09-08 00:00:00'), ('2024-09-09 00:00:00', '2024-09-15 00:00:00'), ('2024-09-16 00:00:00', '2024-09-22 00:00:00'), ('2024-09-23 00:00:00', '2024-09-29 00:00:00'), ('2024-09-30 00:00:00', '2024-10-06 00:00:00'), ('2024-10-07 00:00:00', '2024-10-13 00:00:00'), ('2024-10-14 00:00:00', '2024-10-20 00:00:00'), ('2024-10-21 00:00:00', '2024-10-27 00:00:00'),
           #('2024-10-28 00:00:00', '2024-11-03 00:00:00'), ('2024-11-04 00:00:00', '2024-11-10 00:00:00'), ('2024-11-11 00:00:00', '2024-11-17 00:00:00'), ('2024-11-18 00:00:00', '2024-11-24 00:00:00'), ('2024-11-25 00:00:00', '2024-12-01 00:00:00'), ('2024-12-02 00:00:00', '2024-12-08 00:00:00'), ('2024-12-09 00:00:00', '2024-12-15 00:00:00'), ('2024-12-16 00:00:00', '2024-12-22 00:00:00'), ('2024-12-23 00:00:00', '2024-12-29 00:00:00'), ('2024-12-30 00:00:00', '2024-12-30 00:00:00')]


#CalculationEngine.add_complex_KPI("idle_time_percentage", "", "(idle_time / (working_time + idle_time + offline_time)) * 100")

#Result = CalculationEngine.direct_segmented_calculation_KPI(2, "idle_time_percentage", Ranges, "sum")
#print("TESTING RICCARDO ENGINE")
#print("RICCARDO RESULTS", Result)

""" Ranges = [
    ('2024-05-01 00:00:00', '2024-07-30 00:00:00')
    ]

print("ENGINE RANGES", Ranges)
Result = CalculationEngine.direct_segmented_calculation_KPI(2, "cycles", Ranges, 'sum')
print("ENGINE RESULTS", Result) """