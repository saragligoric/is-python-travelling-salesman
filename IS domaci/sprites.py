import math
import random
import sys

import pygame
import os
import config

from queue import PriorityQueue


class BaseSprite(pygame.sprite.Sprite):
    images = dict()

    def __init__(self, x, y, file_name, transparent_color=None, wid=config.SPRITE_SIZE, hei=config.SPRITE_SIZE):
        pygame.sprite.Sprite.__init__(self)
        if file_name in BaseSprite.images:
            self.image = BaseSprite.images[file_name]
        else:
            self.image = pygame.image.load(os.path.join(config.IMG_FOLDER, file_name)).convert()
            self.image = pygame.transform.scale(self.image, (wid, hei))
            BaseSprite.images[file_name] = self.image
        # making the image transparent (if needed)
        if transparent_color:
            self.image.set_colorkey(transparent_color)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)


class Surface(BaseSprite):
    def __init__(self):
        super(Surface, self).__init__(0, 0, 'terrain.png', None, config.WIDTH, config.HEIGHT)


class Coin(BaseSprite):
    def __init__(self, x, y, ident):
        self.ident = ident
        super(Coin, self).__init__(x, y, 'coin.png', config.DARK_GREEN)

    def get_ident(self):
        return self.ident

    def position(self):
        return self.rect.x, self.rect.y

    def draw(self, screen):
        text = config.COIN_FONT.render(f'{self.ident}', True, config.BLACK)
        text_rect = text.get_rect(center=self.rect.center)
        screen.blit(text, text_rect)


class CollectedCoin(BaseSprite):
    def __init__(self, coin):
        self.ident = coin.ident
        super(CollectedCoin, self).__init__(coin.rect.x, coin.rect.y, 'collected_coin.png', config.DARK_GREEN)

    def draw(self, screen):
        text = config.COIN_FONT.render(f'{self.ident}', True, config.RED)
        text_rect = text.get_rect(center=self.rect.center)
        screen.blit(text, text_rect)


class Agent(BaseSprite):
    def __init__(self, x, y, file_name):
        super(Agent, self).__init__(x, y, file_name, config.DARK_GREEN)
        self.x = self.rect.x
        self.y = self.rect.y
        self.step = None
        self.travelling = False
        self.destinationX = 0
        self.destinationY = 0

    def set_destination(self, x, y):
        self.destinationX = x
        self.destinationY = y
        self.step = [self.destinationX - self.x, self.destinationY - self.y]
        magnitude = math.sqrt(self.step[0] ** 2 + self.step[1] ** 2)
        self.step[0] /= magnitude
        self.step[1] /= magnitude
        self.step[0] *= config.TRAVEL_SPEED
        self.step[1] *= config.TRAVEL_SPEED
        self.travelling = True

    def move_one_step(self):
        if not self.travelling:
            return
        self.x += self.step[0]
        self.y += self.step[1]
        self.rect.x = self.x
        self.rect.y = self.y
        if abs(self.x - self.destinationX) < abs(self.step[0]) and abs(self.y - self.destinationY) < abs(self.step[1]):
            self.rect.x = self.destinationX
            self.rect.y = self.destinationY
            self.x = self.destinationX
            self.y = self.destinationY
            self.travelling = False

    def is_travelling(self):
        return self.travelling

    def place_to(self, position):
        self.x = self.destinationX = self.rect.x = position[0]
        self.y = self.destinationX = self.rect.y = position[1]

    # coin_distance - cost matrix
    # return value - list of coin identifiers (containing 0 as first and last element, as well)
    def get_agent_path(self, coin_distance):
        pass


class ExampleAgent(Agent):
    def __init__(self, x, y, file_name):
        super().__init__(x, y, file_name)

    def get_agent_path(self, coin_distance):
        path = [i for i in range(1, len(coin_distance))]
        random.shuffle(path)
        return [0] + path + [0]


class Aki(Agent):
    def __init__(self, x, y, file_name):
        super().__init__(x, y, file_name)

    def get_agent_path(self, coin_distance):
        prevcoin = 0
        nextcoin = 0

        obidjeni = []
        path = []

        for i in range(len(coin_distance) - 1):
            currmin = sys.maxsize
            for j in range(len(coin_distance)):
                if coin_distance[prevcoin][j] < currmin and j != prevcoin and j not in obidjeni:
                    currmin = coin_distance[prevcoin][j]
                    nextcoin = j
            obidjeni.append(prevcoin)
            path.append(nextcoin)
            prevcoin = nextcoin

        return [0] + path + [0]


class Jocke(Agent):
    def __init__(self, x, y, file_name):
        super().__init__(x, y, file_name)

    def get_agent_path(self, coin_distance):
        elems = [i for i in range(1, len(coin_distance))]

        minpath = []
        minprice = sys.maxsize

        for p in permutFunc(elems):
            currpath = p
            currprice = 0
            for j in range(len(elems) - 1):
                first = currpath[j]
                second = currpath[j + 1]
                currprice = currprice + coin_distance[first][second]
            currprice = currprice + coin_distance[0][currpath[0]]
            currprice = currprice + coin_distance[0][currpath[len(currpath) - 1]]
            if currprice < minprice:
                minprice = currprice
                minpath = currpath
        return [0] + minpath + [0]


def permutFunc(myList):
    # No permutations for empty list
    if len(myList) == 0:
        return []

    # Single permutation for only one element
    if len(myList) == 1:
        return [myList]

    # Permutations for more than 1 characters
    k = []

    # Looping
    for i in range(len(myList)):
        m = myList[i]
        res = myList[:i] + myList[i + 1:]
        for p in permutFunc(res):
            k.append([m] + p)
    return k


class Uki(Agent):
    def __init__(self, x, y, file_name):
        super().__init__(x, y, file_name)

    def get_agent_path(self, coin_distance):
        retpath = []

        queue = PriorityQueue()
        queue.put((0, [0]))

        item = queue.get()
        price = item[0]
        path = item[1]
        for i in range(len(coin_distance)):
            if i != 0:
                newpath = path + [i]
                newprice = price + coin_distance[0][i]
                queue.put((newprice, newpath))

        flag = 1
        while flag:
            item = queue.get()
            price = item[0]
            path = item[1]

            # MOLI SE BOGU DA OVO DOLE ZAPRAVO RADI ISPRAVNO
            #####

            itemlist = [item]

            # skupljas sve elemente iz reda koji imaju istu cenu kao item ako postoje
            nesto = 1
            while nesto:
                nextitem = queue.get()
                nextprice = nextitem[0]
                nextpath = nextitem[1]
                if price == nextprice:
                    itemlist.append(nextitem)
                else:
                    queue.put(nextitem)
                    nesto = 0

            # ako postoji vise od jednog elementa u listi itema biras od njih onaj
            # koji zadovoljava uslove i njega proglasis kao item
            maxcoins = len(path)
            maxcoinid = path[-1]
            for i in range(len(itemlist)):
                nextitem = itemlist[i]
                nextprice = nextitem[0]
                nextpath = nextitem[1]
                nextcoins = len(nextpath)
                nextcoinid = nextpath[-1]
                if nextcoins > maxcoins:
                    item = nextitem
                    price = nextprice
                    path = nextpath
                    maxcoins = nextcoins
                    maxcoinid = nextcoinid
                elif nextcoins == maxcoins:
                    if nextcoinid < maxcoinid:
                        item = nextitem
                        price = nextprice
                        path = nextpath
                        maxcoins = nextcoins
                        maxcoinid = nextcoinid

            # na kraju petlje je odredjen item koji uzimas
            # sve elemente pomocne liste osim itema vratis u red
            for i in range(len(itemlist)):
                if itemlist[i] != item:
                    queue.put(itemlist[i])

            #####
            # MOLI SE BOGU DA OVO GORE ZAPRAVO RADI ISPRAVNO

            # ako je poslednji cvor na putanji koja se izvuce nulti, to je resenje
            if path[-1] == 0:
                retpath = path
                flag = 0
                continue

            # za svakog sledbenika poslednjeg cvora na putanji koja se izvuce se formira nova putanja,
            # izracuna se cena putanje i ona se doda u listu

            # prethodno proveri da li su pokupljeni svi novcici
            # ako jesu dodaj nulti cvor u putanju, opet izracunaj cenu i dodaj ga u listu

            if len(path) == len(coin_distance):
                lastccoin = path[-1]
                newpath = path + [0]
                newprice = price + coin_distance[0][lastccoin]
                queue.put((newprice, newpath))
            else:
                lastccoin = path[-1]
                for i in range(len(coin_distance)):
                    if i not in path:
                        newpath = path + [i]
                        newprice = price + coin_distance[lastccoin][i]
                        queue.put((newprice, newpath))

        return retpath


class Micko(Agent):
    def __init__(self, x, y, file_name):
        super().__init__(x, y, file_name)

    def get_agent_path(self, coin_distance):
        retpath = []

        queue = PriorityQueue()
        queue.put((0, 0, 0, [0]))

        item = queue.get()
        totalprice = item[0]
        mstprice = item[1]
        price = item[2]
        path = item[3]
        for i in range(len(coin_distance)):
            if i != 0:
                newpath = path + [i]
                newprice = price + coin_distance[0][i]
                newmstcost = mstCost(coin_distance, newpath)
                newtotalcost = newprice + newmstcost
                queue.put((newtotalcost, newmstcost, newprice, newpath))

        flag = 1
        while flag:
            item = queue.get()
            totalprice = item[0]
            mstprice = item[1]
            price = item[2]
            path = item[3]

            # MOLI SE BOGU DA OVO DOLE ZAPRAVO RADI ISPRAVNO
            #####

            itemlist = [item]

            # skupljas sve elemente iz reda koji imaju istu cenu kao item ako postoje
            nesto = 1
            while nesto:
                nextitem = queue.get()
                nexttotalprice = nextitem[0]
                nextmstprice = nextitem[1]
                nextprice = nextitem[2]
                nextpath = nextitem[3]
                if totalprice == nexttotalprice:
                    itemlist.append(nextitem)
                else:
                    queue.put(nextitem)
                    nesto = 0

            # ako postoji vise od jednog elementa u listi itema biras od njih onaj
            # koji zadovoljava uslove i njega proglasis kao item
            maxcoins = len(path)
            maxcoinid = path[-1]
            for i in range(len(itemlist)):
                nextitem = itemlist[i]
                nextprice = nextitem[0]
                nextpath = nextitem[3]
                nextcoins = len(nextpath)
                nextcoinid = nextpath[-1]
                if nextcoins > maxcoins:
                    item = nextitem
                    price = nextprice
                    path = nextpath
                    maxcoins = nextcoins
                    maxcoinid = nextcoinid
                elif nextcoins == maxcoins:
                    if nextcoinid < maxcoinid:
                        item = nextitem
                        price = nextprice
                        path = nextpath
                        maxcoins = nextcoins
                        maxcoinid = nextcoinid

            # na kraju petlje je odredjen item koji uzimas
            # sve elemente pomocne liste osim itema vratis u red
            for i in range(len(itemlist)):
                if itemlist[i] != item:
                    queue.put(itemlist[i])

            #####
            # MOLI SE BOGU DA OVO GORE ZAPRAVO RADI ISPRAVNO

            # ako je poslednji cvor na putanji koja se izvuce nulti, to je resenje
            if path[-1] == 0:
                retpath = path
                flag = 0
                continue

            # za svakog sledbenika poslednjeg cvora na putanji koja se izvuce se formira nova putanja,
            # izracuna se cena putanje i ona se doda u listu

            # prethodno proveri da li su pokupljeni svi novcici
            # ako jesu dodaj nulti cvor u putanju, opet izracunaj cenu i dodaj ga u listu

            if len(path) == len(coin_distance):
                lastccoin = path[-1]
                newpath = path + [0]
                newprice = price + coin_distance[0][lastccoin]
                newmstcost = 0
                newtotalcost = newprice + newmstcost
                queue.put((newtotalcost, newmstcost, newprice, newpath))
            else:
                lastccoin = path[-1]
                for i in range(len(coin_distance)):
                    if i not in path:
                        newpath = path + [i]
                        newprice = price + coin_distance[lastccoin][i]
                        newmstcost = mstCost(coin_distance, path)
                        newtotalcost = newmstcost + newprice
                        queue.put((newtotalcost, newmstcost, newprice, newpath))

        return retpath


def mstCost(coin_distance, path):
    N = len(coin_distance)
    g = Graph(N)

    nodes = [0]
    # cvorovi koji treba da se obrade - svi koji nisu u path i dodatno cvor 0
    for i in range(len(coin_distance)):
        if i in path:
            continue
        else:
            nodes.append(i)

    temp = [row[:] for row in coin_distance]
    # matrica grafa
    for j in range(len(coin_distance)):
        if j not in nodes:
            for z in range(len(coin_distance)):
                temp[j][z] = 0
                temp[z][j] = 0

    for p in range(len(coin_distance)):
        for q in range(len(coin_distance)):
            g.addEdge(p, q, temp[p][q])

    # Function call
    return g.KruskalMST()


class Graph:

    def __init__(self, vertices):
        self.V = vertices  # No. of vertices
        self.graph = []
        # to store graph

    # function to add an edge to graph
    def addEdge(self, u, v, w):
        self.graph.append([u, v, w])

    # A utility function to find set of an element i
    # (truly uses path compression technique)
    def find(self, parent, i):
        if parent[i] != i:
            # Reassignment of node's parent to root node as
            # path compression requires
            parent[i] = self.find(parent, parent[i])
        return parent[i]

    # A function that does union of two sets of x and y
    # (uses union by rank)
    def union(self, parent, rank, x, y):

        # Attach smaller rank tree under root of
        # high rank tree (Union by Rank)
        if rank[x] < rank[y]:
            parent[x] = y
        elif rank[x] > rank[y]:
            parent[y] = x

        # If ranks are same, then make one as root
        # and increment its rank by one
        else:
            parent[y] = x
            rank[x] += 1

    # The main function to construct MST using Kruskal's
    # algorithm
    def KruskalMST(self):

        result = []  # This will store the resultant MST

        # An index variable, used for sorted edges
        i = 0

        # An index variable, used for result[]
        e = 0

        # Step 1:  Sort all the edges in
        # non-decreasing order of their
        # weight.  If we are not allowed to change the
        # given graph, we can create a copy of graph
        self.graph = sorted(self.graph,
                            key=lambda item: item[2])

        parent = []
        rank = []

        # Create V subsets with single elements
        for node in range(self.V):
            parent.append(node)
            rank.append(0)

        # Number of edges to be taken is equal to V-1
        while e < self.V - 1:

            # Step 2: Pick the smallest edge and increment
            # the index for next iteration
            u, v, w = self.graph[i]
            i = i + 1
            x = self.find(parent, u)
            y = self.find(parent, v)

            # If including this edge doesn't
            # cause cycle, then include it in result
            # and increment the index of result
            # for next edge
            if x != y:
                e = e + 1
                result.append([u, v, w])
                self.union(parent, rank, x, y)
            # Else discard the edge

        minimumCost = 0
        # print("Edges in the constructed MST")
        for u, v, weight in result:
            minimumCost += weight
            # print("%d -- %d == %d" % (u, v, weight))
        # print("Minimum Spanning Tree", minimumCost)

        return minimumCost
