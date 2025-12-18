import java.util.*;
import java.io.*;

class Graph {
    private Map<String, Node> nodes = new HashMap<>();
    private List<Arc> arcs = new ArrayList<>();
    private Map<Node, List<Arc>> adjacencyList = new HashMap<>();
    
    public Node addNode(String id) {
        Node node = new Node(id);
        nodes.put(id, node);
        adjacencyList.put(node, new ArrayList<>());
        return node;
    }
    
    public Arc addArc(Node from, Node to, int weight) {
        Arc arc = new Arc(from, to, weight);
        arcs.add(arc);
        adjacencyList.get(from).add(arc);
        return arc;
    }
    
    public List<Node> getNodes() {
        return new ArrayList<>(nodes.values());
    }
    
    public boolean isConnected(Node a, Node b) {
        // Упрощенная проверка связи
        return adjacencyList.getOrDefault(a, new ArrayList<>())
            .stream()
            .anyMatch(arc -> arc.to.equals(b));
    }
}

class Node {
    String id;
    
    public Node(String id) {
        this.id = id;
    }
    
    @Override
    public String toString() {
        return "Node{" + id + "}";
    }
    
    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Node node = (Node) o;
        return id.equals(node.id);
    }
    
    @Override
    public int hashCode() {
        return id.hashCode();
    }
}

class Arc {
    Node from;
    Node to;
    int weight;
    
    public Arc(Node from, Node to, int weight) {
        this.from = from;
        this.to = to;
        this.weight = weight;
    }
    
    @Override
    public String toString() {
        return "Arc{" + from + " -> " + to + ", weight=" + weight + "}";
    }
}

public class GeneratedGraphProgram {
    public static Graph create_graph() {
        return new Graph();
    }

    public static Node add_node(Graph graph, String id) {
        return graph.addNode(id);
    }

    public static Arc add_arc(Graph graph, Node from, Node to, int weight) {
        return graph.addArc(from, to, weight);
    }

    public static List<Node> get_nodes(Graph graph) {
        return graph.getNodes();
    }

    public static boolean is_connected(Graph graph, Node a, Node b) {
        return graph.isConnected(a, b);
    }

    public static void print(String text) {
        System.out.print(text);
    }

    public static void println(String text) {
        System.out.println(text);
    }

public static void main(String[] args) {
    Graph g;
    g = create_graph();
    Node n1 = null;
    n1 = add_node(g, "Start");
    Node n2 = null;
    n2 = add_node(g, "End");
    Arc a1 = null;
    a1 = add_arc(g, n1, n2, 10);
    println("Graph created!");
    println("Graph nodes:");
    List<Node> nodes = new ArrayList<>();
    nodes = get_nodes(g);
    println("Total nodes: 2");
    boolean connected = false;
    connected = is_connected(g, n1, n2);
    if (connected) {
        {
            println("Path exists!");
        }
    } else {
        {
            println("Path not exists!");
        }
    }
}
}
