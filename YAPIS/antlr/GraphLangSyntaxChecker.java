import org.antlr.v4.runtime.*;
import org.antlr.v4.runtime.tree.*;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;

public class GraphLangSyntaxChecker {
    
    // Тестовые примеры как поля класса
    private static final String correctCode1 = 
        "graph g;\n" +
        "g = create_graph();\n" +
        "node n1;\n" +
        "n1 = add_node(g, \"Node1\");";

    private static final String correctCode2 = 
        "if (x != null) then {\n" +
        "    write(\"Valid\");\n" +
        "} else {\n" +
        "    write(\"Invalid\");\n" +
        "}";

    private static final String errorCode1 = 
        "graph g\n" +
        "g = create_graph()";

    private static final String errorCode2 = 
        "if (x = y) then { write(\"Error\"); }";

    private static final String errorCode3 = 
        "int x;\n" +
        "x = \"string_value\";";

    public static void main(String[] args) {
        // Если передан аргумент - проверяем файл
        if (args.length > 0) {
            String filename = args[0];
            checkFileSyntax(filename);
        } else {
            // Иначе запускаем стандартные тесты
            runStandardTests();
        }
    }
    
    public static void runStandardTests() {
        String[] testCases = {
            correctCode1,
            correctCode2,
            errorCode1,
            errorCode2,
            errorCode3
        };
        
        for (int i = 0; i < testCases.length; i++) {
            String code = testCases[i];
            System.out.println("=== Тест " + (i + 1) + " ===");
            System.out.println("Проверка кода:");
            System.out.println(code);
            System.out.println("---");
            try {
                checkSyntax(code);
                System.out.println("✓ Синтаксис корректен\n");
            } catch (SyntaxException e) {
                System.out.println("✗ Ошибка: " + e.getMessage() + "\n");
            }
        }
    }
    
    public static void checkFileSyntax(String filename) {
        System.out.println("Проверка файла: " + filename);
        System.out.println("=========================================");
        
        try {
            String content = readFile(filename);
            System.out.println("Содержимое файла:");
            System.out.println(content);
            System.out.println("=========================================");
            
            checkSyntax(content);
            System.out.println("✓ Файл " + filename + " синтаксически корректен!");
            
        } catch (IOException e) {
            System.err.println("✗ Ошибка чтения файла: " + e.getMessage());
        } catch (SyntaxException e) {
            System.err.println("✗ Синтаксическая ошибка в файле: " + e.getMessage());
        }
    }
    
    public static String readFile(String filename) throws IOException {
        return new String(Files.readAllBytes(Paths.get(filename)));
    }
    
    public static void checkSyntax(String code) throws SyntaxException {
        CharStream input = CharStreams.fromString(code);
        GraphLangLexer lexer = new GraphLangLexer(input);
        CommonTokenStream tokens = new CommonTokenStream(lexer);
        GraphLangParser parser = new GraphLangParser(tokens);
        
        parser.removeErrorListeners();
        parser.addErrorListener(new BaseErrorListener() {
            @Override
            public void syntaxError(Recognizer<?, ?> recognizer,
                                    Object offendingSymbol,
                                    int line,
                                    int charPositionInLine,
                                    String msg,
                                    RecognitionException e) {
                throw new SyntaxException(line, charPositionInLine, msg);
            }
        });
        
        try {
            ParseTree tree = parser.program();
            System.out.println("Дерево разбора создано успешно");
        } catch (SyntaxException e) {
            throw e;
        } catch (Exception e) {
            throw new SyntaxException(-1, -1, "Неожиданная ошибка: " + e.getMessage());
        }
    }
    
    static class SyntaxException extends RuntimeException {
        final int line;
        final int position;
        
        SyntaxException(int line, int position, String message) {
            super(String.format("Строка %d:%d - %s", line, position, message));
            this.line = line;
            this.position = position;
        }
    }
}