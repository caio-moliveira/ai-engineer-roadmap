import os
from dotenv import load_dotenv
from llama_index.core import PropertyGraphIndex, Settings
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core import Document
from llama_index.core.indices.property_graph import DynamicLLMPathExtractor
from llama_index.core.graph_stores.types import EntityNode, Relation, KG_NODES_KEY, KG_RELATIONS_KEY
from llama_index.core.schema import BaseNode, TransformComponent

load_dotenv()

def main():
    Settings.llm = OpenAI(model="gpt-4o-mini", temperature=0)
    Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small")

    docs = [
        Document(text="Elon Musk é o CEO da SpaceX e da Tesla. A SpaceX foi fundada em 2002."),
        Document(text="A Tesla produz carros elétricos e baterias. Sua sede é no Texas."),
        Document(text="A Starship é um foguete desenvolvido pela SpaceX para missões a Marte."),
    ]
    # 2. Extractores de Conhecimento Customizados
    # LlamaIndex usa classes "TransformComponent" para varrer o documento e achar nós/arestas.
    # O DynamicLLMPathExtractor extrai triplas e tipifica dinamicamente os nós (ex: "PESSOA", "EMPRESA").
    llm = Settings.llm
    dynamic_extractor = DynamicLLMPathExtractor(
        llm=llm,
        max_triplets_per_chunk=10,
        num_workers=2,
        allowed_entity_types=["PERSON", "COMPANY", "PRODUCT", "LOCATION"],
        allowed_relation_types=["CEO_OF", "FOUNDED", "PRODUCES", "LOCATED_IN", "DEVELOPED_BY", "FOR_MISSION"]
    )

    # Podemos criar um extrator totalmente customizado para adicionar METADADOS fixos aos nós
    # (Ex: "source": "aula_demonstracao" e outros metadados relevantes)
    class CustomMetadataExtractor(TransformComponent):
        def __call__(self, llama_nodes: list[BaseNode], **kwargs) -> list[BaseNode]:
            for llama_node in llama_nodes:
                # Pega triplas que já foram extraídas por outros extractors rodando antes dele
                existing_nodes = llama_node.metadata.pop(KG_NODES_KEY, [])
                
                # Adiciona metadados customizados aos nós
                for entity_node in existing_nodes:
                    if entity_node.properties is None:
                        entity_node.properties = {}
                    entity_node.properties["confidence"] = "alta"

                llama_node.metadata[KG_NODES_KEY] = existing_nodes
            return llama_nodes

    custom_metadata_extractor = CustomMetadataExtractor()

    # 3. Construir o Grafo
    print("Indexando documentos no Property Graph Index usando extractors customizados...")
    # Passamos os nossos extractors aqui. Eles são aplicados sequencialmente.
    index = PropertyGraphIndex.from_documents(
        docs,
        kg_extractors=[dynamic_extractor, custom_metadata_extractor], 
        show_progress=True,
    )

    # 4. Explorar o Grafo e Executar Busca
    print("\nVisualizando alguns nós e suas propriedades no Grafo Base:")
    # Pegamos os nós reais salvos no PropertyGraphStore
    all_nodes = list(index.property_graph_store.get())
    for node in all_nodes:
        # Pular os nós de texto (chunks originais) para o print ficar mais limpo para o aluno
        if node.label == "text_chunk":
            continue
        
        # Filtramos propriedades internas muito longas se houver
        clean_props = {k: v for k, v in node.properties.items() if not k.startswith('_')}
        print(f"🔸 Entidade: '\033[92m{node.name}\033[0m' | Label: '\033[96m{node.label}\033[0m' | Metadados: {clean_props}")

    print("\nExecutando query...\n")
    # ✅ query engine já monta resposta usando o traversal do property graph e vetores
    query_engine = index.as_query_engine(
        include_text=True,
        similarity_top_k=4,
    )

    query = "O que a empresa de Elon Musk produz?"
    print(f"Query: '{query}'")
    resp = query_engine.query(query)
    print(f"Resposta:\n{resp}")
if __name__ == "__main__":
    main()
