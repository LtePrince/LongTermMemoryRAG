neo4j-start:
	@echo "Starting Neo4j..."
	neo4j start

neo4j-stop:
	@echo "Stopping Neo4j..."
	neo4j stop

.PHONY: neo4j-start neo4j-stop