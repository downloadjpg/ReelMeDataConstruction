import csv
import math
from typing import TypeAlias, Dict, Tuple
from collections import defaultdict


'''
outline:

read in ratings to get movie set, review data.
    dict of [movie_id -> average_score, rating_count]
    edge_list:
        dict of users -> to, from, weight
read in movie_data to generate filtered movie_data
'''

Rating = tuple[str, int]
Edge = tuple[str, str, float]

edge_list : [Edge]
movies : []




def main():
    print("Aggregating allowed_movies...")
    allowed_movie_set = get_allowed_movies()
    print("Reading in user ratings...")
    movies, users = read_in_ratings('letterboxd_database/ratings_export.csv', allowed_movie_set)
    #print("Constructing new movie_data.csv...")
    #write_new_movie_data_csv(allowed_movie_set, movies)
    print("Constructing edge list...")
    edges = create_edge_list(users, movies, allowed_movie_set)
    print("Writing edges to edges.csv...")
    write_edge_list_csv(edges, 'output/edges.csv')


def get_allowed_movies() -> set[str]:
    movie_set = set()
    with open('output/significant_movies.csv', "r") as file:
        for line in file:
            movie_set.add(line.strip())

    return movie_set

def read_in_ratings(filepath: str, allowed_movie_set: set[str]) -> (dict[str, tuple[float, int]], dict[str, list[Rating]]):

    movies : dict[str, tuple[float, int]]
    movies = {}

    users : dict[str, list[Rating]]
    users = {}

    with open(filepath, newline='', encoding="utf8") as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        next(reader) # skip header
        for row in reader:
            if not row[1] in allowed_movie_set:
                continue 
            movie_id = row[1]
            rating_value = int(row[2])
            user_id = row[3]

            # add the review to the dictionary of movies, updating the total number of reviews and the average score
            if movie_id in movies:
                count = movies[movie_id][1]
                new_avg = float(movies[movie_id][0] * count + rating_value) / (count + 1)
                movies[movie_id] = (new_avg, count + 1)
            else:
                movies[movie_id] = (rating_value, 1)


            # add the review to the dictionary of users, which will then be used to create the edge list
            if user_id in users:    
                users[user_id].append((movie_id, rating_value))   
            else:
                users[user_id] = []
                users[user_id].append((movie_id, rating_value))  
    return (movies, users)

def write_new_movie_data_csv(allowed_movie_set, movies):
    # read in file
    data : list(str, str, float, int, str)
    data = []
    with open('letterboxd_database/movie_data.csv', newline='', encoding="utf8") as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        next(reader)
        for row in reader:
            try:
                if (not row[5] in allowed_movie_set):
                    continue
            except: 
                print("exception: " + row[5])
                continue
            movie_id = row[5]
            movie_title = row[6]
            image_url = 'https://a.ltrbxd.com/resized/' + row[2] + '.jpg'
            average_rating = movies[movie_id][0]
            rating_count = movies[movie_id][1]
            data.append((movie_id, movie_title, image_url, average_rating, rating_count))


    # write the contents to file
    path = 'output/filtered_movie_data.csv'
    with open(path, 'w', newline='', encoding="utf8") as csvfile:
        # Create a CSV writer
        writer = csv.writer(csvfile)

        # Write the header row
        writer.writerow(['Movie ID', 'Movie Name', 'Image Link', 'Average Score', 'Review Count'])

        # Write each row of data
        for row in data:
            try:
                writer.writerow(row)
            except:
                print("error: " + row)
def create_edge_list(users, movies, allowed_movie_set):
    edges : dict[tuple[str, str], tuple[float, int]] # dict of vertex pairs to edge weight, and count
    edges = defaultdict(lambda: [0.0, 0])

    # loop through all of a user's ratings, connecting all movies they've rated
    total = len(users)
    print(total)
    user_count = 0
    for user_id in users:
        user_count+=1
        print(user_count)
        # loop through every review a user has
        for i in range(len(users[user_id])):
            # loop through every other review
            for j in range(i + 1, len(users[user_id])):
                from_rating = users[user_id][i]
                to_rating = users[user_id][j]

                # identify the pair of movies 
                from_movie_id = from_rating[0]
                to_movie_id = to_rating[0]
                
                vertex_pair = (from_movie_id, to_movie_id)

                # calculate the weight of this connection from this user. will be averaged into overall edge weight
                rating_weight = calculate_edge_weight_per_rating(from_rating, to_rating, movies)
 
                
                # average the rating into the dictionary
                num_ratings = edges[vertex_pair][1]
                current_weight = edges[vertex_pair][0]
                new_weight = (current_weight * num_ratings + rating_weight) / (num_ratings + 1)
                edges[vertex_pair] = (new_weight, num_ratings + 1)
    return edges




def write_edge_list_csv(edges, file_name):
    with open(file_name, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Source', 'Target', 'Weight', 'Count'])
        for edge, data in edges.items():
            to_name = fix_movie_name(edge[0])
            from_name = fix_movie_name(edge[1])
            writer.writerow([to_name, from_name, data[0], data[1]])


def calculate_edge_weight_per_rating(from_rating, to_rating, movies) -> float:
    to_average_rating_value = movies[to_rating[0]][0]
    from_average_rating_value = movies[from_rating[0]][0]

    weight = abs((to_rating[1] - to_average_rating_value) - (from_rating[1] - from_average_rating_value))
    return weight

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

main()