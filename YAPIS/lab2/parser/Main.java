// Файл: Main.java
import org.antlr.v4.runtime.*;
import org.antlr.v4.runtime.tree.*;
import java.io.IOException;

public class Main {
    public static void main(String[] args) throws IOException {
        if (args.length == 0) {
            System.err.println("Ошибка: Укажите путь к файлу в качестве аргумента.");
            System.exit(1);
        }
        String inputFile = args[0];

        // Создаем лексер и парсер
        CharStream input = CharStreams.fromFileName(inputFile);
        GraphLangLexer lexer = new GraphLangLexer(input);
        CommonTokenStream tokens = new CommonTokenStream(lexer);
        GraphLangParser parser = new GraphLangParser(tokens);

        // Начинаем разбор с правила 'program'
        ParseTree tree = parser.program();

        // Выводим дерево разбора (AST) в консоль
        System.out.println("=== Дерево разбора (AST) ===");
        System.out.println(tree.toStringTree(parser));
    }
}