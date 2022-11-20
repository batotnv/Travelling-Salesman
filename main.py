#!/usr/bin/env python
# coding: utf-8

# 
# ![image.png](attachment:image.png)

# # Cel projektu

# Celem projektu jest znalezienie najkrótszej trasy łączącej 71 wybranych sklepów "Castorama" w Polsce. Jest to tzw. "problem komiwojażera".
# 
# W celu osiągnięcia postawionego celu będzie minimalizowana suma odległości pomiędzy poszczególnymi lokalizacjami sklepów.

# # Biblioteki

# Użyte biblioteki w projekcie:

# In[44]:


import numpy as np
import random
import pandas as pd
import math
import matplotlib.pyplot as plt


# # Wczytanie i opis danych

# In[45]:


#wczytanie danych

coordinates = pd.read_csv("wspolrzedne.csv", delimiter =";")

print(coordinates.head())


# Powyżej zaprezentowano 5 pierwszych wierszych w wykorzystywanym zbiorze danych . Lokalizacja sklepów jest określona za pomocą współrzędnych geograficznych:
# 
# * latitude, czyli szerokości geograficznej
# * longitude, czyli długości geograficznej
# 
# W pierwszej kolumnie jest **ID** danego sklepu natomiast w kolumnie **Name** można znaleźć dokładny adres poszczególnych sklepów.

# # Przygotowanie danych

# Dane zostaną przekształcone do listy krotek. Krotka zawiera odpowiednio szerokość i długość geograficzną.

# In[46]:


cities = []

for i in range(0, len(coordinates)):
    city = (coordinates.iloc[i,1], coordinates.iloc[i,2])
    cities.append(city)


# Tak się prezentują przekształcone dane:

# In[47]:


#wszystkie miejsce w jednej liscie
print(cities[1:5])


# # Stworzenie funkcji

# ## Funkcja obliczająca dystans pomiędzy współrzędnymi geograficznymi

# Pierwsza stworzona funkcja w projekcie pozwoli na obliczenie dystansu (w kilometrach) pomiędzy dwoma miejscami, których lokalizacja jest określona za pomocą współrzędnych geograficznych.
# 
# Dla uproszczenia przyjęto najkrótszy dystans nad powierzchnią ziemi (tj. według lotu ptaka). Nie uwzględniono w dystansie ulic itp.
# 
# Użyto tzw. formuły "haversine".

# In[48]:


# x[0] latitude1 - szerokosc geo1
# y[0] latitude2 - szerokosc geo2

# x[1] longitude1 - dlugosc geo 1
# y[1] longitude2 - dlugosc geo 1

def distance_between_coordinates(x, y):
    
    #promien ziemski
    R = 6371e3 #w metrach
    
    #szerokosc na radiany
    phi1 = x[0] * math.pi/180
    phi2 = y[0] * math.pi/180
    
    #delta latitude
    dphi = (abs(x[0]-y[0]))* math.pi/180
    
    #delta longitude
    dlambda = (abs(x[1]-y[1]))* math.pi/180
    
    #zmienne pomocnicze
    a = math.sin(dphi/2) * math.sin(dphi/2) + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda/2) * math.sin(dlambda/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    #odleglosc w metrach
    d = R * c 
    
    return d/1000 # zamiana na kilometry


# ## Funkcja tworząca macierz odległości między wszystkimi lokalizacjami

# In[49]:


#obliczenie odleglosci pomiedzy miejscami

def calculate_distance(cities):
    
    distances = np.zeros((len(cities), len(cities)))
    
    for i in range(len(cities)):
        for j in range(len(cities)):
            distance = distance_between_coordinates(cities[i], cities[j])
            distances[i][j] = distance
    
    return distances
    
    


# ## Funkcja zwrająca losową kolejność odwiedzanych miejsc

# In[50]:


#kolejnosc odwiedzanych miejsc

def random_city_order(n):
    order_list = []
    for i in range(n):
        order_list.append(i)
    random.shuffle(order_list)
    return order_list


# ## Funkcja - wizualizacja na wykresie

# In[51]:


#wizualizacja na wykresie

def draw_plot(cities, t):

    wspx, wspy = zip(*cities)

    plt.scatter(wspx, wspy)

    for j in range(len(t)):
        plt.annotate(t[j], cities[t[j]])

    for j in range(len(t)-1):   
        lines = plt.plot((cities[t[j]][0],cities[t[j+1]][0]), (cities[t[j]][1],cities[t[j+1]][1]))
        plt.setp(lines, color = 'r', linewidth = 1.5)

    plt.show()


# ## Obliczenie całkowitej odległości dla drogi

# In[52]:


def total_distance(distances, t):
    distance = 0
    
    for i in range(len(t)-1):
        distance += distances[t[i]][t[i+1]]
    return distance
 


# ## Zamiana losowych dwóch lokalizacji miejscami

# In[53]:


#zamiana losowych dwoch miast miejscami
#do mutacji

def switch_order(t):
    
    new_t = t[:]
    
    switch_point1 = random.randint(0, len(t)-1)
    switch_point2 = random.randint(0, len(t)-1)
    
    temp = new_t[switch_point1]
    new_t[switch_point1] = new_t[switch_point2]
    new_t[switch_point2] = temp
    
    return new_t


# ## Wybór n najlepszych dróg

# In[54]:


#wybor n najlepszych
def choose_n_best(lst, n, rev=False):
    index = range(len(lst))
    s = sorted(index, reverse=rev, key=lambda i: lst[i])
    return s[:n]


# ## Krzyżówka

# In[55]:


#krzyzowanie

def crossover(o1, o2, P=0.5):
    if random.random() > P:
        
        crossover_point = random.randint(0, len(o1)-1)

        crossed_o1 = o1[:crossover_point]
        for element in o2:
            if element not in crossed_o1:
                crossed_o1.append(element)
                
        crossed_o2 = o2[:crossover_point]
        for element in o1:
            if element not in crossed_o2:
                crossed_o2.append(element)

        return crossed_o1, crossed_o2
    else:
        return o1, o2
    


# ## Mutacja

# In[56]:


#mutacja
def mutation(o1, P = 0.3):
    mutated_o1 = o1[:]
    if random.random() > P:
        mutated_o1 = switch_order(o1)
        
    return mutated_o1


# ## Algorytm genetyczny

# In[57]:


def algorytm_genetyczny(liczba_pokolen, n_pop = 16):
    
    #miasta
    miasta = cities
    
    #obliczenie macierzy odleglosci
    macierz_odleglosci = calculate_distance(miasta)
    
    #losowanie populacji
    populacja = [random_city_order(71) for i in range(n_pop)]
    
    
    for j in range(liczba_pokolen):
        
        #dlugosc trasy dla kazdego osobnika
        dlugosci_tras = [total_distance(macierz_odleglosci, populacja[i]) for i in range(len(populacja))]

        #wybieranie rodzicow
        wybrani_rodzice_id = choose_n_best(dlugosci_tras,10)
        wybrani_rodzice = [populacja[i] for i in wybrani_rodzice_id]
        
          
        #losowe dobieranie w pary
        losowe_pary = [random.sample(wybrani_rodzice, 2) for i in range(5)]
        
        dzieci = []

        #krzyzowka
        for para in losowe_pary:
            c1, c2 = crossover(para[0], para[1])
            dzieci.append(c1)
            dzieci.append(c2)
            
        #mutacja
        dzieci = [mutation(d) for d in dzieci]
        
        #dlugosci tras dzieci
        dlugosci_tras_dzieci = [total_distance(macierz_odleglosci, dzieci[i]) for i in range(len(dzieci))]

        #wybranie najlepszych dzieci
        wybrane_dzieci_id = choose_n_best(dlugosci_tras_dzieci, 6)
        wybrane_dzieci = [dzieci[i] for i in wybrane_dzieci_id]
        
        #nowa populacja
        populacja = wybrani_rodzice + wybrane_dzieci
        
        #najlepsza aktualna dlugosc i trasa
        dlugosci_tras_nowa_populacja = [total_distance(macierz_odleglosci, populacja[i]) for i in range(len(populacja))]
        najlepsza_trasa_id = choose_n_best(dlugosci_tras_nowa_populacja, 1)
        najlepsza_trasa = populacja[najlepsza_trasa_id[0]]
        najlepsza_dlugosc = dlugosci_tras_nowa_populacja[najlepsza_trasa_id[0]]
        
  #      print("Iteracja nr ",  j+1)
        
    
    draw_plot(miasta, najlepsza_trasa)
    print("Dlugosc trasy: ", round(najlepsza_dlugosc,2), "km")
    print("Najlepsza trasa: ", najlepsza_trasa)
    
    return najlepsza_trasa


# ## Uzyskane wyniki

# Dla uzyskania najlepszej drogi przeprowadzono 15000 iteracji w stworzonym algorytmie genetycznym.

# In[60]:


wynik = algorytm_genetyczny(15000)


# Na wykresie powyżej pokazano jak prezentuje się otrzymana trasa.

# Poniżej pokazano kolejność sklepów w uzyskanej trasie.

# In[61]:


kolejnosc_nazwy = [coordinates.iloc[i,3] for i in wynik]

for i in range(len(kolejnosc_nazwy)):
    print(i+1," ",kolejnosc_nazwy[i])

