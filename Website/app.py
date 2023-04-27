import requests
import streamlit as st
import graphviz
import csv
import math
import streamlit_toggle as tog
from streamlit_lottie import st_lottie
from streamlit_agraph import agraph, Node, Edge, Config
from PIL import Image
import heapq
import time


# Find more emojis here: https://www.webfx.com/tools/emoji-cheat-sheet/
st.set_page_config(page_title="ReelMe", page_icon="🍿", layout="centered")

def v_spacer(height, sb=False) -> None:
    for _ in range(height):
        if sb:
            st.sidebar.write('\n')
        else:
            st.write('\n')

def load_lottieurl(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

lottie_coding = load_lottieurl("https://assets5.lottiefiles.com/private_files/lf30_bb9bkg1h.json")

lottie_coding1 = load_lottieurl("https://assets2.lottiefiles.com/packages/lf20_NEId4v1Sv3.json")


# Use local CSS
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("style/style.css")

### BACKEND

def find_movies(edge_data):
    uniques = []
    for edge in edge_data:
        if not edge[0] in uniques:
            uniques.append(edge[0])
        if not edge[1] in uniques:
            uniques.append(edge[1])
    return uniques

def read_edge_file(filename):
    edges = []
    with open(filename) as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            from_movie = row[0]
            to_movie = row[1]
            weight = row[2]
            edges.append([from_movie, to_movie, weight])
    return edges

edge_data = read_edge_file("data/test_edges.csv")
movie_displays = find_movies(edge_data)

# ------------ USE FRONT-END  -------------



construction_start = 0
construction_end = 0

search_start = 0
search_end = 0

# ADJACENCY MATRIX DATA STRUCTURE AND SEARCH ALGORITHM
class AdjacencyMatrix:
    def __init__(self, edges, movies):
        self.graph: dict[str, dict[str, float]]
        self.graph = {}
        for movie in movies:
            self.graph[movie] = {}
        for row in self.graph:
            for movie in movies:
                self.graph[row][movie] = 0.0
        for edge in edges:
            self.add_connection(edge[0], edge[1], edge[2])

    def add_connection(self, from_vertex, to_vertex, weight):
        if from_vertex not in self.graph:
            self.graph[from_vertex] = {}
            self.graph[from_vertex][from_vertex] = 0.0
        if to_vertex not in self.graph:
            self.graph[to_vertex] = {}
            self.graph[to_vertex][to_vertex] = 0.0
        self.graph[from_vertex][to_vertex] = weight
        self.graph[to_vertex][from_vertex] = weight

    def print_connections(self):
        for v in self.graph:
            print(v)
            print(self.graph[v])

    def bidirectional_search(self, targets):
        hits = {}
        visits = {}
        distances = {}
        previous = {}
        heap = {}

        num_to_hit = len(targets)

        middle_point = "null"

        for root in targets:
            previous[root] = {}
            distances[root] = {}
            distances[root][root] = -1
            hits[root] = 0
            heap[root] = [(-1, root)]
            visits[root] = []

        while True:
            for root in targets:
                #print("Dijking", root)
                #print("Heap", heap[root])
                (minimum_weight, choice) = heapq.heappop(heap[root])
                empty = False
                if choice in visits[root] or (choice in targets and choice != root):
                    if len(heap[root]) == 0:
                        continue
                    while choice in visits[root] or choice in targets:
                        (minimum_weight, choice) = heapq.heappop(heap[root])
                        if len(heap[root]) == 0:
                            empty = True
                            break
                if empty:
                    continue
                visits[root].append(choice)
                if choice not in hits:
                    hits[choice] = 1
                else:
                    hits[choice] += 1
                    if hits[choice] == num_to_hit:
                        middle_point = choice
                #print("Current vertex:",choice)
                for adjacent in self.graph[choice]:
                    if self.graph[choice][adjacent] == float(0.0):
                        continue
                    weight = self.graph[choice][adjacent]
                    #print("adjacent and weight are:", adjacent, weight)
                    #print("minimum_weight:", minimum_weight)
                    distance = float(minimum_weight) + float(weight)
                    if adjacent not in distances[root] or distance < distances[root][adjacent]:
                        distances[root][adjacent] = distance
                        #print("Pushing:", distance, adjacent)
                        heapq.heappush(heap[root], (distance, adjacent))
                        previous[root][adjacent] = choice
            if middle_point != "null":
                break

        print("Found it:", middle_point)
        paths = {}
        for root in targets:
            # print("Root:",root)
            paths[root] = []
            next_in_path = middle_point
            while next_in_path != root:
                # ("Appending", previous[root][next_in_path], next_in_path)
                weight = distances[root][next_in_path] - distances[root][previous[root][next_in_path]]
                paths[root].append((previous[root][next_in_path], next_in_path, weight))
                next_in_path = previous[root][next_in_path]

        edges = []
        for path in paths:
            for edge in paths[path]:
                if edge not in edges:
                    edges.append(edge)

        for edge in edges:
            print(edge[0], "->", edge[1], ":", edge[2])

        return [edges, middle_point]


# ADJACENCY LIST DATA STRUCTURE AND SEARCH ALGORITHM
class AdjacencyList:

    def __init__(self, edges):
        self.graph: dict[str, list]
        self.graph = {}
        for edge in edges:
            self.add_connection(str(edge[0]), str(edge[1]), float(edge[2]))

    def add_connection(self, from_vertex, to_vertex, weight):
        if from_vertex not in self.graph:
            self.graph[from_vertex] = []
        if to_vertex not in self.graph:
            self.graph[to_vertex] = []
        self.graph[from_vertex].append((str(to_vertex), float(weight)))
        self.graph[to_vertex].append((str(from_vertex), float(weight)))

    def print_connections(self):
        for v in self.graph:
            print(v)
            print(len(self.graph[v]))

    def bidirectional_search(self, targets):
        hits = {}
        visits = {}
        distances = {}
        previous = {}
        heap = {}

        middle_point = "null"

        for root in targets:
            previous[root] = {}
            distances[root] = {}
            distances[root][root] = 0
            hits[root] = 0
            heap[root] = [(0, root)]
            visits[root] = []

        while True:
            for root in targets:
                #cdprint("Dijking", root)
                #print("Heap", heap[root])
                (minimum_weight, choice) = heapq.heappop(heap[root])
                if choice in visits[root] or (choice in targets and choice != root):
                    if len(heap[root]) == 0:
                        continue
                    while choice in visits[root] or choice in targets:
                        (minimum_weight, choice) = heapq.heappop(heap[root])
                        if len(heap[root]) == 0:
                            empty = True
                            break
                visits[root].append(choice)
                if choice not in hits:
                    hits[choice] = 1
                else:
                    hits[choice] += 1
                    if hits[choice] == len(targets):
                        middle_point = choice
                #print("Current vertex:",choice)
                for i in range(0, len(self.graph[choice])):
                    adjacent = self.graph[choice][i][0]
                    weight = self.graph[choice][i][1]
                    #print("adjacent and weight are:", adjacent, weight)
                    distance = minimum_weight + weight
                    if adjacent not in distances[root] or distance < distances[root][adjacent]:
                        distances[root][adjacent] = distance
                        #print("Pushing:", distance, adjacent)
                        heapq.heappush(heap[root], (distance, adjacent))
                        previous[root][adjacent] = choice
            if middle_point != "null":
                break

        print("Found it:", middle_point)
        paths = {}
        for root in targets:
            #print("Root:",root)
            paths[root] = []
            next_in_path = middle_point
            while next_in_path != root:
                #("Appending", previous[root][next_in_path], next_in_path)
                weight = distances[root][next_in_path] - distances[root][previous[root][next_in_path]]
                paths[root].append((previous[root][next_in_path], next_in_path, weight))
                next_in_path = previous[root][next_in_path]

        edges = []
        for path in paths:
            for edge in paths[path]:
                if edge not in edges:
                    edges.append(edge)

        for edge in edges:
            print(edge[0],"->",edge[1],":",edge[2])

        return [edges, middle_point]

def fix_movie_name(name):
    name = name.capitalize()
    fixed = ''
    for i in range(0, len(name)):
        if name[i] == "-":
            fixed = fixed + " "
        elif name[i-1] == "-":
            fixed = fixed + name[i].upper()
        else:
            fixed = fixed + name[i]

    return fixed

# Method to create agraph graph
def create_graph(movie_data_, edge_data_, queries, recommendation):
    nodes = []
    edges = []
    for movie in movie_data_:
        if movie in queries:
            movie = fix_movie_name(movie)
            nodes.append(Node(id=str(movie),
                              label=str(movie),
                              size=10,
                              shape = 'square')
                         )
        elif movie == recommendation:
            movie = fix_movie_name(movie)
            nodes.append(Node(id=str(movie),
                              label=str(movie),
                              size=15)
                         )
        else:
            movie = fix_movie_name(movie)
            nodes.append(Node(id=str(movie),
                              label=str(movie),
                              size=5)
                         )
    for edge in edge_data_:
        print("Adding edge", edge[0], edge[1])
        edges.append(Edge(source=str(fix_movie_name(edge[0])),
                          label=str(round(float(edge[2]), 1)),
                          target=str(fix_movie_name(edge[1])),
                          nodeHighlightBehavior=True
                          )
                     )
    config = Config(width=500,
                    height=500,
                    directed=False,
                    physics=True,
                    hierarchical=False,
                    # **kwargs
                    )

    return [nodes, edges, config]


def display_graph(nodes_, edges_, config_):
    agraph(nodes=nodes_, edges=edges_, config=config_)


def generate_graph(query_, implementation):
    print("Finding recommendation")
    if implementation == "Adjacency List":
        print("Building Adjacency List")

        construction_start_ = time.time()
        myList = AdjacencyList(edge_data)
        construction_end_ = time.time()

        search_start_ = time.time()
        (recommended_edges, recommendation) = myList.bidirectional_search(query)
        search_end_ = time.time()

    else:
        print("Building Adjacency Matrix")

        construction_start_ = time.time()
        myMatrix = AdjacencyMatrix(edge_data, find_movies(edge_data))
        #myMatrix.print_connections()
        construction_end_ = time.time()

        search_start_ = time.time()
        (recommended_edges, recommendation) = myMatrix.bidirectional_search(query)
        search_end_ = time.time()

    print("Recommendation:",recommendation)
    st.title("Your movie recommendation is:")
    st.title("👉" + recommendation)
    movie_data = find_movies(recommended_edges)
    for movie in movie_data:
        print("Movie:",movie)
    for edge in recommended_edges:
        print("Edge:",edge)
    print("Creating graph")
    graph_data = create_graph(movie_data, recommended_edges, query_, recommendation)
    print("Displaying graph")
    return graph_data, construction_start_, construction_end_, search_start_, search_end_, recommendation


pressed = False

# Raiden frontend
# intro page
st.title("🍿ReelMe")
st.subheader("About Us")
st.markdown(
    "**Welcome to ReelMe! This web app allows you to enter you and your friends favorite movies and reccomend one you will all love. No matter how diverse your tastes.✌️**")
left_column, right_column = st.columns(2)
with left_column:
    st.text("")
    st.subheader("How to use ReelMe")
    st.markdown(
        "1. Enter your favorite movies.\n2. Click the button to get your reccomendation.\n3. Enjoy your movie night!")
with right_column:
    # lotte file images
    st_lottie(lottie_coding, speed=.05, height=200, key="initial")

if "i_am_ready" not in st.session_state:
    st.session_state.i_am_ready = False

click = st.button("I am ready!")

if click:
    st.session_state.i_am_ready = True

# input page
if st.session_state.i_am_ready:
    st.divider()
    col = st.columns(2)
    with col[0]:
        st.text("")
        st.title("Get Started")
        st.text("")
        graph_type = st.radio(
            "Select the graph implementation to use:",
            ('Adjacency List', 'Adjacency Matrix'))
    with col[1]:
        st_lottie(lottie_coding1, speed=.5, height=200, key="initial1")

    options = st.multiselect(
        'Your favorite movies...',
        movie_displays
    )
    
    # RUNTIME
    query = options
    start = 0
    end = 0

    pressed = False
    if st.button('Create graph'):
        pressed = True
        latest_iteration = st.empty()
        bar = st.progress(0)    
        for i in range(100):
            latest_iteration.text(f'Calculating... {i + 1}%')
            bar.progress(i + 1)
            time.sleep(0.01)
        print("Generating graph")
        start = time.time()
        graph_to_display, construction_start, construction_end, search_start, search_end, recommendation = generate_graph(query, graph_type)
        end = time.time()
    if pressed:
        print("Pressed")
        agraph(nodes=graph_to_display[0], edges=graph_to_display[1], config=graph_to_display[2])
        st.metric(label = "Total", value = float(end - start))
        st.metric(label = graph_type + " Construction", value=float(construction_end - construction_start))
        st.metric(label = "Bi-Directional Search", value=float(search_end - search_start))
    else:
        print("Not Pressed")

    options = []