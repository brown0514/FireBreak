import os
import sys
from unittest import TestProgram
# values.index(min(values)

INF = 100000000	# define infinite number

g_N = 0			# number of vetices
g_adj = {}		# adjacent info for the graph
# g_treeAdj = {}	# adjacent info for the rooted tree
g_S = 0			# number of burning trees
g_B = 0			# maximum cost
g_burnList = []	# list of burning trees
g_vertexList = []
g_node = []
g_isVisited = {} # visit flag for make_tree

g_A_plus = {}	# A +
g_A_minus = {}	# A -

class newNode:
	def __init__(self):
		self.status = 0
		self.id = -1
		self.value = 0
		self.size = 0
		self.parent = self.child = self.next = None
		self.adj_num = 0
		self.adj = []

# Algorithm 2 Subprocedure for table ST
def TableST(id, B):
	global g_A_plus, g_A_minus

	ST_plus = {}	# ST +
	ST_minus = {}	# ST -

	for b in range(B + 1):
		if g_node[id].status:
			ST_plus[(0, b)], ST_minus[(0, b)] = (0, []), (-INF, [])
		else:
			ST_plus[(0, b)], ST_minus[(0, b)] = (0, []), (1, [])
	for j in range(1, g_node[id].adj_num + 1):
		child = g_node[id].adj[j - 1]
		for b in range(B + 1):
			# id, j-th child both burn
			z = max((x for x in range(b + 1)), key = lambda x: ST_plus[(j - 1, x)][0] + g_A_plus[(child.id, b - x)][0])	
			ST_plus[(j, b)] = (ST_plus[(j - 1, z)][0] + g_A_plus[(child.id, b - z)][0], ST_plus[(j - 1, z)][1] + g_A_plus[(child.id, b - z)][1])

			# id burn, j-th child not burn, b > 0
			if not child.status and b > 0:
				zz = max((x for x in range(b)), key = lambda x: ST_plus[(j - 1, x)][0] + g_A_minus[(child.id, b - 1 - x)][0])
				temp_m = ST_plus[(j - 1, zz)][0] + g_A_minus[(child.id, b - 1 - zz)][0]
				if temp_m >= ST_plus[(j, b)][0]:
					ST_plus[(j, b)] = (temp_m, ST_plus[(j - 1, zz)][1] + g_A_minus[(child.id, b - 1 - zz)][1] + [child.id])
			
			ST_minus[(j, b)] = (-INF, [])
			# id not burn
			if not g_node[id].status:
				# j-th child burn
				if b > 0:
					z = max((x for x in range(b)), key = lambda x: ST_minus[(j - 1, x)][0] + g_A_plus[(child.id, b - 1 - x)][0])
					ST_minus[(j, b)] = (ST_minus[(j - 1, z)][0] + g_A_plus[(child.id, b - 1 - z)][0], ST_minus[(j - 1, z)][1] + g_A_plus[(child.id, b - 1 - z)][1])
				# j-th child not burn
				if not child.status:
					zz = max((x for x in range(b + 1)), key = lambda x: ST_minus[(j - 1, x)][0] + g_A_minus[(child.id, b - x)][0])
					temp_m = ST_minus[(j - 1, z)][0] + g_A_minus[(child.id, b - z)][0]
					if not (j, b) in ST_minus or temp_m >= ST_minus[(j, b)][0]:
						ST_minus[(j, b)] = (temp_m, ST_minus[(j - 1, z)][1] + g_A_minus[(child.id, b - z)][1])
	
	# value A <- value ST
	for b in range(B + 1):
		g_A_plus[(id, b)] = ST_plus[(g_node[id].adj_num, b)]
		g_A_minus[(id, b)] = ST_minus[(g_node[id].adj_num, b)]

# Algorithm 1 Optimal Tree Cut
def TableA():
	for id in range(g_N):
		TableST(id, g_B)
	if g_A_minus[(g_N - 1, g_B)][0] > g_A_plus[(g_N - 1, g_B)][0]:
		return g_A_minus[(g_N - 1, g_B)]
	else:
		return g_A_plus[(g_N - 1, g_B)]

def make_tree(start_pos, cur_vertex):
	global g_node, g_burnList, g_isVisited

	g_isVisited[cur_vertex] = True
	tot_vertect_cnt = 1
	pos = start_pos
	child_node = None

	# recursive make tree
	for v in g_adj[cur_vertex]:
		if v in g_isVisited and g_isVisited[v]:
			continue
		cnt = make_tree(pos, v)
		
		# setting next child
		if pos != start_pos:
			g_node[pos - 1].next = g_node[pos + cnt - 1]
		else:
			child_node = g_node[pos + cnt - 1]

		pos += cnt
		tot_vertect_cnt += cnt
	
	g_node[pos].value = cur_vertex
	g_node[pos].id = pos
	g_node[pos].size = tot_vertect_cnt

	# check burn status
	if cur_vertex in g_burnList:
		g_node[pos].status = 1
	
	# setting parent and child
	if child_node:
		g_node[pos].child = child_node
		while child_node:
			g_node[pos].adj_num += 1
			g_node[pos].adj.append(child_node)
			child_node.parent = g_node[pos]
			child_node = child_node.next
	
	return tot_vertect_cnt


def input_error():
	print("Input Data Error!")
	return False

#add vertex to the graph
def add_vertex(v):
	if v in g_vertexList:
		return
	g_vertexList.append(v)

# add edge to the graph
def add_edge(x, y):
	global g_adj
	if not x in g_adj:
		g_adj[x] = []
	g_adj[x].append(y)

	if not y in g_adj:
		g_adj[y] = []
	g_adj[y].append(x)

	add_vertex(x)
	add_vertex(y)

# input tree data
def input_tree(strInputPath):
	global g_N, g_B, g_adj, g_S, g_burnList
	with open(strInputPath, "r") as fp:
		inputData = fp.read().split()
	
	pos = 0
	cnt = len(inputData)

	# input N, S
	if pos + 1 >= cnt:
		return input_error()
	g_N = int(inputData[pos])
	if g_N <= 0:
		return input_error()
	g_B = int(inputData[pos + 1])
	if g_B < 0:
		return input_error()
	if g_B >= g_N:
		g_B = g_N - 1
	pos += 2

	# input adjacent info
	for i in range(g_N - 1):
		if pos + 1 >= cnt:
			return input_error()
		x = int(inputData[pos])
		y = int(inputData[pos + 1])
		pos += 2
		add_edge(x, y)
	
	# check the number of vertices
	if g_N != len(g_vertexList):
		return input_error()
	
	# input burning tree list
	if pos >= cnt:
		return input_error()
	g_S = int(inputData[pos])
	pos += 1
	if g_S != cnt - pos:
		return input_error()
	for i in range(g_S):
		g_burnList.append(int(inputData[pos + i]))
	return True

def print_usage():
	print("{} <input file name>".format(sys.argv[0]))

def initialize():
	if len(sys.argv) != 2:
		print_usage()
		sys.exit(1)
	if not input_tree(sys.argv[1]):
		sys.exit(1)
	for i in range(g_N):
		g_node.append(newNode())
	root = g_vertexList[0]
	make_tree(0, root)
	for i in range(g_N):
		if g_node[i].status:
			print("vert: [{}], adj: ".format(i), end="")
		else:
			print("vert: {}, adj: ".format(i), end="")
		for v in g_node[i].adj:
			print("{}, ".format(v.id), end="")
		print("")

def main():
	initialize()
	saved_vertices, opt_cut_system = TableA()
	print("Number of saved vertices = %d" % saved_vertices)
	for i in opt_cut_system:
		print(i)
	

if __name__ == "__main__":
	main()