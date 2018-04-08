import os
import requests
import csv
import argparse
import datetime
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
        return 0
   
#Fin




##--------------------------------------------------###
#funcion para consultar los juegos olimpicos realizados
#Inicio
def GetOlympicGames(url,list,AnnoInicio,AnnoFin,BaseURL):
    response = requests.post(url)
    soup=BeautifulSoup(response.text,"html.parser")
    table = soup.find('table',{'class': 'datagrid_header_table'})
    isFirtsLine=True
    for row in table.findAll("tr"):
        cells = row.findAll('td')
        if(isFirtsLine==False):
            ##["YearOlympic","OlympicName","OlympicCountry","OlympicCity","URL"]
            OlympicName=cells[1].find(text=True) 
            YearOlympic=int(str(OlympicName).split(" ")[0])
            if((YearOlympic>= AnnoInicio) & (YearOlympic<= AnnoFin)):                   
                OlympicCity=" ".join(  str(OlympicName).split(" ")[2:] )
                URL=BaseURL + cells[1].find_all('a')[0]['href']            
                OlympicCountry=cells[2].find(text=True)
                NewRow=[YearOlympic,OlympicName,OlympicCountry,OlympicCity,URL]
                list.append(NewRow)    
        else:
            isFirtsLine=False
    return 0
#Fin



##--------------------------------------------------###
#funcion que consulta los ganadores de medallas por juego olimpico
#Inicio
def GetDetailOlympicGames(Parent,list,BaseURL):

    ##En el detalle del juego olimpico, se muestran 3 opciones para consultar mas detalle
    ##Para nuestro fin, solo estamos interezados en consultar los ganadores
    ParentResponse = requests.post(Parent[4])
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
            time.sleep(0.300)           

          

            #["YearOlympic","OlympicName","OlympicCountry","OlympicCity","WinnerName", "WinnerNationality","WinnerDateBirth","WinnerGender", "Sport", "Discipline","Medal"]

            ##Informacion del juego olimpico
            YearOlympic=Parent[0]
            OlympicName=Parent[1]
            OlympicCountry=Parent[2]
            OlympicCity=Parent[3]

            ##Informacion del ganador
            WinnerName=cells[1].find(text=True) 
            WinnerNationality=cells[2].find_all('a')[0]['title']    
            DetailMedalsURL= BaseURL +  cells[1].find_all('a')[0]['href']   
            DetailMedalsResponse = requests.post(DetailMedalsURL)
            DetailMedalsSoup=BeautifulSoup(DetailMedalsResponse.text,"html.parser")
           
            #Valor no definido           
            WinnerGender="NULL"
            #No todos los detalles de los ganadores contiene toda la informacion
            try:
                WinnerGender=DetailMedalsSoup.findAll('table',{'class': 'data_table'})[0].findAll("tr")[1].findAll("td")[2].text
            except:
                WinnerGender="NULL"        

            #Informacion de medallas
            DetailMedalsTable = DetailMedalsSoup.find('table',{'class': 'datagrid_header_table'})
            isFirtsLine=True
            
            #En algunos caso no existen informacion del detalle de las medallas
            try:
                for RowDetail in DetailMedalsTable.findAll("tr"):
                    cellDetail=RowDetail.findAll('td')
                    if(isFirtsLine==False):
                        YearMedal=cellDetail[0].find(text=True)
                        if(int(YearMedal) == YearOlympic):
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
           
                            NewRow=[YearOlympic,OlympicName,OlympicCountry,OlympicCity,WinnerName, WinnerNationality,WinnerGender, Sport, Discipline,Medal]
                            list.append(NewRow)           

                    else:
                        isFirtsLine=False  
            except:
                isFirtsLine=False   

                   
        else:
            isFirtsLine=False
    return 0
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



try:
    print("#------------------------------------------------------------------------------#")
    print ("Generado archivo...")
    print("...")

    print("Inicio del proceso:" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))

    BaseURL="http://www.theolympicdatabase.nl/"
    QueryURL=BaseURL + "olympic/games"
    OlympicGameList=[]
    HeaderOlympicGameList=["YearOlympic","OlympicName","OlympicCountry","OlympicCity","URL"]
    OlympicGameList.append(HeaderOlympicGameList)




    GetOlympicGames(QueryURL,OlympicGameList,AnnoInicio,AnnoFin,BaseURL)

    ##-----------------------------------------------------
    ##-----------------------------------------------------
    ##-----------------------------------------------------
    #Consultar el detalle de los ganadores de medallas por juego olimpico
    #Current directory where is located the script
    CurrentDir = os.path.dirname(__file__)
    FileName = str( AnnoInicio) + "_" + str(AnnoFin) + "_OlympicGame_Medal.csv"
    FilePath = os.path.join(CurrentDir, FileName)
    DetailOlympicGameList=[]
    HeaderDetailOlympicGameList=["YearOlympic","OlympicName","OlympicCountry","OlympicCity","WinnerName", "WinnerNationality","WinnerGender", "Sport", "Discipline","Medal"]
    DetailOlympicGameList.append(HeaderDetailOlympicGameList)
    IsFirtsOlympicGame=True


    for row in OlympicGameList:
        if (IsFirtsOlympicGame==False):
            GetDetailOlympicGames(row,DetailOlympicGameList,BaseURL)
        else:
            IsFirtsOlympicGame=False
 
    WriteFiles(FilePath,DetailOlympicGameList)



    print("Fin del proceso:" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
    print("Juegos olímpicos encontrados:" + str(len(OlympicGameList)-1))
    print("Medallas Ganadas:" + str(len(DetailOlympicGameList)-1))
    print("Archivo almacenado en el directorio:" + FilePath)

except:
    print("Error en la generación del archivo csv")


