// Generated from GraphLang.g4 by ANTLR 4.13.2
import org.antlr.v4.runtime.tree.ParseTreeVisitor;

/**
 * This interface defines a complete generic visitor for a parse tree produced
 * by {@link GraphLangParser}.
 *
 * @param <T> The return type of the visit operation. Use {@link Void} for
 * operations with no return type.
 */
public interface GraphLangVisitor<T> extends ParseTreeVisitor<T> {
	/**
	 * Visit a parse tree produced by {@link GraphLangParser#program}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitProgram(GraphLangParser.ProgramContext ctx);
	/**
	 * Visit a parse tree produced by {@link GraphLangParser#statement}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitStatement(GraphLangParser.StatementContext ctx);
	/**
	 * Visit a parse tree produced by {@link GraphLangParser#block}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitBlock(GraphLangParser.BlockContext ctx);
	/**
	 * Visit a parse tree produced by {@link GraphLangParser#declaration}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitDeclaration(GraphLangParser.DeclarationContext ctx);
	/**
	 * Visit a parse tree produced by {@link GraphLangParser#assignment}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitAssignment(GraphLangParser.AssignmentContext ctx);
	/**
	 * Visit a parse tree produced by {@link GraphLangParser#if_stmt}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitIf_stmt(GraphLangParser.If_stmtContext ctx);
	/**
	 * Visit a parse tree produced by {@link GraphLangParser#switch_stmt}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitSwitch_stmt(GraphLangParser.Switch_stmtContext ctx);
	/**
	 * Visit a parse tree produced by {@link GraphLangParser#case_block}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitCase_block(GraphLangParser.Case_blockContext ctx);
	/**
	 * Visit a parse tree produced by {@link GraphLangParser#default_block}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitDefault_block(GraphLangParser.Default_blockContext ctx);
	/**
	 * Visit a parse tree produced by {@link GraphLangParser#until_stmt}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitUntil_stmt(GraphLangParser.Until_stmtContext ctx);
	/**
	 * Visit a parse tree produced by {@link GraphLangParser#function_def}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitFunction_def(GraphLangParser.Function_defContext ctx);
	/**
	 * Visit a parse tree produced by {@link GraphLangParser#param_list}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitParam_list(GraphLangParser.Param_listContext ctx);
	/**
	 * Visit a parse tree produced by {@link GraphLangParser#param}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitParam(GraphLangParser.ParamContext ctx);
	/**
	 * Visit a parse tree produced by {@link GraphLangParser#return_stmt}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitReturn_stmt(GraphLangParser.Return_stmtContext ctx);
	/**
	 * Visit a parse tree produced by the {@code CmpExpr}
	 * labeled alternative in {@link GraphLangParser#expr}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitCmpExpr(GraphLangParser.CmpExprContext ctx);
	/**
	 * Visit a parse tree produced by the {@code PrimaryExpr}
	 * labeled alternative in {@link GraphLangParser#expr}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitPrimaryExpr(GraphLangParser.PrimaryExprContext ctx);
	/**
	 * Visit a parse tree produced by the {@code NotExpr}
	 * labeled alternative in {@link GraphLangParser#expr}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitNotExpr(GraphLangParser.NotExprContext ctx);
	/**
	 * Visit a parse tree produced by the {@code AddSubExpr}
	 * labeled alternative in {@link GraphLangParser#expr}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitAddSubExpr(GraphLangParser.AddSubExprContext ctx);
	/**
	 * Visit a parse tree produced by the {@code OrExpr}
	 * labeled alternative in {@link GraphLangParser#expr}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitOrExpr(GraphLangParser.OrExprContext ctx);
	/**
	 * Visit a parse tree produced by the {@code IdExpr}
	 * labeled alternative in {@link GraphLangParser#primary}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitIdExpr(GraphLangParser.IdExprContext ctx);
	/**
	 * Visit a parse tree produced by the {@code LiteralExpr}
	 * labeled alternative in {@link GraphLangParser#primary}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitLiteralExpr(GraphLangParser.LiteralExprContext ctx);
	/**
	 * Visit a parse tree produced by the {@code ParenExpr}
	 * labeled alternative in {@link GraphLangParser#primary}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitParenExpr(GraphLangParser.ParenExprContext ctx);
	/**
	 * Visit a parse tree produced by the {@code IndexExpr}
	 * labeled alternative in {@link GraphLangParser#primary}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitIndexExpr(GraphLangParser.IndexExprContext ctx);
	/**
	 * Visit a parse tree produced by the {@code FuncCallExpr}
	 * labeled alternative in {@link GraphLangParser#primary}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitFuncCallExpr(GraphLangParser.FuncCallExprContext ctx);
	/**
	 * Visit a parse tree produced by {@link GraphLangParser#arg_list}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitArg_list(GraphLangParser.Arg_listContext ctx);
	/**
	 * Visit a parse tree produced by {@link GraphLangParser#type}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitType(GraphLangParser.TypeContext ctx);
	/**
	 * Visit a parse tree produced by {@link GraphLangParser#simple_type}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitSimple_type(GraphLangParser.Simple_typeContext ctx);
	/**
	 * Visit a parse tree produced by {@link GraphLangParser#literal}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitLiteral(GraphLangParser.LiteralContext ctx);
}