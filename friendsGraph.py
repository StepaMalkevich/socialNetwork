import vk
import networkx as nx
import matplotlib.pyplot as plt
import time
import pickle

# To access the friends:
# https://oauth.vk.com/authorize?client_id=id&redirect_uri=https://oauth.vk.com/blank.html
# &response_type=token&scope=friends

# Task: to build the social graph of their friends and to count on it a Multiplexity

access_token = 'your token'
session = vk.Session(access_token=access_token)
vkapi = vk.API(session)


def getUserId(link):
    id = link
    if 'vk.com/' in link:
        id = link.split('/')[-1]
    if not id.replace('id', '').isdigit():
        id = vkapi.utils.resolveScreenName(screen_name=id)['object_id']
    else:
        id = id.replace('id', '')
    return int(id)


# You can calculate this metric for your own id
def getMultiplexity(my_user_id):
    lst = vkapi.friends.getLists(user_id=my_user_id)

    # This will be the length of "friends Lists" + 1, as in the friends list there is no standard concept of "friend"
    print('Multiplexity =', len(lst) + 1)


def getListOfMyFriends(my_user_id):
    getMultiplexity(my_user_id)

    my_friends_ids_list = []
    labels = {}

    my_friends_list = vkapi.friends.get(user_id=my_user_id, fields=['nickname'])
    for element in my_friends_list:
        my_friends_ids_list.append(element['user_id'])
        labels[element['user_id']] = element['last_name']

    return my_friends_ids_list, labels


# Friends list of my friends between each other
def getListOfFriendsBetweenEachOther(user_id, set_of_my_friends):
    friends_ids_list = []

    friends_list = vkapi.friends.get(user_id=user_id, fields=['nickname'])
    for element in friends_list:
        if (element['user_id'] in set_of_my_friends):
            friends_ids_list.append(element['user_id'])

    return friends_ids_list


def uploadEdgesToGraph(G, outer_friend_id, list_of_friends_ids):
    for inner_friend_id in list_of_friends_ids:
        G.add_edge(outer_friend_id, inner_friend_id)


def fill_graph(my_user_id):
    G = nx.Graph()

    my_friends_ids_list, labels = getListOfMyFriends(my_user_id)
    set_of_my_friends = set(my_friends_ids_list)

    uploadEdgesToGraph(G, my_user_id, my_friends_ids_list)

    for my_friend_id in my_friends_ids_list:
        try:
            list_of_friends_about_me = getListOfFriendsBetweenEachOther(my_friend_id, set_of_my_friends)
            uploadEdgesToGraph(G, my_friend_id, list_of_friends_about_me)
            time.sleep(1)
        except vk.exceptions.VkAPIError as e:
            print(e)

    return G, labels


def draw(G, labels):
    nx.draw(G, with_labels=True, labels=labels, font_size=7, node_color="blue", alpha=0.6, node_size=50)
    plt.show()


def save(G, labels):
    with open('friends_graph.pickle', 'wb') as f:
        pickle.dump(G, f)

    with open('labels.pickle', 'wb') as l:
        pickle.dump(labels, l)


def restore():
    with open('friends_graph.pickle', 'rb') as f:
        G = pickle.load(f)

    with open('labels.pickle', 'rb') as l:
        labels = pickle.load(l)

    return G, labels


my_user_id = 'id103719595'
my_user_id = getUserId(my_user_id)

# Fill the graph with information
G, labels = fill_graph(my_user_id)

# Draw the graph
draw(G, labels)
