
import math

def comandos(move):			#!: para as direcoes, quando fundir os codigos deixa de ser necessario
    if move[0] == 1 and move[1] == 0:	    #>
        return "d"
    elif move[0] == -1 and move[1] == 0:	#<
        return "a"
    elif move[1] == 1 and move[0] == 0:	    #˅
        return "s"
    elif move[1] == -1 and move[0] == 0:    #^
        return "w"
    else:
        print("erro no move")
        return ""          #?: n se move					
class Domain:
    def __init__(self,mapa=None, size=None,mapa_coordinates = None, rocks = None, enemies = None):
        self.mapa = mapa								#?: mapa com valores do custo por idice
        self.back_up_map = None
        self.size = size									
        self.mapa_coordinates = mapa_coordinates		#?: contem todas as coordenadas do mapa, funcao de suporte
        self.rocks = rocks								#?: contem todas as rochas em entidades Rock
        self.enemies = enemies							#?: contem todos os enimigos em entidades Enemy
        self.block_value = 5
        
    
    def positions(self,digdug):
        current_coordinate = digdug
        actlist = []
        for dx, dy in [[1, 0], [-1, 0], [0, 1], [0, -1]]:
            neighbor_coordinate = [current_coordinate[0] + dx, current_coordinate[1] + dy]
            if neighbor_coordinate in self.mapa_coordinates:
                actlist.append(neighbor_coordinate)
        #print("POSITIONS: ",actlist)
        return actlist 
        
    def atualize_map(self,map):
        self.mapa = map
        self.back_up_map = self.mapa
        for row in range(len(self.mapa)):
            for col in range(len(self.mapa[row])):
                if self.mapa[row][col] == 1:
                    self.mapa[row][col] = self.block_value
        self.change_map(self.search_tunnels())
        
        
        
    def search_tunnels(self):
        def dfs(x, y):
            if 0 <= x < len(matrix_copy) and 0 <= y < len(matrix_copy[0]) and matrix_copy[x][y] == 0:
                matrix_copy[x][y] = 1  # Mark as visited
                tunnel.append((x, y))
                for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                    dfs(x + dx, y + dy)
        tunnels = []
        matrix_copy = [row[:] for row in self.mapa]  # Create a copy of the original matrix
        for i in range(len(matrix_copy)):
            for j in range(len(matrix_copy[0])):
                if matrix_copy[i][j] == 0:
                    tunnel = []
                    dfs(i, j)
                    tunnels.append(tunnel)
        tunnels = tunnels[1:]
        return tunnels
    def change_map(self,tunnels):
        matrix = self.mapa
        for tunnel in tunnels:
            x1, y1 = tunnel[0]
            x2, y2 = tunnel[-1]
            if x1 == x2:
                if self.is_in_map(x1-1, y1):
                    matrix[x1-1][y1] = -50
                if self.is_in_map(x2+1, y2):
                    matrix[x2+1][y2] = -50
            elif y1 == y2:
                if self.is_in_map(x1, y1-1):
                    matrix[x1][y1-1] = -50
                if self.is_in_map(x2, y2+1):
                    matrix[x2][y2+1] = -50
        return matrix
                
    
    def is_in_map(self, x, y):
        return 0 <= x < len(self.mapa) and 0 <= y < len(self.mapa[0])
    def satisfies(self, digdug, enemy):         #?: se o digdug n tiver inimigo é pq ele ja morreu
        if digdug.enemy == None:
            return True
    
#TODO: comparar as heuristicas, usar a melhor ou fundi-las e torna-las compativeis com as 2 searchs
    def heuristic(self, digdug, goal):						
#TODO: Melhorar a heuristica
        #return abs(goal.pos[0] - digdug.pos[0]) + abs(goal.pos[1] - digdug.pos[1])
        return abs(goal.pos[0] - digdug.pos[0]) + abs(goal.pos[1] - digdug.pos[1] + self.mapa[digdug.pos[0]][digdug.pos[1]])    #?: heuristica com o custo do mapa
    
    #?: apenas atribui o custo do mapa ao node
    def heuristic2(self, newnode,goal):   
#!: experimentar a multiplicação
        #return abs(goal.pos[0] - newnode.pos[0]) + abs(goal.pos[1] - newnode.pos[1])# + self.mapa[newnode.pos[0]][newnode.pos[1]]
        return (2 * math.sqrt((goal.pos[0] - newnode.pos[0])**2 + (goal.pos[1] - newnode.pos[1])**2) ) + self.mapa[newnode.pos[0]][newnode.pos[1]]
    
    def print_enemies(self):
        for enemy in self.enemies:
            print(enemy)
    def __str__(self) -> str:
        self.print_enemies()
class DigDug:  
    def __init__(self, domain = None,last_pos = None, pos = None,dir = None, rope=None, enemy = None, real_dir = None):
        self.domain = domain
        self.last_pos = last_pos															#?: = None quando o jogo começa
        self.pos = pos
        self.dir = dir
        self.real_dir = real_dir
        self.rope = rope
        self.enemy = enemy																	#?: enimigo que se vai focar
        
    def goal_test(self):
        return self.domain.satisfies(self,self.enemy)
    
    def goal_test2(self,node_pos):
        if not self.enemy == None:
            return self.enemy.pos == node_pos
    
    def atualize_pos(self,new_pos):
        self.last_pos = self.pos
        self.pos = new_pos
        x,y = self.pos
        self.domain.mapa[x][y] = 0
        self.domain.back_up_map = self.domain.mapa
        if self.last_pos != None:
            real_dir = comandos([self.pos[0] - self.last_pos[0],self.pos[1] - self.last_pos[1]])
            if not real_dir == "":      #?: so muda o real_dir quando se move
                self.real_dir = real_dir
            #print("REAL DIR:",self.real_dir)
            #print("LAST POS:",self.last_pos)
            #print("POS:",self.pos)
        
    
    def chose_enemy(self):        															#!: ns se fica aqui ou na search                                    
        if self.domain.enemies:   		#?: apenas para confirmar que existe inimigos        
            self.enemy = next((enemy for enemy in self.domain.enemies if not enemy.in_teleport), None)
            if self.enemy is not None:
                heuristic = self.domain.heuristic(self, self.enemy)
                for enemy in self.domain.enemies:
                    new_heuristic = self.domain.heuristic(self,enemy)
                    if new_heuristic < heuristic and not enemy.in_teleport:
                        heuristic = new_heuristic
                        self.enemy = enemy
        #print("DIGDUG self.enemy:",self.enemy)
    def __str__(self):
            return "DIGDUG(" + str(self.pos) + "," + str(self.enemy) + ")"
# Nos de uma arvore de pesquisa
class Enemy:  
    def __init__(self,domain,id,type,pos,dir,real_dir=None,last_pos=None,fire = None,in_teleport=None):
        self.domain = domain						#?: para fazer alteracoes no mapa
        self.type = type
        self.id = id
        self.last_pos = last_pos
        self.pos = pos                      		
        self.dir = dir
        self.real_dir = real_dir
        self.fire = fire
        self.in_teleport = in_teleport
        
    def atualize_dir(self,dir):
        self.dir = dir
    def atualize_teleport(self):
        if self.type == 'Pooka':
            x,y = self.pos
            if self.domain.mapa[x][y] == 1:
                self.in_teleport = True
            else:
                self.in_teleport = False
    def atualize_pos(self,new_pos):					#?:UTILIZAR ESTA FUNCAO PARA INTRODUZIR A NOVA POSICAO
        self.last_pos = self.pos
        self.pos = new_pos
        print("ATUALIZE POS")
        real_dir = comandos([self.pos[0] - self.last_pos[0],self.pos[1] - self.last_pos[1]])
        if not real_dir == "":      #?: so muda o real_dir quando se move
            self.real_dir = real_dir
        self.atualize_teleport()
        print("REAL DIR:",self.real_dir)
        print("LAST POS:",self.last_pos)
        print("POS:",self.pos)
        #print("TELEPORT:",self.in_teleport)
        #self.atualize_domain()
        #self.atualize_domain2()
        
    def atualize_domain(self):		#!:TESTAR
        #print("self.pos[0]",self.pos[0])
        size = 2
        values = [[9, 9, 2, 9, 9, 9], [9, 9, 2, 9, 9], [4, 4, 0, 3, 3], [9, 9, 2, 9, 9], [9, 9, 2, 9, 9]]
#TODO lidar melhor com a subreposicao de valores
        if self.last_pos != None:
            for y in range(self.last_pos[1] - size, self.last_pos[1] + size+1):   #?: resetar os valores para os valores anteriores
                for x in range(self.last_pos[0] - size, self.last_pos[0] + size+1):
                    if x >= 0 and x < self.domain.size[0] and y >= 0 and y < self.domain.size[1]:
                        self.domain.mapa[x][y] = 1
                        #self.domain.mapa[x][y] -= values[x - self.last_pos[0] + size][y - self.last_pos[1] + size]
        for y in range(self.pos[1] - size, self.pos[1] + size+1):
            for x in range(self.pos[0] - size, self.pos[0] + size+1):
                if x >= 0 and x < self.domain.size[0] and y >= 0 and y < self.domain.size[1]:
                    #print("x,y",x,y)
                    self.domain.mapa[x][y] += values[x - self.pos[0] + size][y - self.pos[1] + size]
    
    def atualize_domain2(self):		#?: meio ranhosa, feita para o digdug matar de acordo com a direcao do inimigo
        size = 2
        if self.type == "Fygar" and self.dir == "a" or self.dir == "d":
            values = [[0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 50, 50, 50, 0, 50, 50, 50, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0]]
        elif self.type == "Fygar" and self.dir == "w" or self.dir == "s":
            values = [[0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 50, 0, 0, 0, 0], [0, 0, 0, 0, 50, 0, 0, 0, 0], [0, 0, 0, 0, 50, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 50, 0, 0, 0, 0], [0, 0, 0, 0, 50, 0, 0, 0, 0], [0, 0, 0, 0, 50, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0]]
        else:   #!:TESTAR é suposto apenas ser usado quando o inimigo ainda n tem real_dir, ou seja, na primeira vez
            #values = [[0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0],[0,0,0,0,10,0,0,0,0],[0,0,0,10,0,10,0,0,0],[0,0,0,0,10,0,0,0,0],[0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0]]
            values = [[0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0]]
        """ 
        elif self.real_dir == "a" or self.real_dir == "d":
            values = [[9,9,9,9,1,9,9,9,9],[9,9,9,9,1,9,9,9,9],[9,9,9,9,1,9,9,9,9],[9,9,9,9,1,9,9,9,9],[9,9,9,9,0,9,9,9,9],[9,9,9,9,1,9,9,9,9],[9,9,9,9,1,9,9,9,9],[9,9,9,9,1,9,9,9,9],[9,9,9,9,1,9,9,9,9]]
            #values = [[4, 4, 4, 4, 1, 4, 4, 4, 4], [4, 4, 4, 4, 1, 4, 4, 4, 4], [4, 4, 4, 4, 1, 4, 4, 4, 4], [4, 4, 4, 4, 1, 4, 4, 4, 4], [4, 4, 4, 4, 0, 4, 4, 4, 4], [4, 4, 4, 4, 1, 4, 4, 4, 4], [4, 4, 4, 4, 1, 4, 4, 4, 4], [4, 4, 4, 4, 1, 4, 4, 4, 4], [4, 4, 4, 4, 1, 4, 4, 4, 4]]
        elif self.real_dir == "w" or self.real_dir == "s":
            values = [[9,9,9,9,1,9,9,9,9],[9,9,9,9,1,9,9,9,9],[9,9,9,9,1,9,9,9,9],[9,9,9,9,1,9,9,9,9],[9,9,9,9,0,9,9,9,9],[9,9,9,9,1,9,9,9,9],[9,9,9,9,1,9,9,9,9],[9,9,9,9,1,9,9,9,9],[9,9,9,9,1,9,9,9,9]]
            #values = [[4, 4, 4, 4, 1, 4, 4, 4, 4], [4, 4, 4, 4, 1, 4, 4, 4, 4], [4, 4, 4, 4, 1, 4, 4, 4, 4], [4, 4, 4, 4, 1, 4, 4, 4, 4], [4, 4, 4, 4, 0, 4, 4, 4, 4], [4, 4, 4, 4, 1, 4, 4, 4, 4], [4, 4, 4, 4, 1, 4, 4, 4, 4], [4, 4, 4, 4, 1, 4, 4, 4, 4], [4, 4, 4, 4, 1, 4, 4, 4, 4]]
        else:   #!:TESTAR é suposto apenas ser usado quando o inimigo ainda n tem real_dir, ou seja, na primeira vez
            values = [[0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0]]
        """
#TODO lidar melhor com a subreposicao de valores
        if self.last_pos != None:
            self.domain.mapa = self.domain.back_up_map
            """             
            for y in range(self.last_pos[1] - size, self.last_pos[1] + size+1):   #?: resetar os valores para os valores anteriores
                for x in range(self.last_pos[0] - size, self.last_pos[0] + size+1):
                    if x >= 0 and x < self.domain.size[0] and y >= 0 and y < self.domain.size[1]:
                        self.domain.mapa[x][y] = self.domain.block_value
                        #self.domain.mapa[x][y] -= values[x - self.last_pos[0] + size][y - self.last_pos[1] + size]
            """        
        for y in range(self.pos[1] - size, self.pos[1] + size+1):
            for x in range(self.pos[0] - size, self.pos[0] + size+1):
                if x >= 0 and x < self.domain.size[0] and y >= 0 and y < self.domain.size[1]:
                    #print("x,y",x,y)
                    self.domain.mapa[x][y] += values[x - self.pos[0] + size][y - self.pos[1] + size]
    
    def __str__(self):
            return "ENEMY(" + str(self.pos) + "," + str(self.real_dir) + ")"
class Rope:
    def __init__(self,pos,dir):
        self.pos = pos 								#?: vetores das varias posicoes da corda
        self.dir = dir
class Rock:
    def __init__(self,pos,id):
       self.pos = pos     
       self.id = id   
    def atualize_pos(self,new_pos,domain):
        x,y = self.pos
        domain.mapa[x][y] = 0
        x1, y1 = new_pos
        self.pos = new_pos
        if x1 < len(domain.mapa) and y1 < len(domain.mapa[0]):
            domain.mapa[x1][y1] = 1000
            if x1+1 < len(domain.mapa) and y1+1 < len(domain.mapa[0]):
                domain.mapa[x1][y1+1] = 1000
class SearchNode:   												#!: PODERA N SER NECESSARIO PARA A PESQUISA
    def __init__(self,pos,heuristic=None,parent=None):
        self.pos = pos                      						#?: posicao: coordenadas correspondente no mapa [x,y]
        self.heuristic = heuristic
        self.parent = parent
        self.depth = 0
    
    def __str__(self):
        return "SearchNode(" + str(self.pos) + "," + str(self.heuristic) + "," + str(self.parent) + ")"
#?:PESQUISA FEITA SOBRE O QUE O DIGDUG SABE (DOMINIO(MAPA,INIMIGOS,ROCHAS),POSICAO,INIMIGO A MATAR,ROPE)
class ReactiveSearchTree:   										
    def __init__(self,digdug, counter = 0,next_step = None,move = None): 
        self.digdug = digdug
        self.node_digdug = SearchNode(digdug.pos, digdug.domain.heuristic(self.digdug, SearchNode(self.digdug.domain.size)))
        self.next_step = next_step
        self.move = move
        #?: para a serach2
        self.open_nodes = [self.node_digdug]
        self.solution_nodes = None
        self.path = None
        self.counter = counter
        self.stuck = 0
    def search(self):
        if self.digdug.goal_test():           						#!: o que fazer quando estiver perto
            self.next_step = [0,0]                                       #!: chegou ao enimigo     
            self.move = "" 
        else:
            digdug_enemies = []
            for a in self.digdug.domain.positions(self.digdug.pos): 
                new_node_digdug_pos = a
                new_node_digdug = SearchNode(new_node_digdug_pos)
                new_node_digdug_heuristic = self.digdug.domain.heuristic(new_node_digdug, self.digdug.enemy) 
                new_node_digdug.heuristic = new_node_digdug_heuristic #+ node.heuristic
                digdug_enemies.append(new_node_digdug)
                self.calc_step_move(digdug_enemies)												#!: ainda n chegou ao enimigo     
    def get_path(self,node):
        if node.parent == None:
            return [node.pos]
        path = self.get_path(node.parent)
        path += [node.pos]
        return(path)
     
    def search2(self):
#TODO: ter em conta que o digdug atualiza, e que a path é cortada
#TODO: comparar posicoes (digdug e inimigo) para n calcular paths 
#TODO: Optimizar a parte de quando encontra a solucao, com brakes em vez de returns 
        #!: pode-se fazer um max, para que o digdug n tenha que calcular demasiado longe
        #print("SEARCH2")
        limit = 10
        if self.digdug.enemy == None:           						#!: se n tiver enimigo n executa a search, espera pela proxima
            return None
        while self.open_nodes != []:
            if self.stuck > 1000:
                self.stuck = 0
                self.path = self.get_path(node)
                self.next_step = self.path[1]   #?: o node sesuinte à posicao do digdug
                self.decision2()
                return None
            self.stuck += 1
            #print("while")
            #print("Open nodes: ", self.open_nodes)
            node = self.open_nodes.pop(0)
            #print("Node: ", node)
            if self.digdug.goal_test(node.pos) or\
               node.depth>=limit:  #?: goal é ter a path até ao enimigo, contrariamente ao search que é quando o inimigo estiver morto aka none
                self.solution_node = node
                self.path = self.get_path(node)
                self.next_step = self.path[1]   #?: o node sesuinte à posicao do digdug
                self.decision2()
                return None
            new_nodes = []
            i = 0
            for a in self.digdug.domain.positions(node.pos):  
                if self.stuck > 1000:
                    self.stuck = 0
                    self.path = self.get_path(node)
                    self.next_step = self.path[1]   #?: o node sesuinte à posicao do digdug
                    self.decision2()
                    return None
                newnode_pos = a
                newnode = SearchNode(newnode_pos, parent=node)
                newnode_heuristic = self.digdug.domain.heuristic2(newnode,self.digdug.enemy)
                newnode.heuristic = newnode_heuristic# + node.heuristic
                newnode.depth = node.depth + 1
                #print(i)
                #print("newnode.pos",newnode.pos)
                #print("newnode.heuristic",newnode.heuristic)
                #print("node.pos",node.pos)
                #print("node.heuristic",node.heuristic)
                if newnode_pos not in self.get_path(node):
                    new_nodes.append(newnode)
                i += 1
            self.add_to_open(new_nodes)
        #print("End search2")
        return None
    
    def add_to_open(self,new_nodes):
        open_nodes = self.open_nodes + new_nodes
        sorted_open_nodes = sorted(open_nodes, key=lambda node: (node.heuristic))
        self.open_nodes = sorted_open_nodes
    
    
    # juntar novos nos a lista de nos abertos de acordo com a estrategia
    def calc_step_move(self,digdug_enemies):
        sorted_nodes = sorted(digdug_enemies, key=lambda node: (node.heuristic))
        self.next_step = sorted_nodes[0].pos                                                  #!: envia a proxima posicao a escolher
        self.decision()
    def decision2(self):
#TODO: corrigir problemas, por exemplo o counter
        def all_coordinates_same(path):
            return all(x == path[0][0] for x, _ in path) or all(y == path[0][1] for _, y in path)
        dist = self.dist_digdug_enemy()
        no_bloc = self.no_block_in_path()
        len_path = len(self.path)
        in_dir = self.is_in_direction()
        if dist == 1:
            if in_dir:
                self.move = "A"
            else:
                if self.counter <= 2:
                    y = comandos([self.path[-1][0] - self.node_digdug.pos[0],self.path[-1][1] - self.node_digdug.pos[1]])
                    self.move = (lambda y: "d" if y == "a" else ("a" if y == "d" else ("w" if y == "s" else ("s" if y == "w" else None))))(y)
                    self.counter += self.counter + 1
                    print("----------COUNTER:",self.counter)
                else:
                    y = comandos([self.path[-1][0] - self.node_digdug.pos[0],self.path[-1][1] - self.node_digdug.pos[1]])
                    self.move = (lambda y: "s" if y == "a" else ("w" if y == "d" else ("d" if y == "s" else ("a" if y == "w" else None))))(y)
                    self.counter = 0
        elif dist == 2:
#TODO: analizar outras len_paths
            if len_path == 3:   
                if no_bloc and in_dir:
                    if all_coordinates_same(self.path):
                        print("ALL COORDINATES SAME----------")
                        self.move = "A"
                    else:
                        print("TRIANGULAR SITUATION------------------")
                        y = comandos([self.path[-1][0] - self.node_digdug.pos[0],self.path[-1][1] - self.node_digdug.pos[1]])
                        self.move = (lambda y: "d" if y == "a" else ("a" if y == "d" else ("w" if y == "s" else ("s" if y == "w" else None))))(y)
                elif not no_bloc and in_dir:
                    self.move = comandos([self.next_step[0] - self.node_digdug.pos[0],self.next_step[1] - self.node_digdug.pos[1]])
                else:
                    y = comandos([self.path[-1][0] - self.node_digdug.pos[0],self.path[-1][1] - self.node_digdug.pos[1]])
                    self.move = (lambda y: "d" if y == "a" else ("a" if y == "d" else ("w" if y == "s" else ("s" if y == "w" else None))))(y)
            else:
                self.move = comandos([self.next_step[0] - self.node_digdug.pos[0],self.next_step[1] - self.node_digdug.pos[1]])
        elif dist == 3:     #!: aqui pode dar merda 
            if len_path == 4:  
                if no_bloc and in_dir:
                    self.move = "A"
                else:
                    self.move = comandos([self.next_step[0] - self.node_digdug.pos[0],self.next_step[1] - self.node_digdug.pos[1]])
            else:
                self.move = comandos([self.next_step[0] - self.node_digdug.pos[0],self.next_step[1] - self.node_digdug.pos[1]])
        else:
            self.move = comandos([self.next_step[0] - self.node_digdug.pos[0],self.next_step[1] - self.node_digdug.pos[1]])
    def decision(self):
        print("NEXT STEP:",self.next_step)
        if self.is_close_to_enemy():
            #self.move = "A"
             
            y = self.digdug.real_dir
            in_dir, x , value = self.is_in_direction()
            if in_dir:              #!: para testar
                print("IN DIRECTION")
                if self.no_block_next_step(x,value): 
                    print("NO BLOCK BETWEEN")
                    self.move = "A"
                else:
                    print("BLOCK BETWEEN")
                    self.move = comandos([self.next_step[0] - self.node_digdug.pos[0],self.next_step[1] - self.node_digdug.pos[1]])
            else:
                print("NOT IN DIRECTION")
                if self.no_block_next_step(x,value):
                    print("NO BLOCK BETWEEN")
                    self.move = (lambda y: "d" if y == "a" else ("a" if y == "d" else ("w" if y == "s" else ("s" if y == "w" else None))))("a")
                else:
                    print("BLOCK BETWEEN")
                    self.move = comandos([self.next_step[0] - self.node_digdug.pos[0],self.next_step[1] - self.node_digdug.pos[1]])
                 
                    
        else:
            self.move = comandos([self.next_step[0] - self.node_digdug.pos[0],self.next_step[1] - self.node_digdug.pos[1]])
    #TODO: corrigir estas 2 funcoes abaixo para poder usar na decision()
    def is_in_direction(self):
        #print("TESTING DIRECTION AND BLOCK")
        x1, y1 = self.digdug.pos
        direction = self.digdug.real_dir
        x2, y2 = self.digdug.enemy.pos
        print("DIRECTION:",direction)
        if direction == "a" and x1 > x2 and y1 == y2:
            return True #, "x" , -1     #!: para no_block_between
        elif direction == "d" and x1 < x2 and y1 == y2:
            return True #,"x",+1
        elif direction == "w" and y1 > y2 and x1 == x2:
            return True #, "y",-1
        elif direction == "s" and y1 < y2 and x1 == x2:
            return True #, "y",+1
        else:
            return False #   , None, None
        
    def no_block_next_step(self): #?: vê se nas proximas 2 
        x1, y1 = self.digdug.pos
        dist = 2 #!: se mudar aqui, mudar no is_close_to_enemy
        no_block = True
        for i in range(1, dist):
            if self.path[i]:    #?: para caso a distancia entre o digdug e o enimigo seja menor que 2
                #print("PATH:",self.path[i])
                x,y = self.path[i]
                if self.digdug.domain.mapa[x][y] == 1:   
                    no_block = False
        
        return no_block
        
        
    def dist_digdug_enemy(self):
        return abs(self.digdug.pos[0] - self.digdug.enemy.pos[0]) + abs(self.digdug.pos[1] - self.digdug.enemy.pos[1])
        
    def no_block_in_path(self):
        #print("PATH <<<<<:" ,self.path)
        for i in self.path:
            x, y = i
            if x < len(self.digdug.domain.mapa) and y < len(self.digdug.domain.mapa[0]):
                if self.digdug.domain.mapa[x][y] == 1:
                    return False
        return True
        for i in range(len(self.path)):
            if self.digdug.domain.mapa[i] == 1:
                return False
        return True
    def no_block_between(self,x,signal):
        x1, y1 = self.digdug.pos
        dist = 2
        if x == "x":
            for i in range(1, dist):
                if self.digdug.domain.mapa[x1 + signal * i][y1] == 1:
                    print("BLOCK BETWEEN x")
                    return False
        elif x == "y":
            for i in range(1, dist):
                if self.digdug.domain.mapa[x1][y1 + signal * i] == 1:
                    print("BLOCK BETWEEN y")
                    return False
        else:
            print("NO BLOCK BETWEEN")
            return True
    def is_close_to_enemy(self): 
        #?: funciona
        x1, y1 = self.digdug.pos
        x2, y2 = self.digdug.enemy.pos
        dist = 2    #!: se mudar aqui, mudar no no_block_between
        if abs(x1 - x2) <= dist and abs(y1 - y2) <= dist:  #?: distancia de 2 quadrados
            #print("CLOSE TO ENEMY")
            return True