import org.antlr.v4.runtime.tree.*;
import java.util.*;

public class GraphLangCodeGenerator extends GraphLangBaseVisitor<String> {
    private final StringBuilder code = new StringBuilder();
    private final StringBuilder functionCode = new StringBuilder();
    private final Stack<Map<String, VariableInfo>> scopes = new Stack<>();
    private final Map<String, FunctionInfo> functions = new HashMap<>();
    private final List<String> imports = new ArrayList<>();
    private int indentLevel = 0;
    
    private static class VariableInfo {
        String type;
        String javaType;
        
        VariableInfo(String type, String javaType) {
            this.type = type;
            this.javaType = javaType;
        }
    }
    
    private static class FunctionInfo {
        String returnType;
        String javaReturnType;
        List<VariableInfo> params;
        boolean isStandard;
        
        FunctionInfo(String returnType, String javaReturnType, 
                    List<VariableInfo> params, boolean isStandard) {
            this.returnType = returnType;
            this.javaReturnType = javaReturnType;
            this.params = params;
            this.isStandard = isStandard;
        }
    }
    
    public GraphLangCodeGenerator() {
        scopes.push(new HashMap<>());
        imports.add("java.util.*");
        imports.add("java.io.*");
        
        defineStandardFunctions();
    }
    
    private void defineStandardFunctions() {
        functions.put("create_graph", new FunctionInfo("graph", "Graph", 
            new ArrayList<>(), true));
        functions.put("add_node", new FunctionInfo("node", "Node", 
            Arrays.asList(
                new VariableInfo("graph", "Graph"),
                new VariableInfo("string", "String")
            ), true));
        functions.put("add_arc", new FunctionInfo("arc", "Arc", 
            Arrays.asList(
                new VariableInfo("graph", "Graph"),
                new VariableInfo("node", "Node"),
                new VariableInfo("node", "Node"),
                new VariableInfo("int", "int")
            ), true));
        functions.put("get_nodes", new FunctionInfo("list<node>", "List<Node>", 
            Arrays.asList(new VariableInfo("graph", "Graph")), true));
        functions.put("is_connected", new FunctionInfo("bool", "boolean", 
            Arrays.asList(
                new VariableInfo("graph", "Graph"),
                new VariableInfo("node", "Node"),
                new VariableInfo("node", "Node")
            ), true));
        functions.put("print", new FunctionInfo("void", "void", 
            Arrays.asList(new VariableInfo("string", "String")), true));
        functions.put("println", new FunctionInfo("void", "void", 
            Arrays.asList(new VariableInfo("string", "String")), true));
    }
    
    public String getGeneratedCode() {
        StringBuilder fullCode = new StringBuilder();
        
        fullCode.append("import java.util.*;\n");
        fullCode.append("import java.io.*;\n\n");
        
        // Класс Graph
        fullCode.append("class Graph {\n");
        fullCode.append("    private Map<String, Node> nodes = new HashMap<>();\n");
        fullCode.append("    private List<Arc> arcs = new ArrayList<>();\n");
        fullCode.append("    private Map<Node, List<Arc>> adjacencyList = new HashMap<>();\n");
        fullCode.append("    \n");
        fullCode.append("    public Node addNode(String id) {\n");
        fullCode.append("        Node node = new Node(id);\n");
        fullCode.append("        nodes.put(id, node);\n");
        fullCode.append("        adjacencyList.put(node, new ArrayList<>());\n");
        fullCode.append("        return node;\n");
        fullCode.append("    }\n");
        fullCode.append("    \n");
        fullCode.append("    public Arc addArc(Node from, Node to, int weight) {\n");
        fullCode.append("        Arc arc = new Arc(from, to, weight);\n");
        fullCode.append("        arcs.add(arc);\n");
        fullCode.append("        adjacencyList.get(from).add(arc);\n");
        fullCode.append("        return arc;\n");
        fullCode.append("    }\n");
        fullCode.append("    \n");
        fullCode.append("    public List<Node> getNodes() {\n");
        fullCode.append("        return new ArrayList<>(nodes.values());\n");
        fullCode.append("    }\n");
        fullCode.append("    \n");
        fullCode.append("    public boolean isConnected(Node a, Node b) {\n");
        fullCode.append("        // Упрощенная проверка связи\n");
        fullCode.append("        return adjacencyList.getOrDefault(a, new ArrayList<>())\n");
        fullCode.append("            .stream()\n");
        fullCode.append("            .anyMatch(arc -> arc.to.equals(b));\n");
        fullCode.append("    }\n");
        fullCode.append("}\n\n");
        
        // Класс Node
        fullCode.append("class Node {\n");
        fullCode.append("    String id;\n");
        fullCode.append("    \n");
        fullCode.append("    public Node(String id) {\n");
        fullCode.append("        this.id = id;\n");
        fullCode.append("    }\n");
        fullCode.append("    \n");
        fullCode.append("    @Override\n");
        fullCode.append("    public String toString() {\n");
        fullCode.append("        return \"Node{\" + id + \"}\";\n");
        fullCode.append("    }\n");
        fullCode.append("    \n");
        fullCode.append("    @Override\n");
        fullCode.append("    public boolean equals(Object o) {\n");
        fullCode.append("        if (this == o) return true;\n");
        fullCode.append("        if (o == null || getClass() != o.getClass()) return false;\n");
        fullCode.append("        Node node = (Node) o;\n");
        fullCode.append("        return id.equals(node.id);\n");
        fullCode.append("    }\n");
        fullCode.append("    \n");
        fullCode.append("    @Override\n");
        fullCode.append("    public int hashCode() {\n");
        fullCode.append("        return id.hashCode();\n");
        fullCode.append("    }\n");
        fullCode.append("}\n\n");
        
        // Класс Arc
        fullCode.append("class Arc {\n");
        fullCode.append("    Node from;\n");
        fullCode.append("    Node to;\n");
        fullCode.append("    int weight;\n");
        fullCode.append("    \n");
        fullCode.append("    public Arc(Node from, Node to, int weight) {\n");
        fullCode.append("        this.from = from;\n");
        fullCode.append("        this.to = to;\n");
        fullCode.append("        this.weight = weight;\n");
        fullCode.append("    }\n");
        fullCode.append("    \n");
        fullCode.append("    @Override\n");
        fullCode.append("    public String toString() {\n");
        fullCode.append("        return \"Arc{\" + from + \" -> \" + to + \", weight=\" + weight + \"}\";\n");
        fullCode.append("    }\n");
        fullCode.append("}\n\n");
        
        // Основной класс
        fullCode.append("public class GeneratedGraphProgram {\n");
        
        // Стандартные функции
        fullCode.append("    public static Graph create_graph() {\n");
        fullCode.append("        return new Graph();\n");
        fullCode.append("    }\n\n");
        
        fullCode.append("    public static Node add_node(Graph graph, String id) {\n");
        fullCode.append("        return graph.addNode(id);\n");
        fullCode.append("    }\n\n");
        
        fullCode.append("    public static Arc add_arc(Graph graph, Node from, Node to, int weight) {\n");
        fullCode.append("        return graph.addArc(from, to, weight);\n");
        fullCode.append("    }\n\n");
        
        fullCode.append("    public static List<Node> get_nodes(Graph graph) {\n");
        fullCode.append("        return graph.getNodes();\n");
        fullCode.append("    }\n\n");
        
        fullCode.append("    public static boolean is_connected(Graph graph, Node a, Node b) {\n");
        fullCode.append("        return graph.isConnected(a, b);\n");
        fullCode.append("    }\n\n");
        
        fullCode.append("    public static void print(String text) {\n");
        fullCode.append("        System.out.print(text);\n");
        fullCode.append("    }\n\n");
        
        fullCode.append("    public static void println(String text) {\n");
        fullCode.append("        System.out.println(text);\n");
        fullCode.append("    }\n\n");
        
        // Пользовательские функции
        fullCode.append(functionCode.toString());
        
        // Основной метод
        fullCode.append(code.toString());
        
        fullCode.append("}\n");
        
        return fullCode.toString();
    }
    
    private void enterScope() {
        scopes.push(new HashMap<>());
    }
    
    private void exitScope() {
        scopes.pop();
    }
    
    private void defineVar(String name, String type, String javaType) {
        scopes.peek().put(name, new VariableInfo(type, javaType));
    }
    
    private String typeToJavaType(String type) {
        if (type.contains("<")) {
            int idx = type.indexOf("<");
            String base = type.substring(0, idx);
            String inner = type.substring(idx + 1, type.length() - 1);
            return "List<" + typeToJavaType(inner) + ">";
        }
        
        switch (type) {
            case "int": return "int";
            case "bool": return "boolean";
            case "float": return "double";
            case "string": return "String";
            case "graph": return "Graph";
            case "node": return "Node";
            case "arc": return "Arc";
            case "list": return "List";
            case "void": return "void";
            default: return "Object";
        }
    }
    
    private String generateIndent() {
        return "    ".repeat(indentLevel);
    }
    
    private void appendToCode(String line) {
        code.append(generateIndent()).append(line).append("\n");
    }
    
    private void appendToFunctionCode(String line) {
        functionCode.append(generateIndent()).append(line).append("\n");
    }
    
    @Override
    public String visitProgram(GraphLangParser.ProgramContext ctx) {
        appendToCode("public static void main(String[] args) {");
        indentLevel++;
        enterScope();
        
        for (GraphLangParser.StatementContext stmt : ctx.statement()) {
            visit(stmt);
        }
        
        exitScope();
        indentLevel--;
        appendToCode("}");
        return null;
    }
    
    @Override
    public String visitBlock(GraphLangParser.BlockContext ctx) {
        appendToCode("{");
        indentLevel++;
        enterScope();
        
        for (GraphLangParser.StatementContext stmt : ctx.statement()) {
            visit(stmt);
        }
        
        exitScope();
        indentLevel--;
        appendToCode("}");
        return null;
    }
    
    @Override
    public String visitDeclaration(GraphLangParser.DeclarationContext ctx) {
        String type = ctx.type().getText();
        String javaType = typeToJavaType(type);
        String varName = ctx.ID().getText();
        
        defineVar(varName, type, javaType);
        
        // Инициализация по умолчанию
        switch (type) {
            case "int":
                appendToCode(javaType + " " + varName + " = 0;");
                break;
            case "bool":
                appendToCode(javaType + " " + varName + " = false;");
                break;
            case "float":
                appendToCode(javaType + " " + varName + " = 0.0;");
                break;
            case "string":
                appendToCode(javaType + " " + varName + " = \"\";");
                break;
            case "graph":
                // Не инициализируем при объявлении, ждем присваивания
                appendToCode(javaType + " " + varName + ";");
                break;
            case "node":
                appendToCode(javaType + " " + varName + " = null;");
                break;
            case "arc":
                appendToCode(javaType + " " + varName + " = null;");
                break;
            default:
                if (type.startsWith("list<")) {
                    String innerType = type.substring(5, type.length() - 1);
                    String innerJavaType = typeToJavaType(innerType);
                    appendToCode("List<" + innerJavaType + "> " + varName + " = new ArrayList<>();");
                } else {
                    appendToCode(javaType + " " + varName + " = null;");
                }
        }
        return null;
    }
    
    // --- ИСПРАВЛЕННЫЙ МЕТОД ---
    @Override
    public String visitAssignment(GraphLangParser.AssignmentContext ctx) {
        String name = ctx.ID().getText();
        String value = visit(ctx.expr());
        
        // Используем метод класса, а не несуществующую переменную sb
        appendToCode(name + " = " + value + ";");
        
        return null;
    }
    
    // --- ДОБАВЛЕННЫЙ МЕТОД ---
    // Этот метод нужен, чтобы вызовы функций типа println("..."); попадали в код
    @Override
    public String visitStatement(GraphLangParser.StatementContext ctx) {
        // Если statement - это просто expr ';' (например, вызов функции)
        if (ctx.expr() != null) {
            String exprCode = visit(ctx.expr());
            appendToCode(exprCode + ";");
            return null;
        }
        return super.visitStatement(ctx);
    }
    
    @Override
    public String visitIf_stmt(GraphLangParser.If_stmtContext ctx) {
        String cond = visit(ctx.expr());
        appendToCode("if (" + cond + ") {");
        indentLevel++;
        visit(ctx.block(0));
        indentLevel--;
        
        if (ctx.ELSE() != null && ctx.block().size() > 1) {
            appendToCode("} else {");
            indentLevel++;
            visit(ctx.block(1));
            indentLevel--;
        }
        appendToCode("}");
        return null;
    }
    
    @Override
    public String visitOrExpr(GraphLangParser.OrExprContext ctx) {
        String left = visit(ctx.expr(0));
        String right = visit(ctx.expr(1));
        return "(" + left + " || " + right + ")";
    }
    
    @Override
    public String visitCmpExpr(GraphLangParser.CmpExprContext ctx) {
        String left = visit(ctx.expr(0));
        String right = visit(ctx.expr(1));
        String op = ctx.getChild(1).getText();
        return "(" + left + " " + op + " " + right + ")";
    }
    
    @Override
    public String visitAddSubExpr(GraphLangParser.AddSubExprContext ctx) {
        String left = visit(ctx.expr(0));
        String right = visit(ctx.expr(1));
        String op = ctx.getChild(1).getText();
        return "(" + left + " " + op + " " + right + ")";
    }
    
    @Override
    public String visitNotExpr(GraphLangParser.NotExprContext ctx) {
        String expr = visit(ctx.expr());
        return "(!" + expr + ")";
    }
    
    @Override
    public String visitFuncCallExpr(GraphLangParser.FuncCallExprContext ctx) {
        String funcName = ctx.ID().getText();
        StringBuilder call = new StringBuilder(funcName + "(");
        
        if (ctx.arg_list() != null) {
            List<String> args = new ArrayList<>();
            for (GraphLangParser.ExprContext arg : ctx.arg_list().expr()) {
                args.add(visit(arg));
            }
            call.append(String.join(", ", args));
        }
        call.append(")");
        
        return call.toString();
    }
    
    @Override
    public String visitIdExpr(GraphLangParser.IdExprContext ctx) {
        return ctx.ID().getText();
    }
    
    @Override
    public String visitLiteralExpr(GraphLangParser.LiteralExprContext ctx) {
        return generateLiteral(ctx.literal());
    }
    
    private String generateLiteral(GraphLangParser.LiteralContext ctx) {
        if (ctx.INT_LIT() != null) return ctx.INT_LIT().getText();
        if (ctx.FLOAT_LIT() != null) return ctx.FLOAT_LIT().getText();
        if (ctx.STRING_LIT() != null) {
            String str = ctx.STRING_LIT().getText();
            String content = str.substring(1, str.length() - 1);
            content = content.replace("\\", "\\\\")
                            .replace("\"", "\\\"")
                            .replace("\n", "\\n")
                            .replace("\t", "\\t");
            return "\"" + content + "\"";
        }
        if (ctx.BOOL_LIT() != null) return ctx.BOOL_LIT().getText();
        if (ctx.NULL() != null) return "null";
        return "null";
    }
}