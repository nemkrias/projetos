# IDENTIFIQUE-SE NA LINHA ABAIXO
__author__ = "name = Maria Teresa Martins, number = ist1106382"

from dataclasses import dataclass
import math
import os


# earth radius
ER = 6371.0

@dataclass
class Connection:
    iata_origin: str
    iata_destination:str
    kms: int

COORD_LIMIT = 180

@dataclass
class Coordinates:
    lat : float
    lon : float

@dataclass
class Airport:
    name: str
    country: str
    is_capital: bool
    iata: str
    coord: Coordinates
    outgoing: dict[str,Connection] #associa o código iata do aeroporto de destino da connection
    

@dataclass
class AirMap:
    name: str
    num_airports: int
    num_connections: int
    airports: dict[str,Airport] #associa a cada IATA um aeroporto

Route = list[str]

def new_airmap(name: str) -> AirMap:
    return AirMap(name, 0, 0, {})


def new_coordinates(lat: float, lon: float) -> Coordinates | None:
    """ Returns a new Coordinates object if the given coordinates are valid, or
    None otherwise. """
    if not -180 <= lon <= 180:
        return None
    if not -90 <= lat <= 90:
        return None
    return Coordinates(lat, lon)


def is_valid_iata(iata: str) -> bool:
    """ Returns True if the given IATA code is valid, i.e., a string of three
    uppercase letters, or False otherwise."""
    return isinstance(iata, str) and len(
        iata) == 3 and iata.isupper() and iata.isalpha()


def new_airport(name: str, country: str, iata: str, cap: bool,
                coo: Coordinates) -> Airport | None:
    """ Returns a new Airport object if the given parameters are valid,
    or None otherwise."""
    if not (isinstance(name, str) and len(name) > 0):
        return None
    if not (isinstance(country, str) and len(country) > 0):
        return None
    if not is_valid_iata(iata):
        return None
    if not isinstance(cap, bool):
        return None
    return Airport(name, country, cap, iata, coo, {})


def add_airport(w: AirMap, a: Airport) -> int | None:
    """ Adds a new airport to the AirMap.
    Returns the number of airports in the AirMap after the addition if the
    airport is valid, or None otherwise. """
    if a.iata in w.airports:
        return None
    if len(a.outgoing) > 0:
        return None
    w.airports[a.iata] = a
    w.num_airports = len(w.airports)
    return w.num_airports


def new_connection(origin: str, destination: str,
                   kms: int) -> Connection | None:
    """ Returns a new Connection object if the given parameters are valid,
    or None otherwise."""
    if not is_valid_iata(origin):
        return None
    if not is_valid_iata(destination):
        return None
    if not 0 < kms <= math.pi * ER:
        # kms must be greater than 0 and smaller than hald the circumference
        # of the earth
        return None
    return Connection(origin, destination, kms)


def haversine(phi1: float, phi2: float, lam1: float, lam2: float,
              r: int) -> float:
    """ Auxiliary function for compute_distance. Computes the haversine
    distance between two points on the Earth's surface."""
    a = math.sin((phi2 - phi1) / 2) ** 2
    b = math.sin((lam2 - lam1) / 2) ** 2
    c = math.cos(phi1) * math.cos(phi2)
    return 2 * r * math.asin(math.sqrt(a + b * c))


def compute_distance(a: Airport, b: Airport) -> int:
    """ Returns the distance between two airports in kms,
    rounded to an integer."""
    return int(haversine(math.radians(a.coord.lat),
                         math.radians(b.coord.lat),
                         math.radians(a.coord.lon),
                         math.radians(b.coord.lon),
                         6371))


def add_connection(w: AirMap, s: str, d: str) -> int | None:
    """ Adds a new connection to the AirMap.
    Returns the number of connections in the AirMap after the addition
    if the connection is valid, or None otherwise."""
    if s not in w.airports:  # Source airport not in Airmap
        return None
    if d not in w.airports:  # Destination airport not in Airmap
        return None

    a_s = w.airports[s]
    a_d = w.airports[d]
    if d in a_s.outgoing:  # Connection already exists
        return None

    connection = new_connection(s, d, compute_distance(a_s, a_d))
    a_s.outgoing[d] = connection
    w.num_connections += 1
    return w.num_connections


def near_distance(w: AirMap, a: Airport, radius_kms: int) -> set[str] | None:
    """ Returns a set of airport IATA codes within a given radius
    of a given airport"""
    if radius_kms < 0:  # radius must be positive
        return None
    ans = set()
    for b in w.airports.values():
        if compute_distance(a, b) < radius_kms:
            ans.add(b.iata)
    return ans


def route_distance(w: AirMap, route: list[str]) -> int | None:
    """ Returns the total distance of a route,
    or None if the route is invalid"""
    total_distance = 0
    if len(route) == 0:
        return 0
    if len(route) == 1:
        if route[0] in w.airports:
            return 0
        else:  # the route has an invalid airport
            return None
    for i in range(len(route) - 1):
        iata = route[i]
        iata2 = route[i + 1]
        if iata2 in route[:i + 1]:  # the route has a cycle
            return None
        if iata not in w.airports or iata2 not in w.airports:
            # the route has an invalid airport
            return None
        airport = w.airports[iata]
        if iata2 not in airport.outgoing:  # the route has an invalid connection
            return None
        else:
            total_distance += airport.outgoing[iata2].kms
    return total_distance


def near_hops_set(w: AirMap, aset: set[str]) -> set[str]:
    """ Auxiliary function for near_hops.
    Returns a set of airport IATA codes reachable
    from a given set of airports"""
    startl = set()
    for siata in aset:
        for anext in w.airports[siata].outgoing.values():
            startl.add(anext.iata_destination)
    return startl


def near_hops(w: AirMap, a: Airport, hops: int) -> (set[str] | None):
    """ Returns a set of IATA codes of airports reachable
    from a given airport in a given number of hops"""
    if hops < 0:
        return None
    front = {a.iata}
    for i in range(hops):
        # Add to front the airports reachable from front in one hop
        front = front.union(near_hops_set(w, front))
    return front

#novo projeto
@dataclass
class AirportNotFound(Exception):
    def __init__(self, iata):
        self.iata = iata

@dataclass
class NoConnections(Exception):
    pass

def load_map(filename:str) ->AirMap:
    """constrói um mapa de aeroportos a partir de dois ficheiros com aeroportos e ligações

    Args:
        filename (str): nome do ficheiro comum

    Raises:
        FileNotFoundError: utilizado se um dos ficheiros não for encontrado

    Returns:
        AirMap: mapa de aeroportos 
    """    

    if not os.path.exists(f"{filename}.ports"):
        raise FileNotFoundError(f"The file {filename}.ports does not exist.")
    
    if not os.path.exists(f"{filename}.conn"):
        raise FileNotFoundError(f"The file {filename}.conn does not exist.")
    
    am = new_airmap(filename)

    #extrair todos os aeroportos contidos no AirMap sem as connections
    f1 = open(f"{filename}.ports", 'r', encoding='UTF-8')
    linha = f1.readline()
    while linha != "":
        linha = linha.replace("\n", "")
        lista = linha.split("|")
        coordenadas = new_coordinates(float(lista[3]), float(lista[4]))
        aeroporto = new_airport(lista[0], lista[1], lista[2], lista[5].lower() == "true", coordenadas)
        add_airport(am, aeroporto)
        linha = f1.readline()
    f1.close()

    #extrair as connections de cada aeorporto
    f2 = open(f"{filename}.conn", 'r', encoding='UTF-8')
    linha2 = f2.readline()
    while linha2 != "":
        linha2 = linha2.replace("\n", "")
        lista2 = linha2.split(" ")
        if "X" in lista2:
            if lista2[1] and lista2[2] in am.airports:
                add_connection(am, lista2[1], lista2[2])
        linha2 = f2.readline()
    f2.close()
    
    return am

def longest_connection_from_airport(w: AirMap, iata: str) -> Connection:
    """calcula a maior conexão direta do aeroporto 

    Args:
        w (AirMap): mapa de aeroportos
        iata (str): aeroporto inicial

    Raises:
        AirportNotFound: verfica que o aeroporto está no mapa de aeroportos
        NoConnections: verifica que o aeroporto tem ligações

    Returns:
        Connection: maior conexão 
    """    
    if iata not in w.airports:
        raise AirportNotFound(iata)

    if not w.airports[iata].outgoing:
        raise NoConnections

    #calcular a ligação (assumindo que é única?)
    longest_distance = 0 #armazenar a maior distância
    iata_destino = "" #armazenar o código iata do aeroporto mais longe
    aeroporto = w.airports[iata]
    for destino in aeroporto.outgoing:
        aeroporto_destino = w.airports[destino]
        distance = compute_distance(aeroporto, aeroporto_destino)
        if distance > longest_distance:
            longest_distance = distance
            iata_destino = destino
    
    return Connection(iata, iata_destino, longest_distance)


def longest_connection(w: AirMap) -> Connection:
    """calcula a conexão mais longa do mapa

    Args:
        w (AirMap): mapa de aeroportos

    Raises:
        NoConnections: utilizado se não houver aeroportos no mapa ou se nenhum tiver conexões

    Returns:
        Connection: conexão mais longa
    """    
    distance = 0 #armazena a maior distância
    connection_final: Connection #armazena o código iata do aeroporto de destino

    if w.num_airports == 0 or w.num_connections == 0:
        raise NoConnections

    for iata in w.airports:
        try:
            con = longest_connection_from_airport(w, iata)
            if con.kms > distance:
                distance = con.kms
                connection_final = con
        except NoConnections:
            continue

    
    return connection_final

def get_degree(w: AirMap, iata: str) -> int:
    """calcula o grau do aeroporto, ou seja, nº de ligações que têm início ou fim nele

    Args:
        w (AirMap): mapa de aeroportos
        iata (str): iata do aeroporto a analisar

    Raises:
        AirportNotFound: utilizado se o aeroporto não pertencer ao mapa

    Returns:
        int: nº de ligações que começam ou acabam no aeroporto
    """    
    
    if iata not in w.airports:
        raise AirportNotFound(iata)

    #calcular o grau do aeroporto
    aeroporto = w.airports[iata]
    n_inicio = len(aeroporto.outgoing)
    n_fim = 0
    for aero in w.airports.values():
        if iata in aero.outgoing:
            n_fim += 1
    grau = n_inicio + n_fim
    return grau

def reach(w: AirMap, iata: str) -> int:
    """calcula o menor nº de ligações necessárias para atingir todos os aeroportos do mapa

    Args:
        w (AirMap): mapa de aeroportos
        iata (str): iata do aeroporto inicial

    Raises:
        AirportNotFound: utilizado se o aeroporto não existir no mapa 

    Returns:
        int: nº de ligações necesárias / None se não for possível atingir todos os aeroportos
    """    
    if iata not in w.airports:
        raise AirportNotFound(iata)
    
    aeroporto = w.airports[iata]
    medida = near_hops(w, aeroporto, 0) #set com todos os aeroportos para os quais se verificou connections
    contador = 1 #contador do número de ligações necessárias
    while len(w.airports) > len(medida):
        if near_hops(w, aeroporto, contador) | medida == medida: #caso em que não é possível atingir todos os aeroportos
            return None
        else:
            medida = medida | near_hops(w, aeroporto, contador) #adicionar os aeroportos não repetidos
            contador += 1 #icrementar o número de connections

    return contador - 1

def heapify_node(a: list, n:int, f:int, dic: dict, i: int, j: int):
    """função auxiliar que reorganiza cada subárvore mais pequena

    Args:
        a (list): lista com os aps em aberto que será ordenada num heap
        n (int): comprimento da lista
        f (int): elemento da lista pelo qual se está a iterar
        dic (dict): dicionário de todos os aeroportos para acessar as distâncias e hops
        i (int): depende do peso (distância / hops)
        j (int): depende do peso (hops / distância)

    Returns:
        int: devolve o valor "pai" de cada subárvore organizada
    """    
    pai = f
    esq = 2*f + 1
    dir = 2*f + 2

    if esq < n and (dic[a[esq]][i] < dic[a[pai]][i] or (dic[a[esq]][i] == dic[a[pai]][i] and dic[a[esq]][j] < dic[a[pai]][j])):
        pai = esq

    if dir < n and (dic[a[dir]][i] < dic[a[pai]][i] or (dic[a[dir]][i] == dic[a[pai]][i] and dic[a[dir]][j] < dic[a[pai]][j])):
        pai = dir

    if pai != f:
        a[f], a[pai] = a[pai], a[f]
        return pai

    else:
        return None

    
def heapify(a: list, n:int, f:int, dic: dict, i: int, j: int):
    while f != None:
        f = heapify_node(a, n, f, dic, i, j)

def make_heap(a: list, dic: dict, i:int, j:int):
    for l in range((len(a)//2 - 1), -1, -1):
        heapify(a, len(a), l, dic, i, j)


def auxiliar(w: AirMap, src: str, dst: str, peso: str) -> Route:
    """função que gera uma lista de iatas com uma rota entre o aeroporto de iata src e o aeroporto
    de iata dst, de acordo com o argumento "peso"

    Args:
        w (AirMap): mapa de aeroportos 
        src (str): iata do aeroporto de origem
        dst (str): iata do aeroporto de destino
        peso (str): "shortest", "capital" ou "smooth" são utilizados para escolher a rota: "shortest"
        calcula a rota com distância mais curta, "capital" a rota mais curta passando apenas por 
        capitais e "smooth" a rota com menos escalas; Duas rotas com a msm distância ou nº de escalas
        para "shortest" e "smooth" utilizam o outro critério para desempate

    Returns:
        Route: retorna uma lista com os iatas selecionados ou lista vazia caso não exista rota
    """    
    
    total_aps = {} #dicionário que armazena todos os aeroportos do airmap
    aps_fechados = [src] #lista que armazena todos os aeroportos cuja menor dist / nº hops à origem já foi calculada
    aps_visitados = [] #set que armazena todos os aeroportos aos quais já foi calculada alguma distancia (pode não ser a menor)

    #organização no dic: [iata do ap] = [distancia iniciada a infinito, ap anterior, nº de hops]
    for iata in w.airports:
        total_aps[iata] = [float('inf'), str, float('inf')]
    
    #atualizar a dist, o ap anterior e os hops da origem
    total_aps[src] = [0, src, 0]

    #iniciar o iata_atual como a origem
    iata_atual = src

    while dst not in aps_fechados: #quando dst estiver fechado foi encontrado o menor caminho

        destinos = w.airports[iata_atual].outgoing
        
        #iterar pelos destinos diretos do ap atual
        for ap in destinos:

            #filtrar aps que não são capitais se necessário
            if peso == "capital" and not w.airports[ap].is_capital:
                continue

            #calcular a menor dist conhecida a cada destino / menor nº de hops
            if ap not in aps_fechados:
                
                nova = w.airports[iata_atual].outgoing[ap].kms + total_aps[iata_atual][0]

                if nova < total_aps[ap][0] and (peso != "smooth" or (peso == "smooth" and total_aps[ap][2] >= total_aps[iata_atual][2] + 1)) :
                    total_aps[ap][0] = nova #atualizar a menor dist
                    total_aps[ap][1] = iata_atual #atualizar a menor rota
                    total_aps[ap][2] = total_aps[iata_atual][2] + 1
                
                if ap not in aps_visitados:
                    aps_visitados.append(ap) #adicionar aos aps_visitados


        #determinar o próximo ap a analisar
        prox_iata = None
        prox_dist = float('inf')

        #j e i são utilizados dependendo do peso para escolher o próximo ap
        j: int
        i: int
        
        #próximo ap escolhido com base na dist
        if peso == "shortest" or peso == "capital":
            i = 0
            j = 2
        
        #próximo ap escolhido com base no nº de hops 
        if peso == "smooth":
            i = 2
            j= 0

        #verificar que ainda existem aps
        if len(aps_visitados) == 0:
            break
        
        #utilizar um heap para selecionar o proximo ap
        make_heap(aps_visitados, total_aps, i, j)

        prox_iata = aps_visitados[0]

        aps_fechados.append(prox_iata) #fechar o próximo ap
        aps_visitados.remove(prox_iata) #tirar dos visitados

        if peso == "shortest" or peso == "capital":
            total_aps[prox_iata][2] = total_aps[iata_atual][2] + 1 #atualizar o nº minimo de hops pra dist mínima
        
        iata_atual = prox_iata

    #devolver lista vazia se não for possível chegar ao ap de destino
    if dst not in aps_fechados:
        return []
    
    #escrever a rota mais curta com base nos aps anteriores
    else:
        rota = [dst]
        iterador = dst
        while src not in rota:
            ap_ant = total_aps[iterador][1]
            rota.insert(0, ap_ant)
            iterador = ap_ant

        return rota
    

def shortest_route(w: AirMap, src: str, dst: str) -> Route:
    """função que calcula a rota mais curta; se 2 rotas tiverem a mesma distância, utiliza o nº de 
    hops como critério

    Args:
        w (AirMap): mapa de aeroportos
        src (str): iata do aeroporto de origem
        dst (str): iata do aeroporto de destino

    Raises:
        AirportNotFound(src): utilizado se o aeroporto de origem não existir no mapa
        AirportNotFound(dst): utilizado se o aeroporto de destino não existir no mapa

    Returns:
        Route: lista com a rota mais curta / lista vazia se não existir rota
    """    

    if src not in w.airports:
        raise AirportNotFound(src)

    if dst not in w.airports:
        raise AirportNotFound(dst)

    return auxiliar(w, src, dst, "shortest")


def shortest_capital_route(w: AirMap, src: str, dst: str) -> Route:
    """calcula a rota mais curta, passando apenas por capitais; o critério de desempate é o nº d hops

    Args:
        w (AirMap): mapa de aertoportos
        src (str): iata do aeroporto de origem
        dst (str): iata do aeroporto de destino

    Raises:
        AirportNotFound(src): utilizado se o aeroporto de origem não existe no mapa ou não é capital
        AirportNotFound(dst): utilizado se o aeroporto de destino não existe no mapa ou não é capital

    Returns:
        Route: lista dos iatas dos aeroportos da rota / lista vazia se não existir uma rota
    """    

    if src not in w.airports or w.airports[src].is_capital != True:
        raise AirportNotFound(src)

    if dst not in w.airports or w.airports[dst].is_capital != True:
        raise AirportNotFound(dst)

    return auxiliar(w, src, dst, "capital")

def smoothest_route(w: AirMap, src: str, dst: str) -> Route:
    """calcula a rota com menos escalas; critério de desempate é a distância

    Args:
        w (AirMap): mapa de aeroportos
        src (str): iata do aeroporto de origem
        dst (str): iata do aeroporto de destino

    Raises:
        AirportNotFound(src): utilizado se o aeroporto de origem não existe no mapa
        AirportNotFound(dst): utilizado se o aeroporto de destino não existe no mapa

    Returns:
        Route: lista com os iatas dos aeroportos da rota com menos escalas; lista vazia se não existir 
        rota
    """    

    if src not in w.airports:
        raise AirportNotFound(src)

    if dst not in w.airports:
        raise AirportNotFound(dst)
    
    return auxiliar(w, src, dst, "smooth")