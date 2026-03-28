"""
Serviço de IA para sugestão de tarefas.

IMPORTANTE [fa-exclamation-triangle]: Este é um STUB/MOCK para o MVP.
No futuro, substitua a função `sugerir_tarefas_por_ia` por uma chamada
real a uma API de modelo de linguagem (OpenAI, Anthropic, etc.).

Estrutura sugerida para integração futura:
- Adicionar variável de ambiente para API key
- Usar biblioteca apropriada (openai, anthropic, etc.)
- Implementar tratamento de erros robusto
- Adicionar cache para evitar chamadas repetidas
"""


def sugerir_tarefas_por_ia(intencao_vaga: str) -> list[dict]:
    """
    Gera sugestões de tarefas a partir de uma intenção vaga.
    
    Args:
        intencao_vaga: Texto descrevendo uma intenção vaga
            (ex.: "preciso estudar para a prova", "organizar minhas finanças")
    
    Returns:
        Lista de dicionários com sugestões de tarefas, cada um contendo:
        {
            'titulo': str,  # Título curto da tarefa
            'descricao': str,  # Descrição opcional
            'ordem': int  # 1, 2 ou 3
        }
    
    ATUALMENTE [fa-exclamation-triangle]: Esta é uma implementação stub que retorna sugestões
    genéricas baseadas em palavras-chave. Substitua por chamada real de API.
    """
    intencao_lower = intencao_vaga.lower()
    
    # Sugestões baseadas em palavras-chave (lógica simples para MVP)
    sugestoes = []
    
    # Palavras-chave comuns e suas sugestões
    if any(palavra in intencao_lower for palavra in ['estudar', 'estudo', 'prova', 'exame', 'aprender']):
        sugestoes = [
            {
                'titulo': 'Revisar material principal por 30 minutos',
                'descricao': 'Focar no conteúdo mais importante',
                'ordem': 1
            },
            {
                'titulo': 'Fazer resumo ou mapa mental',
                'descricao': 'Sintetizar o que foi estudado',
                'ordem': 2
            },
            {
                'titulo': 'Resolver exercícios práticos',
                'descricao': 'Aplicar o conhecimento',
                'ordem': 3
            }
        ]
    elif any(palavra in intencao_lower for palavra in ['organizar', 'organização', 'arrumar', 'limpar']):
        sugestoes = [
            {
                'titulo': 'Definir área ou categoria a organizar',
                'descricao': 'Escolher um espaço específico',
                'ordem': 1
            },
            {
                'titulo': 'Separar itens (manter, doar, descartar)',
                'descricao': 'Tomar decisões sobre cada item',
                'ordem': 2
            },
            {
                'titulo': 'Organizar e guardar no lugar certo',
                'descricao': 'Finalizar a organização',
                'ordem': 3
            }
        ]
    elif any(palavra in intencao_lower for palavra in ['finança', 'dinheiro', 'orçamento', 'gastos']):
        sugestoes = [
            {
                'titulo': 'Listar receitas e despesas do mês',
                'descricao': 'Ter visão geral da situação financeira',
                'ordem': 1
            },
            {
                'titulo': 'Identificar gastos desnecessários',
                'descricao': 'Encontrar oportunidades de economia',
                'ordem': 2
            },
            {
                'titulo': 'Definir meta de economia ou ajuste',
                'descricao': 'Estabelecer objetivo claro',
                'ordem': 3
            }
        ]
    elif any(palavra in intencao_lower for palavra in ['exercício', 'treino', 'academia', 'correr']):
        sugestoes = [
            {
                'titulo': 'Preparar equipamento e roupa',
                'descricao': 'Deixar tudo pronto para facilitar',
                'ordem': 1
            },
            {
                'titulo': 'Fazer atividade física (30-60 min)',
                'descricao': 'Executar o exercício planejado',
                'ordem': 2
            },
            {
                'titulo': 'Registrar progresso ou sensação',
                'descricao': 'Anotar como se sentiu',
                'ordem': 3
            }
        ]
    elif any(palavra in intencao_lower for palavra in ['trabalho', 'projeto', 'tarefa profissional']):
        sugestoes = [
            {
                'titulo': 'Definir objetivo específico do dia',
                'descricao': 'O que precisa ser entregue ou avançado',
                'ordem': 1
            },
            {
                'titulo': 'Focar em uma atividade por vez',
                'descricao': 'Evitar multitarefa',
                'ordem': 2
            },
            {
                'titulo': 'Revisar e documentar progresso',
                'descricao': 'Registrar o que foi feito',
                'ordem': 3
            }
        ]
    else:
        # Sugestões genéricas para intenções não reconhecidas
        sugestoes = [
            {
                'titulo': 'Quebrar a intenção em ação pequena e específica',
                'descricao': 'Transformar "preciso fazer X" em "vou fazer Y agora"',
                'ordem': 1
            },
            {
                'titulo': 'Definir tempo ou quantidade específica',
                'descricao': 'Ex.: "por 30 minutos" ou "3 itens"',
                'ordem': 2
            },
            {
                'titulo': 'Agendar momento específico do dia',
                'descricao': 'Definir horário para executar',
                'ordem': 3
            }
        ]
    
    # Retorna até 3 sugestões
    return sugestoes[:3]


# ============================================================================
# EXEMPLO DE INTEGRAÇÃO FUTURA COM API REAL (comentado para referência)
# ============================================================================
# 
# Para implementar integração real com API de IA, substitua a função acima
# por algo similar ao código abaixo:
#
# import os
# import openai  # ou anthropic, etc.
#
# def sugerir_tarefas_por_ia(intencao_vaga: str) -> list[dict]:
#     # Configurar API key (usar variável de ambiente)
#     api_key = os.getenv('OPENAI_API_KEY')
#     if not api_key:
#         raise ValueError("API key não configurada")
#     
#     client = openai.OpenAI(api_key=api_key)
#     
#     prompt = (
#         "Você é um assistente especializado em ajudar pessoas com TDAH a quebrar "
#         "intenções vagas em tarefas pequenas, claras e acionáveis.\n\n"
#         f'A pessoa disse: "{intencao_vaga}"\n\n'
#         "Sugira até 3 tarefas específicas, pequenas e claras que ajudem a pessoa "
#         "a começar a trabalhar nessa intenção. Cada tarefa deve:\n"
#         "- Ser acionável (pode ser feita agora)\n"
#         "- Ser específica (não vaga)\n"
#         "- Ser pequena (pode ser concluída em algumas horas ou menos)\n"
#         "- Ter um título curto (máximo 50 caracteres)\n"
#         "- Opcionalmente ter uma descrição curta\n\n"
#         "Retorne em formato JSON com a estrutura: "
#         '{"tarefas": [{"titulo": "...", "descricao": "...", "ordem": 1}, ...]}'
#     )
#     
#     try:
#         response = client.chat.completions.create(
#             model="gpt-4o-mini",  # ou outro modelo
#             messages=[
#                 {"role": "system", "content": "Você é um assistente especializado em produtividade e TDAH."},
#                 {"role": "user", "content": prompt}
#             ],
#             temperature=0.7,
#             max_tokens=500
#         )
#         
#         # Processar resposta e retornar lista de tarefas
#         # (implementar parsing do JSON retornado)
#         # ...
#         
#     except Exception as e:
#         # Em caso de erro, retornar sugestões genéricas
#         return [
#             {
#                 'titulo': 'Quebrar a intenção em ação específica',
#                 'descricao': 'Transformar em algo acionável',
#                 'ordem': 1
#             }
#         ]

