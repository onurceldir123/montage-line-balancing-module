import matplotlib.pyplot as plt
import networkx as nx
import copy
import numpy as np
import random as rd
class Line():
    def __init__(self, task_list):
        self.graph = self.draw_graph(task_list)
        self.task_list = task_list
        self.input_dictionary = self.create_input_dict(task_list)

    def get_task_time(self, task_number):
        return self.graph.nodes[task_number]['time']
    
    def draw_graph(self, task_list):
        drawed_graph = nx.DiGraph()
        # draw graph and add task times
        drawed_graph.add_node(-1, time=0)
        drawed_graph.add_node(0, time=0)
        for node in task_list:
            drawed_graph.add_node(node[0], time=node[2])
            for successors in node[1]:
                drawed_graph.add_edge(successors, node[0])

        node_list = list(nx.topological_sort(drawed_graph))
        for i in node_list:
            if (i != -1)&(len(list(drawed_graph.successors(i))) == 0):
                  drawed_graph.add_edge(i, -1)

        drawed_graph.nodes[0]['total_weight'] = 0

        #calculate total_weights
        for i in range(1, len(task_list)+1):
            node_list = list(nx.dfs_preorder_nodes(drawed_graph, source=i))
            total_weight = 0
            for node in node_list:
                total_weight += drawed_graph.nodes[node]['time']
            drawed_graph.nodes[i]['total_weight'] = total_weight

        return drawed_graph
    
    def create_graph_for_ushape(self, input_array, graph):    
        reverse_graph = nx.DiGraph()
        # draw reverse graph and addreversed task times
        reverse_graph.add_node(0, time=0)
        for node in input_x:
            for successors in node[1]:
                reverse_graph.add_node(node[0], time=node[2])
                reverse_graph.add_edge(node[0], successors)


        reverse_graph.nodes[0]['total_weight'] = 0

        #calculate reversed_total_weights
        for i in range(1, len(input_x)+1):
            node_list = list(nx.dfs_preorder_nodes(reverse_graph, source=i))
            reversed_total_weight = 0
            for node in node_list:
                reversed_total_weight += reverse_graph.nodes[node]['time']
            graph.nodes[i]['reversed_total_weight'] = reversed_total_weight

        return graph
    
    def create_input_dict(self, task_list):
        input_nodes = []
        input_weights = []

        for i in task_list:
            input_nodes.append(i[0])
            input_weights.append(i[2])

        return dict(zip(input_nodes, input_weights))
    
    def total_work_time(self, station_list_):
        total = 0
        for station in station_list_:
            for i in station:
                total +=self.get_task_time(i)
        return total
    
    def calculate_loss_balance(self, station_list, cycle_time=0):
        loss_balance = 100 - self.calculate_line_efficiency(station_list, cycle_time)
        return loss_balance
    
    def calculate_line_efficiency(self, station_list, cycle_time=0):
        # calculates station times
        station_times = []
        for i in range(len(station_list)):
            station_times.append(self.get_station_time(station_list[i]))
        if cycle_time == 0:     
            cycle_time = max(station_times)
        # calculate smootness Index
        s = 0
        for i in range(len(station_list)):
            s = s + ((np.max(station_times)-station_times[i])**2)

        smooth_index = np.sqrt(s)

        # calculate line efficiency
        line_efficiency = 100 - ((100*smooth_index)/(len(station_times)*cycle_time))

        return line_efficiency
    
    def calculate_smooth_index(self, station_list, cycle_time=0):
        # calculates station times
        station_times = []
        for i in range(len(station_list)):
            station_times.append(self.get_station_time(station_list[i]))
        if cycle_time == 0:     
            cycle_time = max(station_times)
        # calculate smootness Index
        s = 0
        for i in range(len(station_list)):
            s = s + ((np.max(station_times)-station_times[i])**2)

        smooth_index = np.sqrt(s)
        return smooth_index
        
    def get_station_time(self, station):
        total_task_time = 0
        for weight_num in station:
            total_task_time += self.input_dictionary.get(weight_num)
        return total_task_time
    # largest candidate rule
    def find_weighed_successor(self, list_):
        node_list = {}
        for node in list_:
            node_list[node] = self.graph.nodes[node]['total_weight']
        sorted_list = sorted(node_list.items(), key=lambda x: x[1], reverse=True)
        return sorted_list
    
    # helgeson-birnie method
    def find_number_successor(self, list_):
        node_list = {}
        for node in list_:
            node_list[node] = len(list(nx.dfs_preorder_nodes(self.graph, source=node)))
        sorted_list = sorted(node_list.items(), key=lambda x: x[1], reverse=True)
        return sorted_list
    
    def find_reversed_candidate_list(self, list1_, list2_, graph_):
        node_list = {}
        for node in list1_:
            node_list[node] = graph_.nodes[node]['reversed_total_weight']
        for node in list2_:
            node_list[node] = graph_.nodes[node]['total_weight']
        sorted_list = sorted(node_list.items(), key=lambda x: x[1], reverse=True)
        return sorted_list
    
    
    # lcr = largest candidate
    # hb = helgeson birnie method
    def heuristic_method(self, cycle_time, method = 'lcr'):
        G = copy.deepcopy(self.graph)
        stations = []
        station_list = []
        # find 0's successors
        is_finished = False
        while(is_finished==False):
            is_added = False
            new_successors_list = list(G.successors(0))
            for eliminate in new_successors_list:
                if (sum(list(G.predecessors(eliminate))) > 0) | (eliminate == -1):
                    new_successors_list.remove(eliminate)

            if (method == 'lcr'):
                candidate_list = self.find_weighed_successor(new_successors_list)
            else:
                candidate_list = self.find_number_successor(new_successors_list)

            node_list = {}
            for node in new_successors_list:
                node_list[node] = len(list(nx.dfs_preorder_nodes(G, source=node)))
                sorted_list = sorted(node_list.items(), key=lambda x: x[1], reverse=True)
                is_added = False

            for node_number in candidate_list:
                new_node_time = G.nodes[node_number[0]]['time']
                if self.get_station_time(stations)+new_node_time <= cycle_time:
                    is_added = True
                    stations.append(node_number[0])
                    for success_num in list(G.successors(node_number[0])):
                        G.add_edge(0, success_num)
                    G.remove_edges_from(list(G.edges(node_number[0])))
                    G.remove_edge(0,node_number[0])
                    break

            if is_added == False:
                station_list.append(stations)
                stations = []
                stations.append(candidate_list[0][0])
                for success_num in list(G.successors(candidate_list[0][0])):
                    G.add_edge(0, success_num)
                G.remove_edges_from(list(G.edges(candidate_list[0][0])))
                G.remove_edge(0, candidate_list[0][0])

            if (G.number_of_edges() == 1):
                is_finished = True
                station_list.append(stations)
            
        return station_list
    
    # B: behind, F: front
    # lcr = largest candidate
    # hb = helgeson birnie method
    def u_type_balance(self, cycle_time, method = 'lcr'):
        first = True
        G = copy.deepcopy(self.graph)
        G = self.create_graph_for_ushape(self.task_list, G)
        stations = []
        station_list = []
        front_behind_arr = []
        is_finished = False
        while(is_finished == False):
            new_successors_list = list(G.successors(0))
            new_predecessors_list = list(G.predecessors(-1))

            #feasible_list
            for eliminate in new_successors_list:
                if sum(list(G.predecessors(eliminate))) > 0:
                    new_successors_list.remove(eliminate)
            for eliminate in new_predecessors_list:
                if sum(list(G.successors(eliminate))) > 0:
                    new_predecessors_list.remove(eliminate)

            candidate_list = self.find_reversed_candidate_list(new_predecessors_list, new_successors_list, G)
            if first == True:
                candidate_list[0], candidate_list[-1] = candidate_list[-1], candidate_list[0]
                first = False
            is_added = False
            for node_number in candidate_list:
                new_node_time = G.nodes[node_number[0]]['time']
                if self.get_station_time(stations)+new_node_time <= cycle_time:
                    if (node_number[0] in new_successors_list) and (node_number[0] in new_predecessors_list):
                        front_behind_arr.append('F-B')
                        is_added = True
                        stations.append(node_number[0])
                        for success_num in list(G.successors(node_number[0])):
                            G.add_edge(0, success_num)
                        G.remove_edges_from(list(G.edges(node_number[0])))
                        G.remove_edge(0,node_number[0])
                        break
                    elif (node_number[0] in new_predecessors_list):
                        front_behind_arr.append('B')
                        is_added = True
                        stations.append(node_number[0])
                        for predecc_num in list(G.predecessors(node_number[0])):
                            G.add_edge(predecc_num, -1)
                            G.remove_edge(predecc_num, node_number[0])
                        #G.remove_edges_from(list(G.edges(node_number[0])))
                        G.remove_edge(node_number[0],-1)
                        break
                    else:
                        front_behind_arr.append('F')
                        is_added = True
                        stations.append(node_number[0])
                        for success_num in list(G.successors(node_number[0])):
                            G.add_edge(0, success_num)
                        G.remove_edges_from(list(G.edges(node_number[0])))
                        G.remove_edge(0,node_number[0])
                        break

            if is_added == False:
                station_list.append(stations)
                stations = []
                if (candidate_list[0][0] in new_successors_list) and (candidate_list[0][0] in new_predecessors_list):
                    stations.append(candidate_list[0][0])
                    front_behind_arr.append('F-B')
                    for success_num in list(G.successors(candidate_list[0][0])):
                         G.add_edge(0, success_num)
                    G.remove_edges_from(list(G.edges(candidate_list[0][0])))
                    G.remove_edge(0, candidate_list[0][0])
                elif (candidate_list[0][0] in new_predecessors_list):
                    stations.append(candidate_list[0][0])
                    front_behind_arr.append('B')
                    for predecc_num in list(G.predecessors(candidate_list[0][0])):
                        G.add_edge(predecc_num, -1)
                        G.remove_edge(predecc_num, candidate_list[0][0])
                    #G.remove_edges_from(list(G.edges(node_number[0])))
                    G.remove_edge(candidate_list[0][0],-1)
                else:
                    stations.append(candidate_list[0][0])
                    front_behind_arr.append('F')
                    for success_num in list(G.successors(candidate_list[0][0])):
                         G.add_edge(0, success_num)
                    G.remove_edges_from(list(G.edges(candidate_list[0][0])))
                    G.remove_edge(0, candidate_list[0][0])
            if (len(list(G.successors(0))) == 1) & (list(G.successors(0))[0] == -1):
                is_finished = True
                station_list.append(stations)
        return station_list, front_behind_arr
    
    ## ---------------------------------------------------------- ##
    ## ---------------------------------------------------------- ##
    ## ---------------------------------------------------------- ##
    ## ---------------------------------------------------------- ##
    def remove_non_feasibles(self, list_, G_):
        remove_list = []
        for i in range(len(list_)):
            if sum(list(G_.predecessors(list_[i]))) > 0:
                remove_list.append(i)
        for i in range(len(remove_list)):
            del list_[remove_list.pop()]
        return list_
    
    def heuristic_task_allocating(self, task_path, cycle_time):
        station_list_ = []
        station = []
        for task in task_path:
            if(self.get_station_time(station) + self.input_dictionary[task] <= cycle_time):
                station.append(task)

            else:
                station_list_.append(station)
                station = []
                station.append(task)

        station_list_.append(station)
        return station_list_
    
    def local_search_procedure(self, initial_list, cycle_time, local_search="local"):
        p_m = 0.7 
        pop = 30 
        gen = 15
        all_stations = []
        all_stations.append(initial_list)
        for i in range(pop-1):
            station_created = copy.deepcopy(initial_list)
            # probability 2: move right(k) to left(k+1), move right(k+1) to left(k+2) ...      
            k = rd.randint(0,len(station_created)-1)
            if len(station_created[k])>1:
                if(len(station_created)==k+1):
                    station_created.append([])
                station_created[k+1].insert(0, station_created[k][-1])
                station_created[k].pop()
            #bozulanları düzelt;
            for i in range(k, len(station_created)):
                isFinished = False
                while(isFinished==False):
                    if(self.get_station_time(station_created[i]) > cycle_time):
                        if(len(station_created)<=i+1):
                            station_created.append([])
                        station_created[i+1].insert(0, station_created[i][-1])
                        station_created[i].pop()
                        if(self.get_station_time(station_created[i]) <= cycle_time):
                            isFinished = True  
                    else:
                        isFinished = True 
            all_stations.append(station_created)
        if (local_search == "local"):
            unique_list_tasks = []
            for x in all_stations:
                if x not in unique_list_tasks:
                    unique_list_tasks.append(x)
            return unique_list_tasks
        elif(local_search == "genetics") :
            X0 = all_stations[:]

            generation = 1
            Save_bests  = []

            for i in range(gen):
                new_population = []

                All_in_Generation_childs = []

                All_in_Generation_childs_scores = []

                Total_Cost_Mut = self.calculate_line_efficiency(initial_list)
                All_in_Generation_childs.append(initial_list)
                All_in_Generation_childs_scores.append(Total_Cost_Mut)

                #print("----> Generation: #", generation)

                family = 1

                for j in range(int(pop)-1):
                    Parents = []
                    Warrior_1_index = np.random.randint(0,len(X0))
                    Warrior_2_index = np.random.randint(0,len(X0))
                    Warrior_3_index = np.random.randint(0,len(X0))

                    while Warrior_1_index == Warrior_2_index:
                        Warrior_1_index = np.random.randint(0, len(X0))

                    while Warrior_2_index == Warrior_3_index:
                        Warrior_3_index = np.random.randint(0, len(X0))

                    while Warrior_1_index == Warrior_3_index:
                        Warrior_3_index = np.random.randint(0, len(X0))

                    Warrior_1 = X0[Warrior_1_index]
                    Warrior_2 = X0[Warrior_2_index]
                    Warrior_3 = X0[Warrior_3_index]

                    # calculate distances for warriors
                    Prize_Warrior_1 = self.calculate_line_efficiency(Warrior_1)

                    Prize_Warrior_2 = self.calculate_line_efficiency(Warrior_2)

                    Prize_Warrior_3 = self.calculate_line_efficiency(Warrior_3)

                    if Prize_Warrior_1 == max(Prize_Warrior_1, Prize_Warrior_2, Prize_Warrior_3):
                        Winner = Warrior_1
                    elif Prize_Warrior_2 == max(Prize_Warrior_1, Prize_Warrior_2, Prize_Warrior_3):
                        Winner = Warrior_2
                    else:
                        Winner = Warrior_3

                    Parents.append(Winner)

                    parent_1 = Parents[0]
                    Mutated_Child_1 = []
                    prob_mut = np.random.rand()
                    if prob_mut < p_m:
                        Mutated_Child = self.mutation_local(parent_1, cycle_time)
                    else: 
                        Mutated_Child = parent_1

                    Total_Cost_Mut = self.calculate_line_efficiency(Mutated_Child)
                    # print('Child: ', Mutated_Child, 'Score: ', Total_Cost_Mut)
                    family += 1 

                    All_in_Generation_childs.append(Mutated_Child)
                    All_in_Generation_childs_scores.append(Total_Cost_Mut)
                    index_of_best = All_in_Generation_childs_scores.index(max(All_in_Generation_childs_scores))

                    new_population.append(Mutated_Child)
                X0 = new_population[:]
                #Save_best_in_generation.append([
                #    All_in_Generation_childs[index_of_best], 
                #    All_in_Generation_childs_scores[index_of_best]
                #])
                Save_bests.append(All_in_Generation_childs[index_of_best])

                generation += 1
            unique_list_tasks = []
            for x in Save_bests:
                if x not in unique_list_tasks:
                    unique_list_tasks.append(x)
            return unique_list_tasks
    
    def mutation_local(self, station_list_, cycle_time):
        station_created = copy.deepcopy(station_list_)
        # probability 2: move right(k) to left(k+1), move right(k+1) to left(k+2) ...      
        k = rd.randint(0,len(station_created)-1)
        if len(station_created[k])>1:
            if(len(station_created)==k+1):
                station_created.append([])
            station_created[k+1].insert(0, station_created[k][-1])
            station_created[k].pop()
        #bozulanları düzelt;
        for i in range(k, len(station_created)):
            isFinished = False
            while(isFinished==False):
                if(self.get_station_time(station_created[i]) > cycle_time):
                    if(len(station_created)<=i+1):
                        station_created.append([])
                    station_created[i+1].insert(0, station_created[i][-1])
                    station_created[i].pop()
                    if(self.get_station_time(station_created[i]) <= cycle_time):
                        isFinished = True  
                else:
                    isFinished = True 
        return station_created
    def comsoal_algorithm(self, cycle_time, iteration=100, local_search = 'heuristic'):
        generation_list = []
        for i in range(iteration):
            G = copy.deepcopy(self.graph)
            task_list = []
            is_finished = False
            while(is_finished == False):
                new_successors_list = list(G.successors(0))
                feasible_list = self.remove_non_feasibles(new_successors_list, G)
                candidate = rd.choice(feasible_list)
                # adding selected to list
                # adding selected to list
                task_list.append(candidate)
                for success_num in list(G.successors(candidate)):
                    G.add_edge(0, success_num)
                G.remove_edges_from(list(G.edges(candidate)))
                G.remove_edge(0, candidate)
                if (len(list(G.successors(0))) == 1) & (list(G.successors(0))[0] == -1):
                    is_finished = True
            #### BU KISIMA LOCAL SEARCH PROCEDURE EKLENECEK
            station_list = self.heuristic_task_allocating(task_list, cycle_time)
            if (local_search != 'heuristic'):
                station_list = line.local_search_procedure(station_list, cycle_time, local_search=local_search)
                generation_list +=station_list
            else:
                generation_list.append(station_list)
        unique_list_tasks = []
        for x in generation_list:
            if x not in unique_list_tasks:
                unique_list_tasks.append(x)
        return unique_list_tasks