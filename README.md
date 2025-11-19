life of a query:

server gets user's query using route /process -> query is parsing and going through validation pipeline -> query is sended to llm to enrich it with more info 
(such as game tags, etc.) -> llm uses backend tool wich convert enriched query to embeding and works with local model (consists of embeddings index) to get nearest embeddings from index
(other embeddings of games from steamdb.json) -> n best and suitable games are retrieved from index and are sended to llm to choose the most relevant from them (or to add smth by llm as well)

Setup & Run: <br>
You need docker to setup the project.
1. Put your OpenRouter api key to backend/configs/.env.testing
2. Start all containers: docker-compose up -d --build
3. Download models after containers are running: docker exec -it ollama ollama pull mxbai-embed-large
4. To make query: curl -X POST http://localhost:8000/process -H "Content-Type: application/json" -d "{\"text\":\"your user query\"}"
