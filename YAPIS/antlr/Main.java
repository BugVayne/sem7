import org.antlr.v4.runtime.*;
import org.antlr.v4.runtime.tree.*;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.List;

public class Main {
    
    // Убедитесь, что пути правильные относительно папки запуска!
    private static final String[] TEST_FILES = {
        "examples/test_valid.gl",
        "examples/test_syntax_fail.gl",
        "examples/test_semantic_types.gl",
        "examples/test_semantic_scope.gl"
    };

    public static void main(String[] args) {
        System.out.println("==========================================");
        System.out.println("   ОТЛАДОЧНЫЙ ЗАПУСК GRAPH-LANG");
        System.out.println("==========================================");

        for (String filename : TEST_FILES) {
            System.out.println("\n--------------------------------------------------");
            System.out.println("ФАЙЛ: " + filename);
            System.out.println("--------------------------------------------------");

            if (!Files.exists(Paths.get(filename))) {
                System.out.println("!!! ОШИБКА: Файл не найден физически на диске !!!");
                continue;
            }

            try {
                // 1. Читаем и ПОКАЗЫВАЕМ содержимое
                String code = new String(Files.readAllBytes(Paths.get(filename)));
                if (code.trim().isEmpty()) {
                    System.out.println("!!! ВНИМАНИЕ: Файл пуст !!!");
                    continue;
                }
                
                System.out.println("[Содержимое файла]:\n" + code);
                System.out.println("\n[Анализ]:");

                processFile(code);

            } catch (Exception e) {
                System.out.println("КРИТИЧЕСКАЯ ОШИБКА JAVA: " + e.getMessage());
                e.printStackTrace();
            }
        }
    }

    private static void processFile(String code) {
        // 1. Лексер
        CharStream input = CharStreams.fromString(code);
        GraphLangLexer lexer = new GraphLangLexer(input);
        CommonTokenStream tokens = new CommonTokenStream(lexer);
        
        // Загружаем токены, чтобы проверить лексер
        tokens.fill();
        // System.out.println("Токены: " + tokens.getTokens()); // Раскомментируйте, если нужно видеть токены

        // 2. Парсер
        GraphLangParser parser = new GraphLangParser(tokens);
        
        // Важно: сброс и установка слушателя
        parser.removeErrorListeners();
        SyntaxErrorListener syntaxListener = new SyntaxErrorListener();
        parser.addErrorListener(syntaxListener);

        ParseTree tree = parser.program();

        // Проверка синтаксиса
        if (syntaxListener.hasErrors()) {
            System.out.println("СТАТУС: [СИНТАКСИЧЕСКИЕ ОШИБКИ]");
            for (String err : syntaxListener.getErrors()) {
                System.out.println("  ❌ " + err);
            }
            return; // Дальше не идем
        }

        System.out.println("Синтаксис: OK");

        // 3. Семантика
        GraphLangSemanticAnalyzer semanticAnalyzer = new GraphLangSemanticAnalyzer();
        semanticAnalyzer.visit(tree);

        List<String> semanticErrors = semanticAnalyzer.getErrors();

        if (semanticErrors.isEmpty()) {
            System.out.println("СТАТУС: [УСПЕХ] Ошибок нет.");
        } else {
            System.out.println("СТАТУС: [СЕМАНТИЧЕСКИЕ ОШИБКИ]");
            for (String err : semanticErrors) {
                System.out.println("  ❌ " + err);
            }
        }
    }

    static class SyntaxErrorListener extends BaseErrorListener {
        private final List<String> errors = new ArrayList<>();

        @Override
        public void syntaxError(Recognizer<?, ?> recognizer, Object offendingSymbol,
                                int line, int charPositionInLine, String msg,
                                RecognitionException e) {
            errors.add("Строка " + line + ":" + charPositionInLine + " -> " + msg);
        }

        public boolean hasErrors() { return !errors.isEmpty(); }
        public List<String> getErrors() { return errors; }
    }
}