import json
from pprint import pprint
def load_json_file(filename):
    with open(filename) as outfile:
        data = json.load(outfile)
    return   liontravel_air_tickets_data  


def find_air_ticket_info():
    filename = 'liontravel_Air_tickets_Data.txt'  
    liontravel_air_tickets_data  =  load_json_file(filename)
    air_info_keys_list = ['ReturnData','AirlineInfo','AirportInfo','FareInfo']  
    air_tickets_info = liontravel_air_tickets_data[air_info_keys_list[0]][air_info_keys_list[-1]]
    air_tickets_keys_list = ['ItinerarySummary','StopAirport','SellCurrCode','TotalBaseFare','TotalFare','TotalTax','ValidatingAirline']
    air_tickets_Itinerary_keys = ['ArriveAirport','ArriveDate','DepartAirport','DepartDate','SellSeat',
    tickets_Info_Dict = {}
    Depart_tickets_Dict = {}
    Arrive_tickets_Dict = {}
    for i in range(len(air_tickets_info)):
            tickets_Data__ItinerarySummary_Info = air_tickets_info[i][air_tickets_keys_list[0]]
            Depart_tickets_Data = air_tickets_info[i][air_tickets_keys_list[0]][0][0]
            Arrive_tickets_Data = air_tickets_info[i][air_tickets_keys_list[0]][1][0]
            Depart_tickets_Dict[Depart_tickets_Data[air_tickets_Itinerary_keys[2]]] ={'ArriveAirport':Depart_tickets_Data[air_tickets_Itinerary_keys[0]],
            'ArriveDate':Depart_tickets_Data[air_tickets_Itinerary_keys[1]],
            'DepartAirport':Depart_tickets_Data[air_tickets_Itinerary_keys[2]],
            'DepartDate':Depart_tickets_Data[air_tickets_Itinerary_keys[3]],
            'SellSeat':int(list(Depart_tickets_Data[air_tickets_Itinerary_keys[4]].values())[0]),
            'TotalFare':air_tickets_info[i][air_tickets_keys_list[4]]
            }
            Arrive_tickets_Dict[Arrive_tickets_Data[air_tickets_Itinerary_keys[2]]] ={
            'ArriveAirport':Arrive_tickets_Data[air_tickets_Itinerary_keys[0]],
            'ArriveDate':Arrive_tickets_Data[air_tickets_Itinerary_keys[1]],
            'DepartAirport':Arrive_tickets_Data[air_tickets_Itinerary_keys[2]],
            'DepartDate':Arrive_tickets_Data[air_tickets_Itinerary_keys[3]],
            'SellSeat':int(list(Arrive_tickets_Data[air_tickets_Itinerary_keys[4]].values())[0]),
            'TotalFare':air_tickets_info[i][air_tickets_keys_list[4]]
            }
            tickets_Info_Dict{i} = {"Depart_tickets":dict(Depart_tickets_Dict),"Arrive_tickets":dict(Arrive_tickets_Dict)}
    return tickets_Info_Dict            