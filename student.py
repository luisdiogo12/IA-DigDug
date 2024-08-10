import asyncio
import getpass
import json
import os
import websockets
class Domain:
    def __init__(self,level = None,mapa=None, size=None, rocks = None, enemies = None):
        self.map = map								#?: mapa com valores do custo por idice
        self.real_map = map
        self.level = level
        self.size = size									
        self.map_coordinates = None		#?: contem todas as coordenadas do mapa, funcao de suporte
        self.rocks = rocks								#?: contem todas as rochas em entidades Rock
        self.enemies = enemies							#?: contem todos os enimigos em entidades Enemy
        self.inf_digdug = []                            #?: 0-pos 1-real_dir
        
    def in_map(self, x, y):								
        return 0 <= x < self.size[0] and 0 <= y < self.size[1]
    def atualize_map(self,state_map,state_size,state_level):
        self.clear_domain()
        self.level = state_level
        self.map = state_map
        self.real_map = state_map
        self.size = state_size
        self.map_coordinates = list([x, y] for x in range(state_size[0]) for y in range(state_size[1]))
        
    def clear_domain(self):								#?: para limpar o mapa quando muda de nivel
        self.enemies = None
        self.rocks = None
        
    def dist_digdug_enemy(self,enemy_pos):    
        return abs(self.inf_digdug[0][0] - enemy_pos[0]) + abs(self.inf_digdug[0][1] - enemy_pos[1]) 
    def dir_r_entinty(self,entity_pos,target_pos):
            r_dir = [target_pos[0] - entity_pos[0],target_pos[1] - entity_pos[1]]
            if r_dir[0] != 0:
                r_dir[0] = r_dir[0]//abs(r_dir[0])
            if r_dir[1] != 0:
                 r_dir[1] = r_dir[1]//abs(r_dir[1])
            return r_dir
    def rno_block_in_front(self,pos,dir_r): 
        xx,xy = [pos[0] + dir_r[0],pos[1]]
        yx,yy = [pos[0],pos[1] + dir_r[1]] 
        if dir_r[0] == 0:
            if self.in_map(yx, yy):
                if self.real_map[yx][yy] == 1:
                    return 0 
                if self.real_map[yx][yy] == 0:
                    return 2
        elif dir_r[1] == 0:
            if self.in_map(xx, xy):
                if self.real_map[xx][xy] == 1:
                    return 0
                if self.real_map[xx][xy] == 0:
                    return 1
        else:
            if self.in_map(xx, xy) and self.in_map(yx, yy):
                if self.real_map[xx][xy] == 1 and self.real_map[yx][yy] == 1:
                    return 0
            if self.in_map(xx, xy) and self.in_map(yx, yy):
                if self.real_map[xx][xy] == 0 and self.real_map[yx][yy]  == 1:
                    return 1
            elif self.in_map(xx, xy) and not self.in_map(yx, yy):
                if self.real_map[xx][xy] == 0 :
                    return 1
            if self.in_map(xx, xy) and self.in_map(yx, yy):
                if self.real_map[xx][xy] == 1 and self.real_map[yx][yy]  == 0:
                    return 2
                elif not self.in_map(xx, xy) and self.in_map(yx, yy):
                    if self.real_map[yx][yy]  == 0:
                        return 2
            return 3 
    def atualize_enemies(self,state_enemies):   #state_enemies = state["enemies"]
        def find_neg_one(vs):
            for x in range(len(vs)):
                for y in range(len(vs[x])):
                    if vs[x][y] == -1:
                        return [x, y]
        def sum_lists(values,list):
            p_i = find_neg_one(list)
            for x in range(len(list)):
                for y in range(len(list[x])):
                        pos_r = [x-p_i[0],y-p_i[1]]
                        vx,vy = [3+pos_r[0],3+pos_r[1]]
                        values[vx][vy] += list[x][y]
            values[3][3] = -1
            return values

        #?: funcao para atualizar os inimigos e juntamente o mapa
        if not self.enemies:  #?: quando ainda n existem inimigos no domain
            enemies = []
            for enemy in state_enemies: 
                enemies.append(Enemy(enemy["id"],enemy["name"],enemy["pos"],enemy["dir"]))
            self.enemies = enemies
        else:
            next_map = [list(sublista) for sublista in self.real_map]  #?: copia do mapa para se tornar no proximo mapa
            self.enemies = [enemy for enemy in self.enemies if any(e["id"] == enemy.id for e in state_enemies)] #+: remove enimigos que ja n aparecam no state (aka mortos)
            for state_enemy in state_enemies:
                for domain_enemy in self.enemies:
                    if state_enemy["id"] == domain_enemy.id:
                        #+: atualiza o inimigo
                        domain_enemy.atualize_pos(state_enemy["pos"],self.real_map[state_enemy["pos"][0]][state_enemy["pos"][1]])
                        domain_enemy.atualize_dir(state_enemy['dir']) 
                        if 'fire' in state_enemy and state_enemy['fire']:
                            
                            domain_enemy.atualize_fire(state_enemy["fire"])
                            
                       
                        #+: atualiza o mapa
                        dist_digdug_enemy = self.dist_digdug_enemy(domain_enemy.pos)
                        
                        values =[[0,0,0,0,0,0,0],[0,0,0,0,0,0,0],[0,0,0,0,0,0,0],[0,0,0,-1,0,0,0],[0,0,0,0,0,0,0],[0,0,0,0,0,0,0],[0,0,0,0,0,0,0]]
                        dir_r = self.dir_r_entinty(domain_enemy.pos,self.inf_digdug[0])
                        fogo = [[[   0, 1000,    0],[   0, 1000,    0],[  0, 1000,   0],[   0,   -1,    0],[   0,    0,    0]],[[   0,    0,   0,    0,    0],[   0,   -1, 1000, 1000, 1000],[   0,    0,   0,    0,    0]],[[   7,    7,    7],[   0,   -1,    0],[  0, 1000,   0],[   0, 1000,    0],[   0, 1000,    0]],[[   0,    0,   0,    0,    0],[1000, 1000, 1000,   -1,    0],[   0,    0,   0,    0,    0]]]
                        direcoes = [[[7, 100, 7], [0, -1, 0], [0, 0, 0]],[[0, 0, 7], [0, -1, 100], [0, 0, 7]], [[0, 0, 0], [0, -1, 0], [7, 100, 7]],[[7, 0, 0], [100, -1, 0], [7, 0, 0]]]
                        no_block = self.rno_block_in_front(domain_enemy.pos,dir_r)
                        
                        if domain_enemy.type == "Pooka" and domain_enemy.in_teleport == True:
                            v = [[20, 20, 20], 
                                 [20, -1, 20], 
                                 [20, 20, 20]]
                            values = sum_lists(values,v)
                            
                        
                        if dist_digdug_enemy <= 2:
                                x,y = dir_r
                                #if no_block == 0:
                                #    values = [[-1]]
                                if no_block == 1 or no_block == 3:   #noblockx or blockxy
                                    if x == 1:
                                        values = sum_lists(values,direcoes[1])
                                    if x == -1:
                                         values = sum_lists(values,direcoes[3])
                                if no_block == 2 or no_block == 3:   #noblocky or blockxy
                                    if y == 1:
                                        values = sum_lists(values,direcoes[2])
                                    if y == -1:
                                         values = sum_lists(values,direcoes[0])
                        if domain_enemy.type == "Fygar":
                            if dist_digdug_enemy <= 5:
                                x,y = dir_r
                                values = sum_lists(values,fogo[domain_enemy.dir])
                            if domain_enemy.fire !=[]:
                                for fire in domain_enemy.fire:
                                    next_map[fire[0]][fire[1]] += 1000
                        p_i = find_neg_one(values)
                        for x in range(len(values)):
                            for y in range(len(values[x])):
                                
                                pos_r = [x-p_i[0],y-p_i[1]]
                                mx,my = [domain_enemy.pos[0]+pos_r[0],domain_enemy.pos[1]+pos_r[1]]
                                if self.in_map(mx, my):
                                    next_map[mx][my] += values[x][y]
            self.map = next_map
    def atualize_rocks(self,state_rocks):   #state_rocks = state["rocks"]

        values = [[0,0,0],
                  [20,100,20],
                  [20,1000,20]]
        p_i = [1,1]
        if self.rocks == None:  #?: caso o mapa ainda n tenha rochas
            rocks = []
            for rock in state_rocks:
                x,y = rock["pos"]       
                rocks.append(Rock(rock["pos"], rock['id']))
                for x in range(len(values)):
                    for y in range(len(values[x])):
                        pos_r = [x-p_i[0],y-p_i[1]]
                        mx,my = [rock["pos"][0]+pos_r[0],rock["pos"][1]+pos_r[1]]
                        if self.in_map(mx, my):
                            self.map[mx][my] += values[x][y]
            self.rocks = rocks
        else:
            self.rocks = [rock for rock in self.rocks if any(r["id"] == rock.id for r in state_rocks)] #?: para remover rochas que ja n aparecam no state (aka novo nivel/mapa)
            for state_rock in state_rocks:
                for domain_rock in self.rocks:
                    if state_rock["id"] == domain_rock.id:
                        domain_rock.atualize_pos(state_rock["pos"])
                        
                    for x in range(len(values)):
                        for y in range(len(values[x])):
                            pos_r = [x-p_i[0],y-p_i[1]]
                            mx,my = [domain_rock.pos[0]+pos_r[0],domain_rock.pos[1]+pos_r[1]]
                            if self.in_map(mx, my):
                                self.map[mx][my] += values[x][y]
                            
                            
    def positions(self,digdug_pos):
        actlist = []
        for dx, dy in [[1, 0], [-1, 0], [0, 1], [0, -1]]:
            neighbor_coordinate = [digdug_pos[0] + dx, digdug_pos[1] + dy]
            if neighbor_coordinate in self.map_coordinates:
                actlist.append(neighbor_coordinate)
        return actlist 
    def satisfies(self, digdug_pos, enemy_pos):			
        if digdug_pos == enemy_pos:
            return True
        else:
            return False
    
    def cost(self, pos):              
        cost = self.map[pos[0]][pos[1]]
        return cost
    
    def heuristic(self, newnode_pos, goal_pos):						
        heuristic = abs(goal_pos[0] - newnode_pos[0]) + abs(goal_pos[1] - newnode_pos[1]) + self.map[newnode_pos[0]][newnode_pos[1]]    #?: heuristica com o custo do mapa
        return heuristic

# Nos de uma arvore de pesquisa
class Enemy:  
    def __init__(self,id,type,pos,dir,real_dir=None,last_pos=None,fire = None,in_teleport=False):
        self.type = type
        self.id = id
        self.last_pos = last_pos
        self.pos = pos                      		
        self.dir = dir
        self.real_dir = real_dir
        if self.type == "Fygar":
            self.fire = []
        else:
            self.fire = None
        self.in_teleport = in_teleport
        self.rastro = []						#?: fifo das ultimas 3 posicoes, caso futuro
        
    def atualize_dir(self,dir):
        self.dir = dir
    def atualize_teleport(self,real_map_value):
        if self.type == 'Pooka':
            if real_map_value == 1:
                self.in_teleport = True
            else:
                self.in_teleport = False
    def atualize_pos(self,new_pos,real_map_value):					#?:UTILIZAR ESTA FUNCAO PARA INTRODUZIR A NOVA POSICAO
        self.last_pos = self.pos
        self.pos = new_pos
        real_dir = [self.pos[0] - self.last_pos[0],self.pos[1] - self.last_pos[1]]
        if real_dir == [-1,0] or real_dir == [1,0] or real_dir == [0,1] or real_dir == [0,-1]:     #?: so muda o real_dir quando se move
            self.real_dir = real_dir
        if real_dir == [0,0] and self.real_dir == None:         #?: caso n se mexa na primeira iteracao
            if self.dir == 3:                       #a
                self.real_dir = [-1,0]
            elif self.dir == 1:                   #d
                self.real_dir = [1,0]
            elif self.dir == 0:                   #w
                    self.real_dir = [0,1]
            elif self.dir == 2:                   #s
                self.real_dir = [0,-1]
        #?: atualizar in_teleport, fire
        self.atualize_teleport(real_map_value)
        #?: atualizar rastro
        if len(self.rastro) < 3:
            self.rastro.append(new_pos)
        else:
            self.rastro.pop(0)
            self.rastro.append(new_pos)
            
    def atualize_fire(self,state_fire):
        if self.type == "Fygar":        
            self.fire = state_fire
        
    def __str__(self):
            return "ENEMY(" + str(self.pos) + "," + str(self.real_dir) + ")"
class Rope:
    def __init__(self,dir,pos=[]):
        self.pos = pos								#?: vetores das varias posicoes da corda
        self.dir = dir
class Rock:
    def __init__(self,pos,id):
       self.pos = pos     
       self.id = id   
    def atualize_pos(self,pos):
        self.pos = pos
class DigDug:  
    def __init__(self, domain = None,last_pos = None, pos = None,dir = None, rope=None, enemy = None, real_dir = None):
        self.domain = domain
        self.last_pos = last_pos															#?: = None quando o jogo começa
        self.pos = pos
        self.real_dir = real_dir
        self.rope = rope
        self.enemy = enemy																	#?: enimigo que se vai focar
    
    def goal_test(self,node_pos):   #?: se o digdug estiver na mesma posicao que o inimigo
        if not self.enemy == None:
            return self.enemy.pos == node_pos
    
    def atualize_pos(self,new_pos): #state["digdug"] apenas tem a posicao
        self.last_pos = self.pos
        self.pos = new_pos
        x,y = self.pos
        self.domain.real_map[x][y] = 0					
        self.domain.map[x][y] = 0					    
        if self.last_pos != None:
            real_dir = [self.pos[0] - self.last_pos[0],self.pos[1] - self.last_pos[1]]
            if not real_dir == [0,0]:      #?: so muda o real_dir quando se move
                self.real_dir = real_dir
        self.domain.inf_digdug = [new_pos,self.real_dir]
    def atualize_enemy(self):   
        if self.enemy and not any(e.id == self.enemy.id for e in self.domain.enemies):         #?: se o inimigo tiver morrido nao aparece no state e é removido do digdug
                self.enemy = None                                                              #?: serve mais para prevenir erros(na passagem de niveis), pois é sempre escolhido um inimigo
        self.chose_enemy()
    def chose_enemy(self):        													                               
        if self.domain.enemies:   		#?: apenas para confirmar que existe inimigos        
            #self.enemy = next((enemy for enemy in self.domain.enemies if not enemy.in_teleport), None)
            self.enemy = next((enemy for enemy in self.domain.enemies), None)  
            #if self.enemy is not None: #?: para mudar de inimigo caso um outro se aproxime
            dist = self.dist_digdug_enemy(self.enemy.pos)
            dir_r = self.domain.dir_r_entinty(self.pos,self.enemy.pos)
            for enemy in self.domain.enemies:
                new_dist =  self.dist_digdug_enemy(enemy.pos)
                new_dir_r = self.domain.dir_r_entinty(self.pos,self.enemy.pos)
                if new_dist <= dist:
                    if new_dist == dist and new_dist <= 2:
                        if self.real_dir != dir_r:      # nao esta direcionado para ele
                            dist = new_dist
                            dir_r = new_dir_r
                    else:
                        dist = new_dist
                        dir_r = new_dir_r
                    self.enemy = enemy
    
    def dist_digdug_enemy(self,enemy_pos):   
        return abs(self.pos[0] - enemy_pos[0]) + abs(self.pos[1] - enemy_pos[1])
    
    def __str__(self):
            return "DIGDUG(" + str(self.pos) + "," + str(self.enemy) + ")"
class SearchNode:   												
    def __init__(self,pos,heuristic=None,cost = None, parent=None, depth=0):
        self.pos = pos                      						#?: posicao: coordenadas correspondente no mapa [x,y]
        self.heuristic = heuristic
        self.cost = cost
        self.parent = parent
        self.depth = 0
    
    def __str__(self):
        return "sn(" + str(self.pos) + "," + str(self.heuristic) + "," + str(self.parent) + ")"
#?:PESQUISA FEITA SOBRE O QUE O DIGDUG SABE (DOMINIO(MAPA,INIMIGOS,ROCHAS),POSICAO,INIMIGO A MATAR,ROPE)
class SearchTree:   										
    def __init__(self,digdug = None): 
        self.digdug = digdug
        self.node_digdug = None
        self.open_nodes = []
        self.solution_nodes = None
        self.path = None
        self.move = None
        self.terminals = 0
        self.non_terminals = 0
        self.avg_branching = 0
    
    def search_init(self):
        if self.digdug.enemy == None:           						#?: se n tiver enimigo n executa a search, espera pela proxima
            return "no enemy, next iteration"
        self.node_digdug = SearchNode(pos = self.digdug.pos, heuristic=self.digdug.domain.heuristic(self.digdug.pos, self.digdug.enemy.pos),cost = 0,depth = 0)
        self.open_nodes = [self.node_digdug]
        self.solution_nodes = None
        self.path = None
        self.terminals = 0
        self.non_terminals = 0
        self.avg_branching = 0
        move = self.decision()
        return move 
    def get_path(self,node):
        if node.parent == None:
            return [node.pos]
        path = self.get_path(node.parent)
        path += [node.pos]
        return(path)
    def search(self):
        limit = 5
        if self.digdug.enemy == None:           						#?: se n tiver enimigo n executa a search, espera pela proxima
            return "Error: no enemy"
        while self.open_nodes != []:
            self.terminals = len(self.open_nodes)
            node = self.open_nodes.pop(0)
            if self.digdug.goal_test(node.pos) or\
               node.depth>=limit:               #?: goal é ter a path até ao enimigo, contrariamente ao search que é quando o inimigo estiver morto aka none
                self.solution_node = node
                self.path = self.get_path(node)
                return "found"
            self.non_terminals += 1
            new_nodes = []
            for a in self.digdug.domain.positions(node.pos):  
                newnode_pos = a
                if newnode_pos not in self.get_path(node): #?: para n calcular paths que ja foram calculados
                    newnode = SearchNode(newnode_pos, parent=node)
                    newnode.heuristic = self.digdug.domain.heuristic(newnode.pos,self.digdug.enemy.pos)
                    newnode.cost = node.cost + self.digdug.domain.cost(a)
                    newnode.depth = node.depth + 1
                    new_nodes.append(newnode)
            self.add_to_open(new_nodes)
        return "Error: no solution"
            
    
    def add_to_open(self,new_nodes):
        open_nodes = self.open_nodes + new_nodes
        sorted_open_nodes_greedy = sorted(open_nodes, key=lambda node: (node.heuristic))                                    #+: greedy
        sorted_open_nodes_a_star = sorted(open_nodes, key=lambda node: node.cost + node.heuristic) 
        self.open_nodes = sorted_open_nodes_a_star
    
    def decision(self):
        def comandos(move):
            if move[0] == 1 and move[1] == 0:	    #>
                return "d"
            elif move[0] == -1 and move[1] == 0:	#<
                return "a"
            elif move[1] == 1 and move[0] == 0:	    #˅
                return "s"
            elif move[1] == -1 and move[0] == 0:    #^
                return "w"
            else:
                return ""
        if self.digdug.enemy == None:
            return "no enemy, next iteration"
        if self.digdug.real_dir != None:
            dist = self.digdug.domain.dist_digdug_enemy(self.digdug.enemy.pos)
            dir_r = self.digdug.domain.dir_r_entinty(self.digdug.pos,self.digdug.enemy.pos)   # dir relativa, para o digdug contra o inimigo
            real_dir = self.digdug.real_dir
            no_block = self.digdug.domain.rno_block_in_front(self.digdug.pos,real_dir)
            if self.digdug.enemy.type == "Pooka" and self.digdug.enemy.in_teleport != True\
                or self.digdug.enemy.type == "Fygar":
                if dist == 3:     
                    real_dir2 = [(dist-1) * num for num in real_dir]
                    no_block2 = self.digdug.domain.rno_block_in_front(self.digdug.pos,real_dir2)
                    if no_block != 0 and no_block2 != 0 and\
                    (dir_r[0] == real_dir[0] or dir_r[1] == real_dir[1]):
                        return "A"   
                if dist == 2:
                    no_blockxy = self.digdug.domain.rno_block_in_front(self.digdug.pos,dir_r)
                    if no_blockxy != 3:
                            return "A"
                    elif no_block != 0 and\
                    (dir_r[0] == real_dir[0] or dir_r[1] == real_dir[1]):
                        return "A"
                    elif no_block == 0 and dir_r == real_dir:   # d>#e
                        return "A"
                if dist == 1:
                    if self.digdug.rope != None:
                        if real_dir == dir_r and self.digdug.rope.pos != []:
                            return "A"
                    else:
                        next_pos = self.digdug.pos
                        for a in self.digdug.domain.positions(self.digdug.pos):
                            val = self.digdug.domain.map[a[0]][a[1]]
                            if val >= 7 and val <= self.digdug.domain.map[next_pos[0]][next_pos[1]] and val < 999:
                                next_pos = a
                        return comandos([next_pos[0] - self.digdug.pos[0],next_pos[1] - self.digdug.pos[1]])

        search_inf = self.search()
        if search_inf != "found":
            return ""
        if len(self.path) == 1 :
            return ""               # esta morto
        else:
            next_step = self.path[1]
            return comandos([next_step[0] - self.node_digdug.pos[0],next_step[1] - self.node_digdug.pos[1]])

domain = Domain();
digdug = DigDug();
digdug.domain = domain
st = SearchTree(digdug) #?: a search fica sempre a mesma para caso precise memoization
    
def state_inf(state):                                         
    #?: a atualizacao do mapa é feita quando muda de nivel                                                                
    if 'map' in state and 'size' in state and 'level' in state:
        domain.atualize_map(state['map'],state['size'],state['level'])
    if 'digdug' in state:
        digdug.atualize_pos(state['digdug'])    #?: tem que ser antes do atualize anemies para o domain saber a posicao do digdug     
    if 'enemies' in state:
        domain.atualize_enemies(state['enemies'])   #?:atualiza a posicao(real_dir,teleport,fire,rastro) ,direcao e valores no mapa
        digdug.atualize_enemy() #?: o choose enemy vai ser feito aqui, sendo assim feito em cada iteração
    if 'rocks' in state:
        domain.atualize_rocks(state['rocks'])   #?:se n houverem rocks, cria. Se houverem atualiza posicao e valores no mapa
    if 'rope' in state:
        if not digdug.rope:
            digdug.rope = Rope(state['rope']['pos'],state['rope']['dir'])
        else:
            digdug.rope.pos = state['rope']['pos']
            digdug.rope.dir = state['rope']['dir']
    
async def agent_loop(server_address="localhost:8000", agent_name="student"):
    async with websockets.connect(f"ws://{server_address}/player") as websocket:
        await websocket.send(json.dumps({"cmd": "join", "name": agent_name}))
        key = ""
        while True:
            try:
                state = json.loads(													#?: receive game update, this must be called timely 
                    await websocket.recv()											#?:or your game will get out of sync with the server
                )  
                
                state_inf(state)#?: atualiza o estado do jogo- map(real_map,map,level), digdug(pos,enemy,map), enemy(pos,fire,teleport,map), rope, rocks
                
                if domain.level:
                    key = st.search_init() #?: encontra path, return de erros    
                    
                if key == None:
                    key = ""
                await websocket.send(												#?: send key command to server - you must implement
                    json.dumps({"cmd": "key", "key": key})							#?:this send in the AI agent
                )             
            except websockets.exceptions.ConnectionClosedOK:
                print("Server has cleanly disconnected us")
                return
# DO NOT CHANGE THE LINES BELLOW
# You can change the default values using the command line, example:
# $ NAME='arrumador' python3 client.py
loop = asyncio.get_event_loop()
SERVER = os.environ.get("SERVER", "localhost")
PORT = os.environ.get("PORT", "8000")
NAME = os.environ.get("NAME", getpass.getuser())
loop.run_until_complete(agent_loop(f"{SERVER}:{PORT}", NAME))