// Файл: GraphLangSemanticAnalyzer.java
import org.antlr.v4.runtime.tree.ParseTree;
import java.util.*;

public class GraphLangSemanticAnalyzer extends GraphLangBaseVisitor<String> {

    private final Stack<Map<String, String>> scopes = new Stack<>();
    private final Map<String, String> functions = new HashMap<>();
    private final List<String> errors = new ArrayList<>();

    public GraphLangSemanticAnalyzer() {
        scopes.push(new HashMap<>());
        // Стандартные функции
        functions.put("create_graph", "graph");
        functions.put("add_node", "node");
        functions.put("write", "void");
        functions.put("print", "void");
        functions.put("check_path", "bool");
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
        // Важно: вызываем visit явно для блоков, чтобы сработал visitBlock и создались области видимости
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
        // --- ИЗМЕНЕНИЕ ЗДЕСЬ: Поддержка bool ---
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
        if (functions.containsKey(name)) {
            if (ctx.arg_list() != null) {
                for (GraphLangParser.ExprContext e : ctx.arg_list().expr()) visit(e);
            }
            return functions.get(name);
        }
        errors.add("Ошибка: Неизвестная функция '" + name + "'");
        return "unknown";
    }

    private boolean typesCompatible(String target, String source) {
        if (target.equals(source)) return true;
        if (target.equals("float") && source.equals("int")) return true;
        if (source.equals("null") && (target.equals("graph") || target.equals("node"))) return true;
        // Особый случай для unknown, чтобы не спамить ошибками
        if (target.equals("unknown") || source.equals("unknown")) return true;
        return false;
    }
}