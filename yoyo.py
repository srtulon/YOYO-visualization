import networkx as nx
import matplotlib.pyplot as plt
import random
import ast


flip_list=[]
delete_list=[]
inputs = []
messages = []
input_nodes = []
message =dict()
graph_visualizer = None
figures = []

class Node:
    def __init__(self, id):
        self.id = id
        self.state = 'UNKNOWN'
        self.in_links = set()
        self.out_links = set()
        self.neighbors = set()
        self.in_values = dict()
        self.out_values = list()
        self.send_done = False
        self.rec_done = False
        self.min = id
        self.prune = False

    def __repr__(self):
        return str(self.id)
    
    def add_in_link(self, link):
        self.in_links.add(link)
        self.neighbors.add(link)
        #print(str(self.id)+" adding "+str(link.id)+" as in link")

    def add_out_link(self, link):
        self.out_links.add(link)
        self.neighbors.add(link)
        input_nodes.append((self.id,link.id)) 
        #print(str(self.id)+" adding "+str(link.id)+" as out link")

    def remove_in_link(self, link):
        self.in_links.discard(link)
        self.neighbors.discard(link)
        #print(str(self.id)+" removing "+str(link.id)+" as in link")

    def remove_out_link(self, link):
        self.out_links.discard(link)
        self.neighbors.discard(link)
        #print(str(self.id)+" removing "+str(link.id)+" as out link")


    def send_id(self, other):
        other.receive_id(self)

        if len(self.in_links) == len(self.neighbors):
            self.state = 'SINK'
        elif len(self.out_links) == len(self.neighbors):
            self.state = 'SOURCE'
        elif len(self.out_links) > 0 and len(self.in_links) > 0:
            self.state = 'INTERNAL'

    def receive_id(self, other):
        if other.id > self.id:
            self.add_out_link(other)
        else:
            self.add_in_link(other)

        if len(self.in_links) == len(self.neighbors):
            self.state = 'SINK'
        elif len(self.out_links) == len(self.neighbors):
            self.state = 'SOURCE'
        elif len(self.out_links) > 0 and len(self.in_links) > 0:
            self.state = 'INTERNAL'

    def update_state(self):
        self.send_done = False
        self.rec_done = False
        self.in_values = dict()
        self.out_values = list()
        if self.state == 'SOURCE':
            if len(self.in_links) > 0 and len(self.out_links) == 0:
                self.state = 'SINK'
                print(str(self.id)+" is becoming sink")
            elif len(self.out_links) > 0 and len(self.in_links) > 0:
                self.state = 'INTERNAL'
                print(str(self.id)+" is becoming internal")
            if len(self.out_links) == 0 and len(self.in_links) == 0:
                print(str(self.id)+' becomes leader')
                self.state = 'LEADER'
                return self.id
            
        if self.state == 'INTERNAL':
            if len(self.in_links) > 0 and len(self.out_links) == 0:
                print(str(self.id)+" is becoming sink")
                self.state = 'SINK'
            if len(self.in_links) == 0 and len(self.out_links) == 0:
                self.state = "DELETED"
                print(str(self.id)+" is becoming deleted")

        if self.state == 'SINK':    
            if len(self.in_links) == 0 and len(self.out_links) == 0:
                self.state = "DELETED"
                print(str(self.id)+" is becoming deleted")
            elif len(self.out_links) > 0 and len(self.in_links) > 0:
                self.state = 'INTERNAL'
                print(str(self.id)+" is becoming internal")

        if self.state == "DELETED":  
            self.send_done = True
            self.rec_done = True

    def send_yo_message(self,other,min):
        other.receive_yo_message(self,min)

    
    def receive_yo_reply(self, other, message):
        print(str(self.state)+" "+str(self.id)+" recieved "+message+" from "+str(other.id))
        if self.state == 'INTERNAL' :
            self.out_values.append(message)

    def receive_yo_message(self, other,min):
        if  self.min > min:
            self.min = min

        if min in self.in_values:
            self.in_values[min].append(other)
        else:
            self.in_values[min]=[other]
        

    def send_yo_reply(self, other, message):
        other.receive_yo_reply(self, message)


    def process_source(self):
        if not self.send_done:
            for node in list(self.out_links):
                print(str(self.state)+" "+str(self.id)+" send "+str(self.id)+" to "+str(node.id))
                self.send_yo_message(node,self.id)
                message[(self,node)] = self.id
        self.send_done = True
        self.rec_done = True

            
    def process_internal(self):
        if sum(len(values) for values in self.in_values.values()) == len(self.in_links):
            if not self.send_done:
                for node in list(self.out_links):
                    print(str(self.state)+" "+str(self.id)+" send "+str(self.min)+" to "+str(node.id))
                    self.send_yo_message(node,self.min)
                    message[(self,node)] = self.min
            self.send_done = True
        if len(self.out_values) == len(self.out_links):
            if not self.rec_done:
                if "no" in self.out_values:
                    for node in self.in_links:
                        print(str(self.state)+" "+str(self.id)+" send no to "+str(node.id))
                        self.send_yo_reply(node,"no")
                        message[(self,node)] = "N"
                        flip_list.append((self,node))
                else:
                    counter = 1
                    for node in self.in_values[self.min]:
                        message[(self,node)] = "Y"
                        if counter >= 2:
                            if (self,node) not in delete_list:
                                delete_list.append((self,node))
                                message[(self,node)] = "Y(P)"
                        print(str(self.state)+" "+str(self.id)+" send yes to "+str(node.id))
                        self.send_yo_reply(node,"yes")
                        counter += 1
                    for node in self.in_links:
                        if node not in self.in_values[self.min]:
                            print(str(self.state)+" "+str(self.id)+" send no to "+str(node.id))
                            self.send_yo_reply(node,"no")
                            message[(self,node)] = "N"
                            flip_list.append((self,node))
                    if len(self.in_links) == 1 and len(self.out_links) == 1:
                        if self.prune:
                            last_link = next(iter(self.in_links))
                            delete_list.append((self,last_link))
                            last_link.prune = True
                            message[(self,last_link)] = "Y(P)" 

            self.rec_done = True

                
    def process_sink(self):
        if sum(len(values) for values in self.in_values.values()) == len(self.in_links):  
            self.rec_done = True
            counter = 1
            if not self.send_done:
                for node in list(self.in_links):
                    #print(self.in_values[self.min])
                    if node in self.in_values[self.min]:
                        message[(self,node)] = "Y"
                        if counter > 1 :
                            if (self,node) not in delete_list:
                                delete_list.append((self,node))
                                message[(self,node)] = "Y(P)"
                        print(str(self.state)+" "+str(self.id)+" send yes to "+str(node.id))
                        self.send_yo_reply(node,"yes")
                        counter += 1
                    else: 
                        print(str(self.state)+" "+str(self.id)+" send no to "+str(node.id))
                        self.send_yo_reply(node,"no")
                        message[(self,node)] = "N"
                        flip_list.append((self,node))
            self.send_done = True
        
            if len(self.in_links) == 1 and len(self.out_links) == 0:
                    last_link = next(iter(self.in_links))
                    delete_list.append((self,last_link))
                    last_link.prune = True
                    message[(self,last_link)] = "Y(P)"


def yo_yo_algorithm(node_mapping):
    global flip_list, delete_list, input_nodes, inputs, messages, message, figures
    for node in node_mapping:
        if node_mapping[node].state == 'UNKNOWN':
            for neighbor in node_mapping[node].neighbors:
                node_mapping[node].send_id(neighbor)

    while any(node_mapping[node].state != 'LEADER' and node_mapping[node].state != 'DELETED' for node in node_mapping):
        for node in node_mapping:
            if node_mapping[node].state == 'SOURCE':
                node_mapping[node].process_source()
                #print(str(node)+ " "+str(node_mapping[node].state))
                graph_visualizer.update_graph()
                figures.append(graph_visualizer.draw_graph(node_mapping, message))
                continue
        for node in node_mapping:
            if node_mapping[node].state == 'INTERNAL':
                node_mapping[node].process_internal()
                #print(str(node)+ " "+str(node_mapping[node].state))
                graph_visualizer.update_graph()
                figures.append(graph_visualizer.draw_graph(node_mapping, message))
                continue
        for node in node_mapping:
            if node_mapping[node].state == 'SINK':
                node_mapping[node].process_sink()
                #print(str(node)+ " "+str(node_mapping[node].state))
                graph_visualizer.update_graph()
                figures.append(graph_visualizer.draw_graph(node_mapping, message))
                continue
            
        for node in node_mapping:
            if node_mapping[node].state == 'INTERNAL':
                node_mapping[node].process_internal()
                #print(str(node)+ " "+str(node_mapping[node].state))
                graph_visualizer.update_graph()
                figures.append(graph_visualizer.draw_graph(node_mapping, message))
                continue

        if all(node_mapping[node].send_done for node in node_mapping):
            graph_visualizer.update_graph()
            figures.append(graph_visualizer.draw_graph(node_mapping, message))

            if all(node_mapping[node].rec_done for node in node_mapping):
                for to_flip in flip_list:
                    to_flip[0].remove_in_link(to_flip[1])
                    to_flip[0].add_out_link(to_flip[1])
                    to_flip[1].remove_out_link(to_flip[0])
                    to_flip[1].add_in_link(to_flip[0])

                for to_delete in delete_list:
                    to_delete[0].remove_in_link(to_delete[1])     #pruning
                    to_delete[1].remove_out_link(to_delete[0])
                
                for node in node_mapping:
                    node_mapping[node].update_state()
                    #print(str(node_mapping[node])+" "+str(node_mapping[node].state)+" "+str(node_mapping[node].in_links)+" "+str(node_mapping[node].out_links))
                flip_list = []
                delete_list = []
                input_nodes = [] 
                message = dict()
                inputs.append(input_nodes)
                messages.append(message)

        for node in node_mapping:
            if node_mapping[node].state == 'LEADER' and len(node_mapping[node].in_links) == 0 and len(node_mapping[node].out_links) == 0:
                graph_visualizer.update_graph()
                figures.append(graph_visualizer.draw_graph(node_mapping, message))
                return node_mapping[node]
            


class GraphVisualizer:
    def __init__(self, edge_list):
        self.all_nodes = self.create_nodes(edge_list)
        self.all_G = self.create_graph(edge_list, self.all_nodes)
        self.pos = self.compute_positions(self.all_G)
        self.fig = plt.figure()
        self.graph_edge_changed = False
        self.previous_edge_labels = None

    def create_nodes(self, edge_list):
        nodes = {}
        for edge in edge_list:
            if edge[0] not in nodes:
                nodes[edge[0]] = Node(edge[0])
            if edge[1] not in nodes:
                nodes[edge[1]] = Node(edge[1])
        return nodes

    def draw_undirected_graph(self, edge_list):
        G = nx.Graph()
        for src_id, dst_id in edge_list:
            G.add_edge(self.all_nodes[src_id], self.all_nodes[dst_id])
        fig, ax = plt.subplots()
        nx.draw(G, self.pos, with_labels=True, node_color='skyblue', font_weight='bold',connectionstyle='arc3, rad=0.1')
        return fig
        #plt.pause(3)
    
    def create_graph(self, edge_list, nodes):
        G = nx.DiGraph()
        
        for edge in edge_list:
            src, dst = edge
            if src > dst:
                G.add_edge(nodes[dst], nodes[src])
                nodes[src].add_in_link(nodes[dst])
                nodes[dst].add_out_link(nodes[src])
            else:
                G.add_edge(nodes[src], nodes[dst])
                nodes[src].add_out_link(nodes[dst])
                nodes[dst].add_in_link(nodes[src])
                
        return G
    
    def update_graph(self):
        
        current_edges = list(self.all_G.edges)
        self.all_G.remove_edges_from(list(self.all_G.edges))

        for node in self.all_nodes.values():
            for in_node in node.in_links:
                self.all_G.add_edge(in_node, node)
            for out_node in node.out_links:
                self.all_G.add_edge(node, out_node)

        if current_edges != list(self.all_G.edges) :
            self.graph_edge_changed = True
        else:
            self.graph_edge_changed = False

    def compute_positions(self, G):
        return nx.circular_layout(G)

    def draw_graph(self, edge_list, edge_labels):
        deleted = []
        source = [] 
        sink = []
        for node in self.all_nodes.values():
            if node.state == 'SINK':
                sink.append(node)
            if node.state == 'SOURCE':
                source.append(node)
            if node.state == 'DELETED':
                deleted.append(node)

        #plt.clf()
        fig, _ = plt.subplots()
        nx.draw(self.all_G, self.pos, with_labels=True, node_color='skyblue', font_weight='bold', arrowsize=20)
        nx.draw_networkx_nodes(self.all_G, self.pos, nodelist=sink, node_shape='s',  node_color='skyblue')
        nx.draw_networkx_nodes(self.all_G, self.pos, nodelist=source,  node_color='skyblue', linewidths=2, edgecolors='black')
        nx.draw_networkx_nodes(self.all_G, self.pos, nodelist=deleted,node_color='red')
        nx.draw_networkx_edge_labels(self.all_G, self.pos, edge_labels=edge_labels, label_pos=0.75, font_size=8)
        #plt.pause(.1)
        if self.graph_edge_changed == True:
            self.graph_edge_changed = False
            return fig
        elif self.previous_edge_labels != edge_labels:
            self.previous_edge_labels = edge_labels.copy()
            return fig
        else:
            return None
        

def generate_graph(num_nodes):

    nodes = list(range(1, num_nodes+1))
    random.shuffle(nodes)
    edges = set((nodes[i], nodes[i+1]) for i in range(num_nodes-1))
    for i in range(1, num_nodes+1):
        for j in range(i+1, num_nodes+1):
            if (i, j) not in edges and random.uniform(0, 1) < 0.3:
                edges.add((i, j))
    return list(edges)

def check_input_format(input_node):
    try:
        input_list = eval(input_node, {'__builtins__': None}, {})
        if not isinstance(input_list, list):
            return False
        
        for item in input_list:
            if not isinstance(item, tuple) or len(item) != 2:
                return False
            if not (isinstance(item[0], int) and isinstance(item[1], int)):
                return False
                
        return True
    
    except Exception:
        return False


def call_yoyo():
    global graph_visualizer, figures
    while True:
        user_input = input('Would you want a random graph? (yes/no) Press enter for yes : ')

        if user_input.lower() == 'yes' or user_input.lower() == 'y' or user_input.lower() == '':
            node_num = int(input('How many nodes do you want? '))
            while node_num < 2:
                node_num = int(input("Please enter a number at least equal or greater than 2 : "))
            input_node = generate_graph(node_num)
            break
        elif user_input.lower() == 'no' or user_input.lower() == 'n':
            input_node = input('Please input your graph: ')
            while not check_input_format(input_node):
                input_node = input('Please input correct graph : ')
            input_node = ast.literal_eval(input_node)
            break
        else:
            print('Please type yes or no')

    #[(1, 2), (2, 3), (3, 4), (1, 3), (2, 4),(5,9),(5,6),(5,7),(7,8),(8,6),(3,6),(6,9),(2,4),(2,7),(4,3),(1,2),(1,4),(1,7),(4,7)]
    #[(1, 2), (2, 3), (3, 1), (4, 1), (4, 2), (4, 3)],
    #[(1, 3), (3, 4), (4, 1), (1, 2), (2, 3)],
    #[(5,9),(5,6),(5,7),(7,8),(8,6),(3,6),(6,9),(2,4),(2,7),(4,3),(1,2),(1,4)]
    #[(3,11),(3,14),(3,12),(11,12),(5,11),(5,12),(5,20),(12,20),(4,14),(4,20),(41,20),(20,7),(31,7),(2,31)]

    graph_visualizer = GraphVisualizer(input_node)
    node_mapping = graph_visualizer.all_nodes

    figures.append(graph_visualizer.draw_undirected_graph(input_node))

    leader = yo_yo_algorithm(node_mapping)
    print("Leader:", leader)

    i = 0
    for fig in figures:
        if fig != None:
            fig.savefig(str(i)+'.png')
            i+=1

call_yoyo()
