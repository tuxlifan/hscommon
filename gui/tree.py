# Copyright 2011 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

class Node(list):
    def __init__(self, name):
        list.__init__(self)
        self._name = name
        self._parent = None
        self._path = None
    
    def __eq__(self, other):
        return self is other
    
    def __hash__(self):
        return object.__hash__(self)
    
    def __repr__(self):
        return '<Node %r>' % self.name
    
    def append(self, node):
        list.append(self, node)
        node._parent = self
        node._path = None
    
    def clear(self):
        del self[:]
    
    def find(self, predicate, include_self=True):
        try:
            return next(self.findall(predicate, include_self=include_self))
        except StopIteration:
            return None
    
    def findall(self, predicate, include_self=True):
        if include_self and predicate(self):
            yield self
        for child in self:
            for found in child.findall(predicate, include_self=True):
                yield found
    
    def get_node(self, index_path):
        result = self
        if index_path:
            for index in index_path:
                result = result[index]
        return result
    
    def get_path(self, target_node):
        if target_node is None:
            return None
        return target_node.path
    
    @property
    def children_count(self):
        return len(self)
    
    @property
    def name(self):
        return self._name
    
    @property
    def parent(self):
        return self._parent
    
    @property
    def path(self):
        if self._path is None:
            if self._parent is None:
                self._path = []
            else:
                self._path = self._parent.path + [self._parent.index(self)]
        return self._path
    
    @property
    def root(self):
        if self._parent is None:
            return self
        else:
            return self._parent.root
    

class Tree(Node):
    def __init__(self):
        Node.__init__(self, '')
        self._selected_nodes = []
    
    def __hash__(self):
        return object.__hash__(self)
    
    def _select_nodes(self, nodes):
        # all selection changes go through this method, so you can override this if you want to
        # customize the tree's behavior.
        self._selected_nodes = nodes
    
    def clear(self):
        self._selected_nodes = []
        Node.clear(self)
    
    @property
    def selected_node(self):
        return self._selected_nodes[0] if self._selected_nodes else None
    
    @selected_node.setter
    def selected_node(self, node):
        if node is not None:
            self._select_nodes([node])
        else:
            self._select_nodes([])
    
    @property
    def selected_nodes(self):
        return self._selected_nodes
    
    @selected_nodes.setter
    def selected_nodes(self, nodes):
        self._select_nodes(nodes)
    
    @property
    def selected_path(self):
        return self.get_path(self.selected_node)
    
    @selected_path.setter
    def selected_path(self, index_path):
        if index_path is not None:
            self.selected_paths = [index_path]
        else:
            self._select_nodes([])
    
    @property
    def selected_paths(self):
        return list(map(self.get_path, self._selected_nodes))
    
    @selected_paths.setter
    def selected_paths(self, index_paths):
        nodes = []
        for path in index_paths:
            try:
                nodes.append(self.get_node(path))
            except IndexError:
                pass
        self._select_nodes(nodes)
    
