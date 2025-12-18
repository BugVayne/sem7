import java.io.*;
import java.util.*;

public class TestRunner {
    
    // List of files to test
    private static final String[] TEST_FILES = {
        "test_complex.gl",
        "test_logic.gl",
        "error_syntax.gl",
        "error_semantic.gl",
        "program.gl"
    };

    public static void main(String[] args) {
        System.out.println("=========================================");
        System.out.println("      AUTOMATED COMPILER TESTS");
        System.out.println("=========================================\n");

        int passed = 0;
        int failed = 0;

        for (String fileName : TEST_FILES) {
            System.out.println(">>> TESTING FILE: " + fileName);
            boolean compilerSuccess = runCompiler(fileName);
            
            // Logic: 
            // Files starting with 'test_' MUST succeed.
            // Files starting with 'error_' MUST fail compilation.
            
            boolean testPassed;
            if (fileName.startsWith("error_")) {
                // For error files, success means the compiler returned an error code
                testPassed = !compilerSuccess; 
                
                if (testPassed) {
                    System.out.println("   [OK] Compiler caught the error as expected.");
                } else {
                    System.out.println("   [FAIL] Compiler accepted invalid code (It should have failed!)");
                }
            } else {
                // For normal files, success means exit code 0
                testPassed = compilerSuccess;
                
                if (testPassed) {
                    System.out.println("   [OK] Execution successful.");
                } else {
                    System.out.println("   [FAIL] Compilation or execution error.");
                }
            }

            if (testPassed) passed++; else failed++;
            System.out.println("-----------------------------------------");
        }

        System.out.println("\nSUMMARY:");
        System.out.println("Total Tests: " + TEST_FILES.length);
        System.out.println("Passed:      " + passed);
        System.out.println("Failed:      " + failed);
        
        if (failed > 0) System.exit(1);
    }

    private static boolean runCompiler(String fileName) {
        try {
            // Command: java -cp ... GraphLangCompiler fileName --run
            // Note: Use ";" for Windows classpath, ":" for Linux/Mac
            String classpath = ".;antlr-4.13.2-complete.jar";
            
            ProcessBuilder pb = new ProcessBuilder(
                "java", 
                "-cp", classpath, 
                "GraphLangCompiler", 
                fileName, 
                "--run"
            );
            
            pb.redirectErrorStream(true); // Merge stdout and stderr
            Process process = pb.start();

            // Read output
            BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
            String line;
            while ((line = reader.readLine()) != null) {
                // Filter logs to show only relevant info
                // We want to see output from the program (println) and Errors
                
                boolean isImportant = line.contains("Error") || 
                                      line.contains("error") || 
                                      line.contains("Exception") ||
                                      line.trim().startsWith("Result:") ||
                                      line.trim().matches("^[0-9].*") || // Numbered lists
                                      !line.startsWith("["); // Hide compiler stages [1/5]...

                // Skip blank lines or standard headers
                if (line.trim().isEmpty() || line.contains("GraphLang Compiler") || line.contains("===")) continue;

                if (isImportant) {
                    System.out.println("   LOG: " + line);
                }
            }

            int exitCode = process.waitFor();
            return exitCode == 0;

        } catch (Exception e) {
            System.out.println("   CRITICAL SYSTEM ERROR: " + e.getMessage());
            return false;
        }
    }
}