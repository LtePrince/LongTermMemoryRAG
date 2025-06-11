package main

import (
	"context"
	"fmt"

	"github.com/LtePrince/LongTermMemoryRAG/util"
	"github.com/mark3labs/mcp-go/mcp"
	"github.com/mark3labs/mcp-go/server"
)

var (
	neo4jPath string = "./data/neo4j.json"
)

var (
	addr string = "localhost:8083"
)

func main() {
	_, err := util.CreateNeo4jDriver(neo4jPath)
	if err != nil {
		fmt.Println(err)
		return
	}

	fmt.Println("Neo4j driver created successfully")

	s := server.NewMCPServer(
		"只读 Neo4j 服务器",
		"0.0.1",
		server.WithToolCapabilities(true),
	)

	srv := server.NewSSEServer(s)

	// 定义 executeReadOnlyCypherQuery 这个工具的 schema
	executeReadOnlyCypherQuery := mcp.NewTool("executeReadOnlyCypherQuery",
		mcp.WithDescription("执行只读的 Cypher 查询"),
		mcp.WithString("cypher",
			mcp.Required(),
			mcp.Description("Cypher 查询语句，必须是只读的"),
		),
	)

	getAllNodeTypes := mcp.NewTool("getAllNodeTypes",
		mcp.WithDescription("获取所有的节点类型"),
	)

	getNodeField := mcp.NewTool("getNodeField",
		mcp.WithDescription("获取节点的字段"),
		mcp.WithString("nodeLabel",
			mcp.Required(),
			mcp.Description("节点的标签"),
		),
	)

	// 将真实函数和申明的 schema 绑定
	s.AddTool(executeReadOnlyCypherQuery, func(ctx context.Context, request mcp.CallToolRequest) (*mcp.CallToolResult, error) {
		args, ok := request.Params.Arguments.(map[string]interface{})
		if !ok {
			return mcp.NewToolResultText(""), fmt.Errorf("invalid arguments type")
		}
		cypher, ok := args["cypher"].(string)
		if !ok {
			return mcp.NewToolResultText(""), fmt.Errorf("cypher argument is not a string")
		}
		result, err := util.ExecuteReadOnlyCypherQuery(cypher)

		fmt.Println(result)

		if err != nil {
			return mcp.NewToolResultText(""), err
		}

		return mcp.NewToolResultText(fmt.Sprintf("%v", result)), nil
	})

	s.AddTool(getAllNodeTypes, func(ctx context.Context, request mcp.CallToolRequest) (*mcp.CallToolResult, error) {
		result, err := util.GetAllNodeTypes()

		fmt.Println(result)

		if err != nil {
			return mcp.NewToolResultText(""), err
		}

		return mcp.NewToolResultText(fmt.Sprintf("%v", result)), nil
	})

	s.AddTool(getNodeField, func(ctx context.Context, request mcp.CallToolRequest) (*mcp.CallToolResult, error) {
		args, ok := request.Params.Arguments.(map[string]interface{})
		if !ok {
			return mcp.NewToolResultText(""), fmt.Errorf("invalid arguments type")
		}
		nodeLabel, ok := args["nodeLabel"].(string)
		if !ok {
			return mcp.NewToolResultText(""), fmt.Errorf("nodeLabel argument is not a string")
		}
		result, err := util.GetNodeFields(nodeLabel)

		fmt.Println(result)

		if err != nil {
			return mcp.NewToolResultText(""), err
		}

		return mcp.NewToolResultText(fmt.Sprintf("%v", result)), nil
	})

	// 在 http://localhost:8083/sse 开启服务
	fmt.Printf("Server started at http://%s/sse\n", addr)
	srv.Start(addr)
}
