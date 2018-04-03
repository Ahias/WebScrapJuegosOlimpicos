import os
import requests
import csv
import argparse
from datetime import datetime
from datetime import timedelta
from bs4 import BeautifulSoup
import time


##-----------------------------------------------------
##-----------------------------------------------------
##-----------------------------------------------------
##-----------------------------------------------------
##-------Declaracion de funciones----------------------

##--------------------------------------------------###
#funcion para escribir los archivos

#Inicio
def WriteFiles(filePath,List):
    with open(filePath, 'w', newline='') as csvFile:
        writer = csv.writer(csvFile)
        for row in List:
            writer.writerow(row)
#Fin




##--------------------------------------------------###
#funcion para consultar los juegos olimpicos realizados
#Inicio
def GetOlympicGames(url,list,AnnoInicio,AnnoFin):
    response = requests.post(url)
    soup=BeautifulSoup(response.text,"html.parser")
    table = soup.find('table',{'class': 'datagrid_header_table'})
    isFirtsLine=True
    for row in table.findAll("tr"):
        cells = row.findAll('td')
        if(isFirtsLine==False):
            Name=cells[1].find(text=True) 
            Year=int(str(Name).split(" ")[0])
            if((Year>= AnnoInicio) & (Year<= AnnoFin)):                 
                Key=str(Name).split(" ")[0] + "_" + str(Name).split(" ")[1][0:3]
                City=" ".join(  str(Name).split(" ")[2:] )
                FullURL="http://www.theolympicdatabase.nl/" + cells[1].find_all('a')[0]['href']            
                Country=cells[2].find(text=True)
                NewRow=[Key,Name,Country,City,FullURL]
                list.append(NewRow)     
                time.sleep(1)
        else:
            isFirtsLine=False
#Fin



##--------------------------------------------------###
#funcion que consulta los ganadores de medallas por juego olimpico
#Inicio
def GetDetailOlympicGames(url,list,key,BaseURL):

    ##En el detalle del juego olimpico, se muestran 3 opciones para consultar mas detalle
    ##Para nuestro fin, solo estamos interezados en consultar los ganadores
    ParentResponse = requests.post(url)
    ParentSoup=BeautifulSoup(ParentResponse.text,"html.parser")
    ParentTable = ParentSoup.find('table',{'class': 'data_table'})
    ##En esta parte consultamos especificamente el miembro que contiene la URL del detalle de los ganadores
    WinnerURL=BaseURL + ParentTable.findAll("tr")[5].find_all('a')[0]['href'] 

    ##Navegando con los ganadores
    WinnerResponse = requests.post(WinnerURL)
    WinnerSoup=BeautifulSoup(WinnerResponse.text,"html.parser")
    WinnerTable = WinnerSoup.find('table',{'class': 'datagrid_header_table'})    

    isFirtsLine=True
    for row in WinnerTable.findAll("tr"):
        cells = row.findAll('td')
        if(isFirtsLine==False):
            #HeaderDetailOlympicGameList=["Key", "Order", "Winner", "Nationality", "Sport", "Discipline","Medal"]
            Order=cells[0].find(text=True) 
            Winner=cells[1].find(text=True) 
            DetailMedalsURL= BaseURL +  cells[1].find_all('a')[0]['href'] 
            Nationality=cells[2].find_all('a')[0]['title'] 
            
            
            #consulta de medallas
            DetailMedalsResponse = requests.post(DetailMedalsURL)
            DetailMedalsSoup=BeautifulSoup(DetailMedalsResponse.text,"html.parser")
            DetailMedalsTable = DetailMedalsSoup.find('table',{'class': 'datagrid_header_table'})

            isFirtsLine=True

            for RowDetail in DetailMedalsTable.findAll("tr"):
                cellDetail=RowDetail.findAll('td')
                if(isFirtsLine==False):
                    KeyYear=key[0:4]
                    Year=cellDetail[0].find(text=True)
                    if(cellDetail[0].find(text=True) == key[0:4]):
                        Sport = cellDetail[2].find(text=True) 
                        Discipline= cellDetail[3].find(text=True) 
                        Gold=  cellDetail[4].find_all('img')#[0]['src']
                        Silver= cellDetail[5].find_all('img')#[0]['src']
                        Broze= cellDetail[6].find_all('img')#[0]['src']

                        Medal=""
                        if (len(Gold)>0):
                            Medal="Gold"
                        elif (len(Silver)>0):
                            Medal="Silver"
                        elif (len(Broze)>0):
                            Medal="Broze"
           
                        NewRow=[key,Order,Winner,Nationality,Sport,Discipline,Medal]
                        list.append(NewRow)
                        time.sleep(0.500)

                else:
                    isFirtsLine=False           

                   
        else:
            isFirtsLine=False
#Fin

##---------------Fin de funciones----------------------
##-----------------------------------------------------
##-----------------------------------------------------
##-----------------------------------------------------



print("#------------------------------------------------------------------------------#")
print("Debe definir el periodo que desea consultar (Todos los juegos desde 1896 hasta 2008):")
print("")
print("Ingrese el año de inicio:")
AnnoInicio=int(input())
print("Ingrese el año de fin:")
AnnoFin=int(input())



##-----------------------------------------------------
##-----------------------------------------------------
##-----------------------------------------------------
#Consultar lista de juegos olimpicos que se encuentra registrados
#en el sitio de base de datos
print("")

print("#------------------------------------------------------------------------------#")
print ("Generado archivo maestro...")
print("...")
#Current directory where is located the script
CurrentDir = os.path.dirname(__file__)
FileName = str( AnnoInicio) + "_" + str(AnnoFin) + "_Master_Olympic_Games.csv"
FilePath = os.path.join(CurrentDir, FileName)


BaseURL="http://www.theolympicdatabase.nl/"
QueryURL="http://www.theolympicdatabase.nl/olympic/games"
OlympicGameList=[]
HeaderOlympicGameList=["Key","Name","Country","City","URL"]
OlympicGameList.append(HeaderOlympicGameList)

GetOlympicGames(QueryURL,OlympicGameList,AnnoInicio,AnnoFin)
WriteFiles(FilePath,OlympicGameList)

print("")

print("Archivo generado almacenado en el siguiente directorio:" + FilePath)
print("")


##-----------------------------------------------------
##-----------------------------------------------------
##-----------------------------------------------------
#Consultar el detalle de los ganadores de medallas por juego olimpico
print("#------------------------------------------------------------------------------#")
print ("Generado archivo detalle...")
FileName = str( AnnoInicio) + "_" + str(AnnoFin) + "_Detail_Medal.csv"
FilePath = os.path.join(CurrentDir, FileName)
DetailOlympicGameList=[]
HeaderDetailOlympicGameList=["Key", "Order", "Winner", "Nationality", "Sport", "Discipline","Medal"]
DetailOlympicGameList.append(HeaderDetailOlympicGameList)
IsFirtsOlympicGame=True
for row in OlympicGameList:
    if (IsFirtsOlympicGame==False):
        GetDetailOlympicGames(row[4],DetailOlympicGameList,row[0],BaseURL)
    else:
        IsFirtsOlympicGame=False
 
WriteFiles(FilePath,DetailOlympicGameList)
print("")

print("Archivo generado almacenado en el siguiente directorio:" + FilePath)
print("")



