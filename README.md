life of a query:

server get user's query using route /process -> query is parsing and going through validation pipeline -> query is sended to llm to enrich it with more info 
(such as game tags, etc.) -> llm uses backend tool wich convert enriched query to embeding and works with local model (consists of embeddings index) to get nearest embeddings from index
(other embeddings of games from steamdb.json) -> n best and suitable games are retrieved from index and are sended to llm to choose the most relevant from them (or to add smth by llm as well)
