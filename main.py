import csv
import math

# could probably use more classes, especially where i have the dict[tuple[str, str], tuple[float, int]] nonsense
class Rating:
    def __init__(self, movieName: str, score: int):
        self.movieName = movieName
        self.score = score

# ````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````
# Biggest problems right now:
# The number of ratings per edge is veryyyy low. 1.00006 low. Need to bring this up to > 30
# Solutions: make the allowed_movies set much more constrictive, so we're only considering widely reviewed, popular top_movies
# ???
# ````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````
def main():
    print("Reading in list of top movies...")
    top_movies = get_top_movie_set("dsaproj3/modified_inputs/top_movie_list.csv")
    #print("Top " + str(len(movies)) + " movies:\n")
    #print(movies)

    print("Reading in ratings...")
    users = read_in_ratings('dsaproj3/letterboxd_database/ratings_export.csv', allowed_movies=top_movies, max_size=1000, modulo=10) 

    #for userID in users:
    #    print("User: " + userID + ", Reviews: " + str(len(users[userID])))

    print("Creating edges...")
    edges = create_edge_list(users)

    print("Writing edges to file...")
    create_edge_file("output/edges.csv", edges)

    print("Done!")
    print("Average reviews per edge: " + str(count_average_ratings_per_edge(edges)))



def calculate_edge_weight_per_rating(from_rating : Rating, to_rating : Rating) -> float:
    # TODO: incorporate a movie's average rating so the equation looks like abs( (to_rating - to_average) - (from_rating - from_average) )
    return abs(float(to_rating.score) - float(from_rating.score)) 

def count_average_ratings_per_edge(edges):
    average = 0.0
    i = 0.0
    for edge in edges:
        i+=1
        average += edges[edge][1] 
    return average/i


def create_edge_list(users: dict[str, list[Rating]]) -> dict[tuple[str, str], tuple[float, int]]:

    edges : dict[tuple[str, str], tuple[float, int]] # tuple of to, from movieID to weight and number of edges
    edges = {}

    # loop through all of a user's ratings, connecting all movies they've rated
    for userID in users:
        for fromRating in users[userID]:
            for to_rating in users[userID]:

                # identify the pair of movies
                fromMovieID = fromRating.movieName
                toMovieID = to_rating.movieName
                # break we're connecting a movie to itself
                if fromMovieID == toMovieID : break
                vertexPair = (fromMovieID, toMovieID)

                # calculate this user's connection's weight, will be averaged in to the edge weight.
                ratingWeight = calculate_edge_weight_per_rating(fromRating, to_rating)

                # add the vertexPair key to the dict if this is the first connection between these two vertexes
                if not vertexPair in edges:
                    edges[vertexPair] = (0.0, 0)

                # weird tuple fenangling because i shouldn't have used a tuple for the weight/number of ratings
                numRatings = edges[vertexPair][1]
                # averages this rating into the edges' weight
                edges[vertexPair] = ( (edges[vertexPair][0] * numRatings + ratingWeight) / (numRatings + 1) , numRatings + 1)
    return edges



def create_edge_file(filepath: str, edges: dict[tuple[str, str], tuple[float, int]]):

    # TODO: this writes the file all at once using one string, which is probably why it takes for-fucking-ever to run. feel free to optimize!
    text = "Source,Target,Weight\n"
    i = 0.0
    size = len(edges)
    print("Writing " + str(len(edges)) + " edges...")
    for edge in edges:
        fromMovie = edge[0]
        toMovie = edge[1]
        weight = edges[edge][0]
        text += fromMovie + "," + toMovie + "," + str(weight) + "\n"

        # silly little progress counter
        if (i % 1000) == 0:
            print(str(i/size * 100)+'%')
        i += 1


    with open('dsaproj3/output/edges.csv', 'w') as file:
        file.write(text)
        

# reads all ratings into a dictionary mapping usernames to a list of their ratings
# allowed_movies, if passed, is a set of movies that the reader will check against, discarding all reviews not in it.
def read_in_ratings(filepath: str, allowed_movies = None, max_size = 1000000, modulo = 1) -> dict[str, list[Rating]]: 
    users : dict[str, list[Rating]]
    users = {}

    with open(filepath, newline='', encoding="utf8") as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        i = 0
        for row in reader:
            i += 1
            # if the max number of reviews has been reached, break
            if i >= max_size * modulo: break
            # optional modulo argument allows to take every nth review. useful for getting a wider distribution of users. (modulo = 3 ~> only every third review is added)
            if not (i % modulo == 0): continue
            # grab data from csv
            movieID = row[1]
            ratingVal = row[2]
            userID = row[3]
            # if the movie is not in the given set of allowed movies, discard the review (added clause for no set provided)
            if not (allowed_movies == None or movieID in allowed_movies): 
                continue
            # add the user to the dictionary if this is their first review
            if not userID in users:
                users[userID] = []
            # add the review to their list of rating
            users[userID].append(Rating(movieID, ratingVal))
    return users


# method to read in a list of movies, i manually created the file by sorting the movie_data.csv by popularity and then pruning the top 50,000 or something.
def get_top_movie_set(filepath: str) -> set[str]:
    movies : set[str]
    movies = set()
    with open(filepath, newline='', encoding="utf8") as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            movies.add(row[0])
    return movies


if __name__ == "__main__":
    main()