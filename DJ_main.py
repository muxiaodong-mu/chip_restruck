import random 
import numpy as np
from altgraph import Graph as g
from altgraph import GraphAlgo as ga
random.seed(5)

# 定义变量
array_height = 64
array_size = array_height**2
fault_rate = 0.001

fault_array = []
fault_2dlist = [np.array([]) for i in range(array_height)]
array_2dlist = [np.array([]) for i in range(array_height)]
min_colum_num = array_height
min_row_id = 0
first_row = []
last_row = []
min_row = []

id_coor_map = dict()
G = g.Graph()

ans = []

def createData(array_size,fault_rate):
    global fault_array, first_row, last_row, id_coor_map, G, array_2dlist
    fault_id_list = random.sample(range(array_size),int(array_size*fault_rate))
    fault_array = [i not in fault_id_list for i in range(array_size)]
    id_coor_map = {i:(int(i/array_height),i%array_height) for i in range(array_size)}

    base = [i for i in range(array_height)]
    for i in range(array_height):
        array_2dlist[i] = np.array([i*array_height+j for j in base])
        fault_2dlist[i] = np.array(fault_array[i*array_height:(i+1)*array_height])

    first_row = array_2dlist[0][fault_2dlist[0]]
    last_row = array_2dlist[array_height-1][fault_2dlist[array_height-1]]
        
def buildGraph():
    global G, array_2dlist, fault_array, id_coor_map

    def G_add_edge(G, a, b):
        global id_coor_map
        a_coor = id_coor_map[a]
        b_coor = id_coor_map[b]
        w = ( abs(a_coor[0]-b_coor[0])**2 + abs(a_coor[1]-b_coor[1])**2 )**0.5
        G.add_edge(a, b, w)
        G.add_edge(b, a, w)

    for i in range(array_height-1):
        for a in array_2dlist[i]:
            if not fault_array[a] : continue
            a_y = id_coor_map[a][1]
            for b in array_2dlist[i+1]:
                if not fault_array[b] : continue
                b_y = id_coor_map[b][1]
                # 做一个减支操作
                if abs(a_y - b_y) > 3+(a%array_height)/3: continue # 0.5*array_height
                G_add_edge(G, a, b)

def getMinRow(fault_array):
    # 获取True最少的那一行，作为最短路径起点
    global min_colum_num, min_row_id, min_row, ans
    for i in range(array_height):
        tmp = sum(fault_array[i*array_height:(i+1)*array_height])
        # print(fault_2dlist[i])
        if min_colum_num > tmp:
            min_colum_num = tmp
            min_row_id = i
    min_row = array_2dlist[min_row_id][fault_2dlist[min_row_id]]
    ans = [[] for i in range(min_colum_num)]

def changeStartOrder():
    # 为了最大限度保证结果列不相互影响，调整一下计算顺序
    # 例如[1, 2, 3, 4],调整为[1, 4, 2, 3]
    global min_row
    min_row = list(min_row)
    tmp = []
    while(len(min_row)):
        tmp.append(min_row[0])
        del min_row[0]
        if not len(min_row) : break
        tmp.append(min_row[-1])
        del min_row[-1]
    min_row = tmp

def Dijkstra(G, start, end):
    return ga.shortest_path(G, start, end)

def solve():
    global G, min_row, last_row, first_row, id_coor_map, array_height
    ans_flag = 0
    path_up = []
    path_down = []
    # 检测min_row是不是和first_row和last_row重复了
    first_flag = 1
    last_flag = 1
    if min_row[0] == first_row[0]: first_flag = 0
    if min_row[0] == last_row[0]: last_flag = 0   

    # 核心代码
    for center in min_row:
        center_y = id_coor_map[center][1]
        near_node = -1
        min_distance = array_height
        # 找上边距离中心最临近点
        if first_flag:
            for f_node in first_row:
                if not fault_array[f_node] : continue
                fnode_y = id_coor_map[f_node][1]
                if min_distance >= abs(center_y - fnode_y):
                    min_distance = abs(center_y - fnode_y)
                    near_node = f_node
            path_up = (Dijkstra(G, center, near_node))
            # 隐藏用过的点
            fault_array[path_up[-1]] = False
            for i in path_up:
                if i==center: continue
                G.hide_node(i)
            # path_up反转,去除中心点
            path_up.reverse()
            if last_flag: path_up = path_up[:-1]

        # 找下边距离中心最临近点
        if last_flag:
            min_distance = array_height
            for l_node in last_row:
                if not fault_array[l_node] : continue
                lnode_y = id_coor_map[l_node][1]
                if min_distance >= abs(center_y - lnode_y):
                    min_distance = abs(center_y - lnode_y)
                    near_node = l_node
            path_down = (Dijkstra(G, center, near_node))
            # 隐藏用过的点
            fault_array[path_down[-1]] = False # 隐藏最后一个点，fault矩阵里置false即可，隐藏会报错
            for i in path_down:
                G.hide_node(i)
        
        ans[ans_flag] = path_up+path_down
        ans_flag += 1
        print(path_up+path_down)

def countLength(ans):
    global id_coor_map
    length = 0
    for path in ans:
        for i in range(len(path)-1):
            a_x = id_coor_map[path[i]][0]
            a_y = id_coor_map[path[i]][1]
            b_x = id_coor_map[path[i+1]][0]
            b_y = id_coor_map[path[i+1]][1]
            length += abs(a_x - b_x)+abs(a_y-b_y)
    return length

if __name__ == "__main__":
    createData(array_size,fault_rate)
    getMinRow(fault_array)
    # changeStartOrder()
    buildGraph()
    solve()
    print(countLength(ans))
    # 测试
    # print(ans)
    for i in range(array_height):
        print(array_2dlist[i])
    print(first_row,min_row,last_row)