import os
import sys
from time import sleep
from unittest import TestProgram
from tkinter import *
import random
# values.index(min(values)

tk_root = Tk()
tk_root.update()
tk_root.title("Windy Firebreak Location in Trees")

g_radius 		= 1
g_widthUnit 	= 100
g_heightUnit 	= 100
g_width			= 1000
g_height		= 500
g_columnNum		= 1
g_rowNum		= 1
g_burnColor		= "#EE9D9D"
g_unburnColor	= "#ADDCB8"

# Canvas
canvas = Canvas(width=g_width, height=g_height, bg="#cedbd2")
canvas.pack()

INF = 100000000	# define infinite number

g_N = 0			# number of vetices
g_adj = {}		# adjacent info for the graph
# g_treeAdj = {}	# adjacent info for the rooted tree
g_S = 0			# number of burning trees
g_B = 0			# maximum cost
g_burnList = []	# list of burning trees
g_vertexList = []
g_node = []
g_root_node = None
g_isVisited = {} # visit flag for make_tree

g_A_plus = {}	# A +
g_A_minus = {}	# A -

class newNode:
	def __init__(self):
		self.status = 0
		self.id = -1
		self.value = 0
		self.size = 0
		self.depth = 1
		self.width = 1
		self.parent = self.child = self.next = None
		self.adj_num = 0
		self.adj = []
		self.remove_flag = 0

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
					ST_minus[(j, b)] = (ST_minus[(j - 1, z)][0] + g_A_plus[(child.id, b - 1 - z)][0], ST_minus[(j - 1, z)][1] + g_A_plus[(child.id, b - 1 - z)][1] + [child.id])
				# j-th child not burn
				if not child.status:
					zz = max((x for x in range(b + 1)), key = lambda x: ST_minus[(j - 1, x)][0] + g_A_minus[(child.id, b - x)][0])
					temp_m = ST_minus[(j - 1, zz)][0] + g_A_minus[(child.id, b - zz)][0]
					if not (j, b) in ST_minus or temp_m >= ST_minus[(j, b)][0]:
						ST_minus[(j, b)] = (temp_m, ST_minus[(j - 1, zz)][1] + g_A_minus[(child.id, b - zz)][1])
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

# make tree and initialize for determining initial infos such as parent, child, id, status, etc
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
		g_node[pos].width = 0
		g_node[pos].depth = 0
		while child_node:
			g_node[pos].width += child_node.width
			if g_node[pos].depth < child_node.depth:
				g_node[pos].depth = child_node.depth
			g_node[pos].adj_num += 1
			g_node[pos].adj.append(child_node)
			child_node.parent = g_node[pos]
			child_node = child_node.next
		g_node[pos].depth += 1
	
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

# random generate tree data
def random_input_tree():
	global g_N, g_B, g_adj, g_S, g_burnList
	if g_N <= 0 or g_S < 0 or g_B < 0 or g_S > g_N:
		return False
	if g_B >= g_N:
		g_B = g_N - 1
	for i in range(1, g_N):
		j = random.randint(0, i - 1)
		add_edge(i, j)
	ids = []
	for i in range(g_S):
		ids.append(1)
	for i in range(g_S, g_N):
		ids.append(0)
	random.shuffle(ids)
	for i in range(g_N):
		if ids[i]:
			g_burnList.append(i)
	return True

def initialize():
	global g_widthUnit, g_heightUnit, g_root_node, g_radius
	if not random_input_tree():
		sys.exit(1)
	for i in range(g_N):
		g_node.append(newNode())
	make_tree(0, g_vertexList[0])
	g_root_node = g_node[g_N - 1]

	# initial calculation for drawing graph
	g_columnNum = g_root_node.width + 2
	g_rowNum = g_root_node.depth + 2
	g_heightUnit = g_height / g_rowNum
	g_widthUnit = g_width / g_columnNum / 2
	g_radius = g_heightUnit
	if g_radius > g_widthUnit:
		g_radius = g_widthUnit
	g_radius /= 4
	# for i in range(g_N):
	# 	if g_node[i].status:
	# 		print("vert: [{}], adj: ".format(i), end="")
	# 	else:
	# 		print("vert: {}, adj: ".format(i), end="")
	# 	for v in g_node[i].adj:
	# 		print("{}, ".format(v.id), end="")
	# 	print("")

def draw_graph(width_st, px, py, depth, st, node):

	# calculate the postion where the node be drawn
	x = width_st + (st + node.width / 2) * g_widthUnit
	y = (depth + 0.5) * g_heightUnit

	# determine the color of the node
	color = g_unburnColor
	if node.status:
		color = g_burnColor

	# draw line between the node and its parent	
	if px >= 0 and node.remove_flag == 0:
		canvas.create_line(x, y, px, py, width=3, fill="black")

	# recursive drawing children
	cur_pos = st
	for v in node.adj:
		draw_graph(width_st, x, y, depth + 1, cur_pos, v)
		cur_pos += v.width

	# draw the node
	canvas.create_oval(x-g_radius, y-g_radius, x+g_radius, y+g_radius, fill=color, outline="black")
	canvas.create_text(x, y, text=str(node.id))

def mark_burn_vertices():
	for i in range(g_N):
		if not g_node[i].remove_flag and g_node[i].status and g_node[i].parent:
			g_node[i].parent.status = 1

	for i in range(g_N - 1, -1, -1):
		if not g_node[i].remove_flag and g_node[i].parent and g_node[i].parent.status:
			g_node[i].status = 1

class Num:
	def __init__(self, master):
		self.master = master
		self.master.attributes("-topmost", True)
		toplevel_offsetx, toplevel_offsety = int(tk_root.winfo_x() + g_width / 2), int(tk_root.winfo_y() + g_height / 2)
		padx = 70
		pady = 5
		self.master.geometry(f"+{toplevel_offsetx - padx}+{toplevel_offsety - pady}")
		self.frame = Frame(self.master)
		self.label = Label(self.master, text = "Please insert the number of trees")
		self.entry = Entry(self.master)
		self.button_ok = Button(self.frame, text="OK", width=25, command=self.get_vert_num)
		self.button_ok.pack()
		self.entry.pack()
		self.label.pack()
		self.frame.pack()
	
	def get_vert_num(self):
		global g_N
		g_N = self.entry.get()
		g_N = int(g_N)
		self.master.destroy()
		tk_burn = Toplevel(tk_root)
		input = Burn(tk_burn)

class Burn:
	def __init__(self, master):
		self.master = master
		self.master.attributes("-topmost", True)
		toplevel_offsetx, toplevel_offsety = int(tk_root.winfo_x() + g_width / 2), int(tk_root.winfo_y() + g_height / 2)
		padx = 70
		pady = 5
		self.master.geometry(f"+{toplevel_offsetx - padx}+{toplevel_offsety - pady}")
		self.frame = Frame(self.master, width=100, height=200)
		self.label = Label(self.master, text = "Please insert the number of burnt trees")
		self.entry = Entry(self.master)
		self.button_ok = Button(self.frame, text="OK", width=25, command=self.get_burn_num)
		self.button_ok.pack()
		self.entry.pack()
		self.label.pack()
		self.frame.pack()
	
	def get_burn_num(self):
		global g_S
		g_S = self.entry.get()
		g_S = int(g_S)
		self.master.destroy()
		tk_budget = Toplevel(tk_root)
		input = Budget(tk_budget)

class Budget:
	def __init__(self, master):
		self.master = master
		self.master.attributes("-topmost", True)
		toplevel_offsetx, toplevel_offsety = int(tk_root.winfo_x() + g_width / 2), int(tk_root.winfo_y() + g_height / 2)
		padx = 70
		pady = 5
		self.master.geometry(f"+{toplevel_offsetx - padx}+{toplevel_offsety - pady}")
		self.frame = Frame(self.master, width=100, height=200)
		self.label = Label(self.master, text = "Please insert the budget!")
		self.entry = Entry(self.master)
		self.button_ok = Button(self.frame, text="OK", width=25, command=self.get_budget)
		self.button_ok.pack()
		self.entry.pack()
		self.label.pack()
		self.frame.pack()
	
	def get_budget(self):
		global g_B
		g_B = self.entry.get()
		g_B = int(g_B)
		self.master.destroy()
		start_work()

def start_work():
	initialize()
	saved_vertices, opt_cut_system = TableA()
	# draw the inital graph
	draw_graph(0, -1, -1, 1, 1, g_root_node)

	for i in opt_cut_system:
		g_node[i].remove_flag = 1
	mark_burn_vertices()

	# draw the splited graph
	draw_graph(g_width / 2, -1, -1, 1, 1, g_root_node)

	txt = "Budget: %d, Number of saved vertices = %d" % (g_B, saved_vertices)
	canvas.create_text(g_width /2, g_heightUnit / 2, text=txt)

def generate_tree():
	tk_num = Toplevel(tk_root)
	input = Num(tk_num)

def main():
	generate_tree()

if __name__ == "__main__":
	main()
	tk_root.mainloop()