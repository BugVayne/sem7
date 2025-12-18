// GraphLangCompiler.java
import org.antlr.v4.runtime.*;
import org.antlr.v4.runtime.tree.*;
import java.io.*;
import java.nio.file.*;

public class GraphLangCompiler {
    
    public static void main(String[] args) throws IOException {
        if (args.length < 1) {
            System.out.println("Использование:");
            System.out.println("  java GraphLangCompiler <input.gl> [output.java] [--run]");
            System.out.println("\nОпции:");
            System.out.println("  --run    : Скомпилировать и сразу запустить программу");
            System.exit(1);
        }
        
        String inputFile = args[0];
        String outputFile = "GeneratedGraphProgram.java"; // Всегда генерируем этот файл
        boolean runAfterCompile = false;
        
        // Парсим аргументы
        for (int i = 1; i < args.length; i++) {
            if (args[i].equals("--run")) {
                runAfterCompile = true;
            } else if (!args[i].startsWith("--")) {
                outputFile = args[i];
            }
        }
        
        System.out.println("=========================================");
        System.out.println("     GraphLang Compiler v2.0");
        System.out.println("=========================================");
        System.out.println("Входной файл:  " + inputFile);
        System.out.println("Выходной файл: " + outputFile);
        
        try {
            // 1. Чтение исходного кода
            System.out.println("\n[1/5] Чтение исходного файла...");
            String sourceCode = new String(Files.readAllBytes(Paths.get(inputFile)));
            
            // 2. Лексический и синтаксический анализ
            System.out.println("[2/5] Лексический и синтаксический анализ...");
            CharStream input = CharStreams.fromString(sourceCode);
            GraphLangLexer lexer = new GraphLangLexer(input);
            CommonTokenStream tokens = new CommonTokenStream(lexer);
            GraphLangParser parser = new GraphLangParser(tokens);
            
            // Установка обработчика ошибок
            parser.removeErrorListeners();
            parser.addErrorListener(new BaseErrorListener() {
                @Override
                public void syntaxError(Recognizer<?, ?> recognizer,
                                        Object offendingSymbol,
                                        int line,
                                        int charPositionInLine,
                                        String msg,
                                        RecognitionException e) {
                    throw new RuntimeException("Синтаксическая ошибка в строке " + line + 
                                               ":" + charPositionInLine + " - " + msg);
                }
            });
            
            ParseTree tree = parser.program();
            System.out.println("✓ Синтаксический анализ успешен");
            
            // 3. Семантический анализ
            System.out.println("[3/5] Семантический анализ...");
            GraphLangSemanticAnalyzer semanticAnalyzer = new GraphLangSemanticAnalyzer();
            semanticAnalyzer.visit(tree);
            
            if (!semanticAnalyzer.getErrors().isEmpty()) {
                System.out.println("\n✗ Семантические ошибки:");
                for (String error : semanticAnalyzer.getErrors()) {
                    System.out.println("  " + error);
                }
                System.exit(1);
            }
            System.out.println("✓ Семантический анализ успешен");
            
            // 4. Генерация кода
            System.out.println("[4/5] Генерация Java-кода...");
            GraphLangCodeGenerator codeGenerator = new GraphLangCodeGenerator();
            codeGenerator.visit(tree);
            String javaCode = codeGenerator.getGeneratedCode();
            
            // Запись результата
            Files.write(Paths.get(outputFile), javaCode.getBytes());
            System.out.println("✓ Java-код сгенерирован: " + outputFile);
            
            // 5. Компиляция Java-кода
            System.out.println("[5/5] Компиляция Java-кода...");
            ProcessBuilder pb = new ProcessBuilder("javac", outputFile);
            Process process = pb.start();
            
            // Читаем вывод компилятора
            BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
            String line;
            boolean hasErrors = false;
            while ((line = reader.readLine()) != null) {
                if (line.contains("error")) {
                    System.err.println("Java compilation error: " + line);
                    hasErrors = true;
                }
            }
            
            int exitCode = process.waitFor();
            if (exitCode != 0 || hasErrors) {
                throw new RuntimeException("Ошибка компиляции Java-кода");
            }
            
            System.out.println("✓ Java-код успешно скомпилирован");
            
            System.out.println("\n=========================================");
            System.out.println("✓ Компиляция успешно завершена!");
            System.out.println("=========================================");
            
            // 6. Запуск программы (если указано)
            if (runAfterCompile) {
                System.out.println("\nЗапуск программы:");
                System.out.println("-----------------------------------------");
                runJavaProgram();
            } else {
                System.out.println("\nДля запуска программы выполните:");
                System.out.println("  java GeneratedGraphProgram");
                System.out.println("\nИли перекомпилируйте с опцией --run");
            }
            
        } catch (Exception e) {
            System.err.println("\n✗ Ошибка компиляции: " + e.getMessage());
            e.printStackTrace();
            System.exit(1);
        }
    }
    
    private static void runJavaProgram() throws IOException, InterruptedException {
        ProcessBuilder pb = new ProcessBuilder("java", "GeneratedGraphProgram");
        pb.redirectErrorStream(true);
        
        Process process = pb.start();
        
        // Чтение вывода программы
        BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
        String line;
        while ((line = reader.readLine()) != null) {
            System.out.println(line);
        }
        
        process.waitFor();
    }
}