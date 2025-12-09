// Generated from GraphLang.g4 by ANTLR 4.13.2
import org.antlr.v4.runtime.tree.ParseTreeListener;

/**
 * This interface defines a complete listener for a parse tree produced by
 * {@link GraphLangParser}.
 */
public interface GraphLangListener extends ParseTreeListener {
	/**
	 * Enter a parse tree produced by {@link GraphLangParser#program}.
	 * @param ctx the parse tree
	 */
	void enterProgram(GraphLangParser.ProgramContext ctx);
	/**
	 * Exit a parse tree produced by {@link GraphLangParser#program}.
	 * @param ctx the parse tree
	 */
	void exitProgram(GraphLangParser.ProgramContext ctx);
	/**
	 * Enter a parse tree produced by {@link GraphLangParser#statement}.
	 * @param ctx the parse tree
	 */
	void enterStatement(GraphLangParser.StatementContext ctx);
	/**
	 * Exit a parse tree produced by {@link GraphLangParser#statement}.
	 * @param ctx the parse tree
	 */
	void exitStatement(GraphLangParser.StatementContext ctx);
	/**
	 * Enter a parse tree produced by {@link GraphLangParser#block}.
	 * @param ctx the parse tree
	 */
	void enterBlock(GraphLangParser.BlockContext ctx);
	/**
	 * Exit a parse tree produced by {@link GraphLangParser#block}.
	 * @param ctx the parse tree
	 */
	void exitBlock(GraphLangParser.BlockContext ctx);
	/**
	 * Enter a parse tree produced by {@link GraphLangParser#declaration}.
	 * @param ctx the parse tree
	 */
	void enterDeclaration(GraphLangParser.DeclarationContext ctx);
	/**
	 * Exit a parse tree produced by {@link GraphLangParser#declaration}.
	 * @param ctx the parse tree
	 */
	void exitDeclaration(GraphLangParser.DeclarationContext ctx);
	/**
	 * Enter a parse tree produced by {@link GraphLangParser#assignment}.
	 * @param ctx the parse tree
	 */
	void enterAssignment(GraphLangParser.AssignmentContext ctx);
	/**
	 * Exit a parse tree produced by {@link GraphLangParser#assignment}.
	 * @param ctx the parse tree
	 */
	void exitAssignment(GraphLangParser.AssignmentContext ctx);
	/**
	 * Enter a parse tree produced by {@link GraphLangParser#if_stmt}.
	 * @param ctx the parse tree
	 */
	void enterIf_stmt(GraphLangParser.If_stmtContext ctx);
	/**
	 * Exit a parse tree produced by {@link GraphLangParser#if_stmt}.
	 * @param ctx the parse tree
	 */
	void exitIf_stmt(GraphLangParser.If_stmtContext ctx);
	/**
	 * Enter a parse tree produced by {@link GraphLangParser#switch_stmt}.
	 * @param ctx the parse tree
	 */
	void enterSwitch_stmt(GraphLangParser.Switch_stmtContext ctx);
	/**
	 * Exit a parse tree produced by {@link GraphLangParser#switch_stmt}.
	 * @param ctx the parse tree
	 */
	void exitSwitch_stmt(GraphLangParser.Switch_stmtContext ctx);
	/**
	 * Enter a parse tree produced by {@link GraphLangParser#case_block}.
	 * @param ctx the parse tree
	 */
	void enterCase_block(GraphLangParser.Case_blockContext ctx);
	/**
	 * Exit a parse tree produced by {@link GraphLangParser#case_block}.
	 * @param ctx the parse tree
	 */
	void exitCase_block(GraphLangParser.Case_blockContext ctx);
	/**
	 * Enter a parse tree produced by {@link GraphLangParser#default_block}.
	 * @param ctx the parse tree
	 */
	void enterDefault_block(GraphLangParser.Default_blockContext ctx);
	/**
	 * Exit a parse tree produced by {@link GraphLangParser#default_block}.
	 * @param ctx the parse tree
	 */
	void exitDefault_block(GraphLangParser.Default_blockContext ctx);
	/**
	 * Enter a parse tree produced by {@link GraphLangParser#until_stmt}.
	 * @param ctx the parse tree
	 */
	void enterUntil_stmt(GraphLangParser.Until_stmtContext ctx);
	/**
	 * Exit a parse tree produced by {@link GraphLangParser#until_stmt}.
	 * @param ctx the parse tree
	 */
	void exitUntil_stmt(GraphLangParser.Until_stmtContext ctx);
	/**
	 * Enter a parse tree produced by {@link GraphLangParser#function_def}.
	 * @param ctx the parse tree
	 */
	void enterFunction_def(GraphLangParser.Function_defContext ctx);
	/**
	 * Exit a parse tree produced by {@link GraphLangParser#function_def}.
	 * @param ctx the parse tree
	 */
	void exitFunction_def(GraphLangParser.Function_defContext ctx);
	/**
	 * Enter a parse tree produced by {@link GraphLangParser#param_list}.
	 * @param ctx the parse tree
	 */
	void enterParam_list(GraphLangParser.Param_listContext ctx);
	/**
	 * Exit a parse tree produced by {@link GraphLangParser#param_list}.
	 * @param ctx the parse tree
	 */
	void exitParam_list(GraphLangParser.Param_listContext ctx);
	/**
	 * Enter a parse tree produced by {@link GraphLangParser#param}.
	 * @param ctx the parse tree
	 */
	void enterParam(GraphLangParser.ParamContext ctx);
	/**
	 * Exit a parse tree produced by {@link GraphLangParser#param}.
	 * @param ctx the parse tree
	 */
	void exitParam(GraphLangParser.ParamContext ctx);
	/**
	 * Enter a parse tree produced by {@link GraphLangParser#return_stmt}.
	 * @param ctx the parse tree
	 */
	void enterReturn_stmt(GraphLangParser.Return_stmtContext ctx);
	/**
	 * Exit a parse tree produced by {@link GraphLangParser#return_stmt}.
	 * @param ctx the parse tree
	 */
	void exitReturn_stmt(GraphLangParser.Return_stmtContext ctx);
	/**
	 * Enter a parse tree produced by the {@code CmpExpr}
	 * labeled alternative in {@link GraphLangParser#expr}.
	 * @param ctx the parse tree
	 */
	void enterCmpExpr(GraphLangParser.CmpExprContext ctx);
	/**
	 * Exit a parse tree produced by the {@code CmpExpr}
	 * labeled alternative in {@link GraphLangParser#expr}.
	 * @param ctx the parse tree
	 */
	void exitCmpExpr(GraphLangParser.CmpExprContext ctx);
	/**
	 * Enter a parse tree produced by the {@code PrimaryExpr}
	 * labeled alternative in {@link GraphLangParser#expr}.
	 * @param ctx the parse tree
	 */
	void enterPrimaryExpr(GraphLangParser.PrimaryExprContext ctx);
	/**
	 * Exit a parse tree produced by the {@code PrimaryExpr}
	 * labeled alternative in {@link GraphLangParser#expr}.
	 * @param ctx the parse tree
	 */
	void exitPrimaryExpr(GraphLangParser.PrimaryExprContext ctx);
	/**
	 * Enter a parse tree produced by the {@code NotExpr}
	 * labeled alternative in {@link GraphLangParser#expr}.
	 * @param ctx the parse tree
	 */
	void enterNotExpr(GraphLangParser.NotExprContext ctx);
	/**
	 * Exit a parse tree produced by the {@code NotExpr}
	 * labeled alternative in {@link GraphLangParser#expr}.
	 * @param ctx the parse tree
	 */
	void exitNotExpr(GraphLangParser.NotExprContext ctx);
	/**
	 * Enter a parse tree produced by the {@code AddSubExpr}
	 * labeled alternative in {@link GraphLangParser#expr}.
	 * @param ctx the parse tree
	 */
	void enterAddSubExpr(GraphLangParser.AddSubExprContext ctx);
	/**
	 * Exit a parse tree produced by the {@code AddSubExpr}
	 * labeled alternative in {@link GraphLangParser#expr}.
	 * @param ctx the parse tree
	 */
	void exitAddSubExpr(GraphLangParser.AddSubExprContext ctx);
	/**
	 * Enter a parse tree produced by the {@code OrExpr}
	 * labeled alternative in {@link GraphLangParser#expr}.
	 * @param ctx the parse tree
	 */
	void enterOrExpr(GraphLangParser.OrExprContext ctx);
	/**
	 * Exit a parse tree produced by the {@code OrExpr}
	 * labeled alternative in {@link GraphLangParser#expr}.
	 * @param ctx the parse tree
	 */
	void exitOrExpr(GraphLangParser.OrExprContext ctx);
	/**
	 * Enter a parse tree produced by the {@code IdExpr}
	 * labeled alternative in {@link GraphLangParser#primary}.
	 * @param ctx the parse tree
	 */
	void enterIdExpr(GraphLangParser.IdExprContext ctx);
	/**
	 * Exit a parse tree produced by the {@code IdExpr}
	 * labeled alternative in {@link GraphLangParser#primary}.
	 * @param ctx the parse tree
	 */
	void exitIdExpr(GraphLangParser.IdExprContext ctx);
	/**
	 * Enter a parse tree produced by the {@code LiteralExpr}
	 * labeled alternative in {@link GraphLangParser#primary}.
	 * @param ctx the parse tree
	 */
	void enterLiteralExpr(GraphLangParser.LiteralExprContext ctx);
	/**
	 * Exit a parse tree produced by the {@code LiteralExpr}
	 * labeled alternative in {@link GraphLangParser#primary}.
	 * @param ctx the parse tree
	 */
	void exitLiteralExpr(GraphLangParser.LiteralExprContext ctx);
	/**
	 * Enter a parse tree produced by the {@code ParenExpr}
	 * labeled alternative in {@link GraphLangParser#primary}.
	 * @param ctx the parse tree
	 */
	void enterParenExpr(GraphLangParser.ParenExprContext ctx);
	/**
	 * Exit a parse tree produced by the {@code ParenExpr}
	 * labeled alternative in {@link GraphLangParser#primary}.
	 * @param ctx the parse tree
	 */
	void exitParenExpr(GraphLangParser.ParenExprContext ctx);
	/**
	 * Enter a parse tree produced by the {@code IndexExpr}
	 * labeled alternative in {@link GraphLangParser#primary}.
	 * @param ctx the parse tree
	 */
	void enterIndexExpr(GraphLangParser.IndexExprContext ctx);
	/**
	 * Exit a parse tree produced by the {@code IndexExpr}
	 * labeled alternative in {@link GraphLangParser#primary}.
	 * @param ctx the parse tree
	 */
	void exitIndexExpr(GraphLangParser.IndexExprContext ctx);
	/**
	 * Enter a parse tree produced by the {@code FuncCallExpr}
	 * labeled alternative in {@link GraphLangParser#primary}.
	 * @param ctx the parse tree
	 */
	void enterFuncCallExpr(GraphLangParser.FuncCallExprContext ctx);
	/**
	 * Exit a parse tree produced by the {@code FuncCallExpr}
	 * labeled alternative in {@link GraphLangParser#primary}.
	 * @param ctx the parse tree
	 */
	void exitFuncCallExpr(GraphLangParser.FuncCallExprContext ctx);
	/**
	 * Enter a parse tree produced by {@link GraphLangParser#arg_list}.
	 * @param ctx the parse tree
	 */
	void enterArg_list(GraphLangParser.Arg_listContext ctx);
	/**
	 * Exit a parse tree produced by {@link GraphLangParser#arg_list}.
	 * @param ctx the parse tree
	 */
	void exitArg_list(GraphLangParser.Arg_listContext ctx);
	/**
	 * Enter a parse tree produced by {@link GraphLangParser#type}.
	 * @param ctx the parse tree
	 */
	void enterType(GraphLangParser.TypeContext ctx);
	/**
	 * Exit a parse tree produced by {@link GraphLangParser#type}.
	 * @param ctx the parse tree
	 */
	void exitType(GraphLangParser.TypeContext ctx);
	/**
	 * Enter a parse tree produced by {@link GraphLangParser#simple_type}.
	 * @param ctx the parse tree
	 */
	void enterSimple_type(GraphLangParser.Simple_typeContext ctx);
	/**
	 * Exit a parse tree produced by {@link GraphLangParser#simple_type}.
	 * @param ctx the parse tree
	 */
	void exitSimple_type(GraphLangParser.Simple_typeContext ctx);
	/**
	 * Enter a parse tree produced by {@link GraphLangParser#literal}.
	 * @param ctx the parse tree
	 */
	void enterLiteral(GraphLangParser.LiteralContext ctx);
	/**
	 * Exit a parse tree produced by {@link GraphLangParser#literal}.
	 * @param ctx the parse tree
	 */
	void exitLiteral(GraphLangParser.LiteralContext ctx);
}