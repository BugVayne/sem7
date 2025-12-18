import org.antlr.v4.runtime.tree.ParseTree;
import java.util.*;

public class GraphLangSemanticAnalyzer extends GraphLangBaseVisitor<String> {

    private final Stack<Map<String, String>> scopes = new Stack<>();
    private final Map<String, FunctionInfo> functions = new HashMap<>();
    private final List<String> errors = new ArrayList<>();

    private static class FunctionInfo {
        String returnType;
        List<String> paramTypes;
        
        FunctionInfo(String returnType, List<String> paramTypes) {
            this.returnType = returnType;
            this.paramTypes = paramTypes;
        }
    }

    public GraphLangSemanticAnalyzer() {
        scopes.push(new HashMap<>());
        
        // Добавляем ВСЕ стандартные функции, которые есть в кодогенераторе
        defineStandardFunctions();
    }

    private void defineStandardFunctions() {
        // Графовые операции
        functions.put("create_graph", new FunctionInfo("graph", Arrays.asList()));
        functions.put("add_node", new FunctionInfo("node", Arrays.asList("graph", "string")));
        functions.put("add_arc", new FunctionInfo("arc", Arrays.asList("graph", "node", "node", "int")));
        functions.put("remove_node", new FunctionInfo("bool", Arrays.asList("graph", "node")));
        functions.put("remove_arc", new FunctionInfo("bool", Arrays.asList("graph", "arc")));
        
        // Операции с графами
        functions.put("get_nodes", new FunctionInfo("list<node>", Arrays.asList("graph")));
        functions.put("get_arcs", new FunctionInfo("list<arc>", Arrays.asList("graph")));
        functions.put("find_path", new FunctionInfo("list<node>", Arrays.asList("graph", "node", "node")));
        functions.put("is_connected", new FunctionInfo("bool", Arrays.asList("graph", "node", "node")));
        
        // Ввод-вывод
        functions.put("write", new FunctionInfo("void", Arrays.asList("string")));
        functions.put("print", new FunctionInfo("void", Arrays.asList("string")));
        functions.put("println", new FunctionInfo("void", Arrays.asList("string")));
        functions.put("read_line", new FunctionInfo("string", Arrays.asList()));
        functions.put("read_int", new FunctionInfo("int", Arrays.asList()));
        
        // Математические функции
        functions.put("abs", new FunctionInfo("int", Arrays.asList("int")));
        functions.put("sqrt", new FunctionInfo("float", Arrays.asList("float")));
        functions.put("pow", new FunctionInfo("float", Arrays.asList("float", "float")));
        
        // Операции со списками
        functions.put("create_list", new FunctionInfo("list", Arrays.asList()));
        functions.put("add_to_list", new FunctionInfo("void", Arrays.asList("list", "object")));
        functions.put("get_from_list", new FunctionInfo("object", Arrays.asList("list", "int")));
        
        // Старые функции для обратной совместимости
        functions.put("check_path", new FunctionInfo("bool", Arrays.asList("graph", "node", "node")));
    }

    public List<String> getErrors() { return errors; }

    private void enterScope() { scopes.push(new HashMap<>()); }
    private void exitScope() { scopes.pop(); }

    private void defineVar(String name, String type) {
        if (scopes.peek().containsKey(name)) {
            errors.add("Ошибка: Переменная '" + name + "' уже объявлена.");
        } else {
            scopes.peek().put(name, type);
        }
    }

    private String resolveVar(String name) {
        for (int i = scopes.size() - 1; i >= 0; i--) {
            if (scopes.get(i).containsKey(name)) return scopes.get(i).get(name);
        }
        return null;
    }

    @Override
    public String visitBlock(GraphLangParser.BlockContext ctx) {
        enterScope();
        super.visitBlock(ctx);
        exitScope();
        return null;
    }

    @Override
    public String visitDeclaration(GraphLangParser.DeclarationContext ctx) {
        defineVar(ctx.ID().getText(), ctx.type().getText());
        return null;
    }

    @Override
    public String visitAssignment(GraphLangParser.AssignmentContext ctx) {
        String name = ctx.ID().getText();
        String varType = resolveVar(name);
        if (varType == null) {
            errors.add("Ошибка: Присваивание неопределенной переменной '" + name + "'.");
            return null;
        }
        String exprType = visit(ctx.expr());
        if (exprType != null && !typesCompatible(varType, exprType)) {
            errors.add("Ошибка типов: Нельзя присвоить '" + exprType + "' переменной типа '" + varType + "' (" + name + ").");
        }
        return null;
    }

    @Override
    public String visitIf_stmt(GraphLangParser.If_stmtContext ctx) {
        String condType = visit(ctx.expr());
        if (condType != null && !condType.equals("bool")) {
            errors.add("Ошибка: Условие if должно быть bool, получено: " + condType);
        }
        for (GraphLangParser.BlockContext b : ctx.block()) {
            visit(b);
        }
        return null;
    }

    @Override
    public String visitUntil_stmt(GraphLangParser.Until_stmtContext ctx) {
        String condType = visit(ctx.expr());
        if (condType != null && !condType.equals("bool")) {
            errors.add("Ошибка: Условие until должно быть bool");
        }
        visit(ctx.block());
        return null;
    }

    @Override
    public String visitIdExpr(GraphLangParser.IdExprContext ctx) {
        String type = resolveVar(ctx.ID().getText());
        if (type == null) {
            errors.add("Ошибка: Переменная '" + ctx.ID().getText() + "' не найдена.");
            return "unknown";
        }
        return type;
    }

    @Override
    public String visitLiteralExpr(GraphLangParser.LiteralExprContext ctx) {
        if (ctx.literal().INT_LIT() != null) return "int";
        if (ctx.literal().FLOAT_LIT() != null) return "float";
        if (ctx.literal().STRING_LIT() != null) return "string";
        if (ctx.literal().NULL() != null) return "null";
        if (ctx.literal().BOOL_LIT() != null) return "bool"; 
        return "unknown";
    }

    @Override
    public String visitAddSubExpr(GraphLangParser.AddSubExprContext ctx) {
        String left = visit(ctx.expr(0));
        String right = visit(ctx.expr(1));
        if (left.equals("int") && right.equals("int")) return "int";
        if ((left.equals("float") || left.equals("int")) && (right.equals("float") || right.equals("int"))) return "float";
        errors.add("Ошибка: Нельзя сложить/вычесть " + left + " и " + right);
        return "unknown";
    }

    @Override
    public String visitCmpExpr(GraphLangParser.CmpExprContext ctx) {
        String left = visit(ctx.expr(0));
        String right = visit(ctx.expr(1));
        if (!typesCompatible(left, right) && !typesCompatible(right, left)) {
             errors.add("Ошибка: Сравнение разных типов " + left + " и " + right);
        }
        return "bool";
    }
    
    @Override
    public String visitFuncCallExpr(GraphLangParser.FuncCallExprContext ctx) {
        String name = ctx.ID().getText();
        FunctionInfo funcInfo = functions.get(name);
        
        if (funcInfo != null) {
            // Проверяем количество аргументов
            List<String> argTypes = new ArrayList<>();
            if (ctx.arg_list() != null) {
                for (GraphLangParser.ExprContext e : ctx.arg_list().expr()) {
                    argTypes.add(visit(e));
                }
                
                // Простая проверка количества аргументов
                if (argTypes.size() != funcInfo.paramTypes.size()) {
                    errors.add("Ошибка: Функция '" + name + "' ожидает " + funcInfo.paramTypes.size() + 
                              " аргументов, получено " + argTypes.size());
                }
            } else {
                if (!funcInfo.paramTypes.isEmpty()) {
                    errors.add("Ошибка: Функция '" + name + "' ожидает " + funcInfo.paramTypes.size() + 
                              " аргументов, получено 0");
                }
            }
            return funcInfo.returnType;
        }
        
        errors.add("Ошибка: Неизвестная функция '" + name + "'");
        return "unknown";
    }

    private boolean typesCompatible(String target, String source) {
        if (target.equals(source)) return true;
        if (target.equals("float") && source.equals("int")) return true;
        if (source.equals("null") && (target.equals("graph") || target.equals("node") || 
                                      target.equals("arc") || target.equals("list"))) return true;
        // Для generic типов
        if (target.startsWith("list<") && source.equals("list")) return true;
        if (source.startsWith("list<") && target.equals("list")) return true;
        // Особый случай для unknown, чтобы не спамить ошибками
        if (target.equals("unknown") || source.equals("unknown")) return true;
        return false;
    }
}