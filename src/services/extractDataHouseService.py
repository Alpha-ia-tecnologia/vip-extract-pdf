from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
import fitz
import re
import os
from dotenv import load_dotenv

load_dotenv()

class Exequente(BaseModel):
    nome: str= Field(description="Exequente name")
    cpf: str = Field(description="exequente cpf")
    cnpj: str = Field(description="exequente cnpj")
    pagina_referencia: str = Field(description="refrence page")


class Executado(BaseModel):
    nome: str= Field(description="Executado name")
    cpf: str = Field(description="Executado cpf")
    cnpj: str = Field(description="Executado cnpj")
    pagina_referencia: str = Field(description="refrence page")



class Imovel(BaseModel):
    endereco: str = Field(description="imovel address")
    bairro: str = Field(description="nome bairro")
    municipo: str = Field(description="nome do municipio")
    estado: str = Field(description="nome do estado")
    matricula: str = Field(description="imovel registration")
    registro_cartorio: str = Field(description="Cartório de Registro de Imóveis")
    avaliacao: str = Field(description="evaluation")
    pagina_referencia: str = Field(description="refrence page")


class Processo(BaseModel):
    tribunal: str = Field(description="nome do tribunal")
    municipio: str = Field(description="nome do municipio")
    estado: str = Field(description="nome do estado")
    vara: str = Field(description="nome da vara")
    foro: str = Field(description="nome do foro")
    comarca: str = Field(description="nome da comarca")
    numero_processo: str = Field(description="numero do processo")
    pagina_referencia: str = Field(description="refrence page")



class Leilao(BaseModel):
    valor_1_lance_minimo: str = Field(description="valor do primeiro leilão")
    porcentagem_2_leilao: str = Field(description="porcentagem do segundo leilão")
    nome_leiloeiro: str = Field(description="nome do leiloeiro")
    registro: str = Field(description="numero do registro")
    sigla: str = Field(description="sigla")
    comissao_pagamento: str = Field(description="percentual da comissão")
    pagina_referencia: str = Field(description="refrence page")



class Juiz(BaseModel):
    nome: str = Field(description="nome do juiz")
    pagina_refrencia: str = Field("reference page from judge name")



class Debito(BaseModel):
    valor_causa: str = Field(description="Valor mais atualizado do debito")
    data_debito: str = Field(description="data do debito")
    pagina_referencia: str = Field(description="refrence page")


class ExtractDataHouseService:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-pro",
            temperature= 0,
            google_api_key = os.getenv("APIKEY")
        )

    def convert_to_json(self, text: str, keys: str = None):
        if keys is None:
                prompt = ChatPromptTemplate.from_messages(
                [
                        ("system", """
                            você e um assistente que seu único propósito é receber um texto e retornar um json válido.
                            Instruções:
                            1- Receba uma texto que estará no formato chave:valor;
                            2- Formate em uma json válido;
                            3- Retorne **APENAS** a string JSON, **SEM** qualquer texto adicional ou a palavra "JSON" ou "json"

                        """),
                        ("user", "Formate em JSON o texto {text} usando de referência o exemplo acima")
                ] 
                )
        else:
            prompt = ChatPromptTemplate.from_messages(
            [
                    ("system", """
                        você e um assistente que seu único propósito é receber um texto e retornar um json válido.
                        Instruções:
                        1- Receba uma texto que estará no formato chave:valor;
                        2- Receba uma texto contendo o nome das chaves;
                        3- Crie um json com as chaves passadas. Obs: Não crie o nome das chaves, utilize as chaves passadas;
                        4- Formate em uma json válido;
                        5- Retorne **APENAS** a string JSON, **SEM** qualquer texto adicional ou a palavra "JSON" ou "json"
                        6- O JSON deve ser retornado em uma única linha, sem espaços desnecessários e sem quebras de linha.
                        Obs:formate de forma que permita transformar o json em objeto

                    """),
                    ("user", "Formate em JSON o texto {text} usando de referência as instruções acima com essas chaves: {keys}")
            ] 
            )
        

        chain = prompt | self.llm | JsonOutputParser()
        response = chain.invoke({"text": text, "keys": keys})



        return response


    def get_data_in_text(self, text: str, data: str, type_data: str = None):
        if type_data is None:
                prompt = ChatPromptTemplate.from_messages(
                    [
                        ("system", """Seu objetivo é analisar o texto fornecido e termos especificos retorna as informações solicitadas no formato chave:valor
                        . Para cada termo, você deve identificar todas as ocorrências. Caso algum termo não seja encontrado no texto, retorne o nome do termo seguido da palavra-chave: None. 
                        Instruções:
                        1- Receba uma lista de termos para busca no texto ou um termo.
                        2- Faça um resumo do texto recebido contendo todas as informações importantes e relevantes
                        3- Para cada termo requerido, busque todas as ocorrências no texto e retorne no formato:
                        chave: Nome do termo.
                        valor: Todas as ocorrências encontradas no texto que não sejam repitidas.
                        4- Caso um termo tenha múltiplas ocorrências e a as informações não forem repetidas, retorne todas elas, separadas por vírgulas.
                        5- Algumas informções podem vir repitidas, neste caso retorne ela somente uma vez.
                        6- Busque no texto o termo pedido, seja preciso no termo, não traga termos semelhantes, somente os solicitado.
                        7- Se um termo não for encontrado, retorne:
                        chave: Nome do termo valor: None.
                        8- O resultado final deve ter somente a informações requiridas, não traga informações que não foram pedidas ou termos semelhantes.
                        9- Não retorne um json
                        10- Não traga informações que não foram pedidas
                        11- Todas as chaves devem vim sem acentuação(ç, ^, ´, `)
                        12- As chaves não podem conter espaço. Substitua para underline
                        Obeservações: 
                        Sempre inclua a página onde achou a informação
                        Exemplos de fluxo:
                        Pergunta: Qual é o cpf do exequente ?
                        Resposta: nome: Arthur Sousa, cpf: 620.324.578-78 pagina_referencia: 10
                        Pergunta: cpf, cnpj, fls do executado 
                        Resposta: nome: Jorge Jesus, cpf: 620.354.668-77, cnpj: None fls: 10, pagina_referencia: 15
                        Pergunta: Lance minímo do primeiro leilão
                        Resposta: lance_minimo_primeiro_leiao: R$ 20000.000, pagina_referencia: 50

                        """),
                        ("user", "Com base no texto passado extrair as informações: {data}. O texto: {text}")
                    ]
                )

                message = prompt.invoke({"data": data, "text": text})
                response = self.llm.invoke(message).content
                return response
        else:
            system = """Seu objetivo é analisar o texto fornecido e termos especificos retorna as informações solicitadas no formato chave:valor. 
                Para cada termo, você deve identificar todas as ocorrências. Caso algum termo não seja encontrado no texto, retorne o nome do termo seguido da palavra-chave: None. 
                        Instruções:
                        1- Receba uma lista de termos para busca no texto ou um termo.
                        Para cada termo, busque todas as ocorrências no texto e retorne no formato:
                        chave: Nome do termo.
                        valor: Todas as ocorrências encontradas no texto que não sejam repitidas.
                        2- Caso um termo tenha múltiplas ocorrências e a as informações não forem repetidas, retorne todas elas, separadas por vírgulas.
                        3- Algumas informções podem vir repitidas, neste caso retorne ela somente uma vez.
                        4- Busque no texto o termo pedido, seja preciso no termo, não traga termos semelhantes, somente os solicitado.
                        5- Se um termo não for encontrado, retorne:
                        chave: Nome do termo.
                        valor: None.
                        6- O resultado final deve ter somente a informações requiridas, não traga informações que não foram pedidas ou termos semelhantes.
                        7- retorne um json
                        8- Não traga informações que não foram pedidas
                        9- Todas as chaves devem vim sem acentuação(ç, ^, ´, `)
                        10- As chaves não podem conter espaço. Substitua para underline


                        exemplo:
                        pergunta: endereço do imovel(processo), matricula, Cartório de Registro de Imóveis, avaliação
                        resposta: endereco: rua: 10, numero: 25, bairro: Jardim Renacença, matricula: 123, registro: Cartório São Luis, avaliacao: R$ 10000.000 pagina_referencia: 25
                    """""

            prompt = ChatPromptTemplate.from_messages([
                ("system", system),
                ("human", "Texto: {text} \n\n Extraia os seguintes dados: {data}")
            ])

            if type_data == "exequente":
                llm_structred = self.llm.with_structured_output(Exequente)
            elif type_data == "executado":
                llm_structred = self.llm.with_structured_output(Executado)
            elif type_data == "imovel":
                llm_structred = self.llm.with_structured_output(Imovel)
            elif type_data == "processo":
                llm_structred = self.llm.with_structured_output(Processo)
            elif type_data == "leilao":
                llm_structred = self.llm.with_structured_output(Leilao)
            elif type_data == "juiz":
                llm_structred = self.llm.with_structured_output(Juiz)
            elif type_data == "debito":
                llm_structred = self.llm.with_structured_output(Debito)

            chain = prompt | llm_structred 
            response = chain.invoke({"text": text, "data": data})
            return response



    def search_certidao_penhora(self, document):
        for page in range(document.page_count):
            current_page = document.load_page(page)
            text = current_page.get_text("text")
            find_certidao_penhora = text.find("CERTIDÃO DE PENHORA")
            if find_certidao_penhora != -1:
                return page
            

    def search_end_certidao_penhora(self, document, ini_certidao_penhora):
        for page in range(ini_certidao_penhora, document.page_count):
            current_page = document.load_page(page)
            text = current_page.get_text("text")
            find_end_certidao_penhora = text.find("O referido é verdade e dou fé")
            if find_end_certidao_penhora != -1:
                return page
        

    def search_process_data(self, text: str):
        find_process_data_by_certidao = text.find("CERTIDÃO")
        if find_process_data_by_certidao != -1:
            return True
        return False


    def search_imovel_address(self, text: str):
        find_imovel_address_by_localizacao_word = text.find(" imóvel localizado")
        find_imovel_addres_by_situado_word = text.find(" imóvel situado")
        find_imovel_adddres_by_imovel_word = text.find("imóvel")
        find_imovel_address_by_upper_imovel_word = text.find("IMÓVEL")

        if find_imovel_addres_by_situado_word != -1 or find_imovel_address_by_localizacao_word != -1 or find_imovel_adddres_by_imovel_word != -1 or find_imovel_address_by_upper_imovel_word != -1:
            return True
        return False


    def search_judges(self, text: str):
        find_judge_v1 = text.find("Juiz(a) de Direito: Dr(a)")
        find_judge_v2  = text.find("Juiz(a) de Direito")

        if find_judge_v1 != -1 or find_judge_v2 != -1:
            return True
        return False


    def search_leilao_in_document(self, text: str):
        find_lance_by_leilao_word = text.find("DO LEILÃO")
        find_lance_by_lance_minimo_word_lower = text.find("lance mínimo")
        find_lance_by_lance_word = text.find("lance")
        find_lance_by_lance_minimo_word_upper = text.find("LANCE MÍNIMO")
        find_lance_by_lance_minimo_word_first_letter_upper = text.find("Lance mínimo")
        find_leilao_by_certidao_remesa_relacao = text.find("CERTIDÃO DE REMESSA DE RELAÇÃO")
        find_leilao_by_porcentage_letter = text.find("%")

        if find_leilao_by_certidao_remesa_relacao != -1 or find_leilao_by_porcentage_letter != -1:
            return True

        if find_lance_by_lance_word != -1 or find_lance_by_leilao_word != -1 or find_lance_by_lance_minimo_word_lower != -1 or find_lance_by_lance_minimo_word_upper != -1 or find_lance_by_lance_minimo_word_first_letter_upper != -1:
            return True
        return False


    def search_debito_in_document(self, text: str):
        find_debito_by_debito_word = text.find("débito")
        find_debito_by_debito_upper_word = text.find("DÉBITO")  
        find_debito_by_debito_de_setence = text.find("débito de")

        if find_debito_by_debito_word != -1 or find_debito_by_debito_de_setence != -1 or find_debito_by_debito_upper_word != -1:
            return True
        return False


    def search_person_in_document(self, text: str):
        find_exequente_by_exequente_colon_word = text.find("Exequente:")
        find_exequente_by_exequente_word = text.find("exequente")
        find_exequente_by_exequente_title_word = text.find("Exequente")
        find_exequente_by_exequente_upper_word = text.find("EXEQUENTE") 
        find_exquente_by_requerer_upper_word = text.find("REQUERER")
        find_executado_by_executado_colon_word = text.find("Executado:")
        find_executado_by_executado_word = text.find("executado")
        find_executado_by_executada_title_word = text.find("Executada")
        find_executado_by_executado_title_word = text.find("Executado")
        find_executado_by_executada_word = text.find("excutada")
        find_executado_by_executada_upper_word = text.find("EXECUTADA")

        if any(val != -1 for val in [
        find_exequente_by_exequente_colon_word,
        find_exequente_by_exequente_word,
        find_exequente_by_exequente_title_word,
        find_exequente_by_exequente_upper_word,
        find_exquente_by_requerer_upper_word,
        find_executado_by_executado_colon_word,
        find_executado_by_executado_word,
        find_executado_by_executada_title_word,
        find_executado_by_executado_title_word,
        find_executado_by_executada_word,
        find_executado_by_executada_upper_word
        ]):
            return True
        
        return False
        
    def extract_data(self, file_path):
        print("ok")
        document = fitz.open(file_path)
        dictionary = {}
        process_text = ''
        person_text = ''
        imovel_text = ''
        leilao_text = ''
        judges_text = ''
        debito_text = ''
        try:
            init_certidao_penhora_document = self.search_certidao_penhora(document)
            end_certidao_penhora_document = self.search_end_certidao_penhora(document, init_certidao_penhora_document)
            certidao_penhora_document = document.load_page(init_certidao_penhora_document).get_text("text") + document.load_page(end_certidao_penhora_document).get_text("text")
            process_data = self.convert_to_json(self.get_data_in_text(certidao_penhora_document, "tribunal, municipio, Estado, vara, foro, comarca, número do processo, exequente(s), CNPJ ou CPF do exequente, executado(s),  CNPJ ou CPF do executado, endereço do imovel, bairro, municipio, estado, número de matricula, Cartório de Registro de Imóveis"""))
            dictionary["processo"] = process_data["processo"]
            dictionary["exequente"] = process_data["exequente"]
            dictionary["executado"] = process_data["executado"]
            dictionary["imovel"] = process_data["imovel"]

        except:
            for page in range(document.page_count):
                current_page = document.load_page(page).get_text("text")
                find_data_process = self.search_process_data(current_page)
                find_imovel_address = self.search_imovel_address(current_page) 
                find_person_in_document = self.search_person_in_document(current_page)

                if find_data_process:
                    process_text += current_page + f"Página: {page + 1} "

                if find_person_in_document or page == 0:
                    if re.findall(r"\d{3}\.\d{3}\.\d{3}-\d{2}", current_page) or re.findall(r"\d{2}\.\d{3}\.\d{3}\/\d{4}\-\d{2}", current_page):   
                        person_text += current_page + f"Página: {page + 1} "
                
                if find_imovel_address:
                    imovel_text += current_page + f"Página: {page + 1} " 



            find_data_process = self.get_data_in_text("tribunal, municipio, Estado, vara, foro, comarca, número do processo.", process_text , "processo")
            find_exequente_data = self.get_data_in_text("Exequente(s): nome, cpf, cnpj, pagina de referencia. Obs: todos os exequentes", person_text, "exequente")
            find_executado_data = self.get_data_in_text("Executado(s): nome, cpf, cnpj, pagina de referencia. Obs: todos os excutados", person_text, "executado")
            find_imovel_address = self.get_data_in_text("endereço do imovel referente a matricula, matricula, Cartório de Registro de Imóveis, avaliação", imovel_text, "imovel")



            process_data = self.convert_to_json(find_data_process)
            exequente_data = self.convert_to_json(find_exequente_data)
            executado_data = self.convert_to_json(find_executado_data)
            imovel_address_data = self.convert_to_json(find_imovel_address)

            dictionary["processo"] = process_data
            dictionary["exequente"] = exequente_data
            dictionary["executado"] = executado_data
            dictionary["imovel"] = imovel_address_data

                
        finally:
            for page in range(document.page_count):
                current_page = document.load_page(page).get_text("text")
                find_judge = self.search_judges(current_page)
                find_leilao = self.search_leilao_in_document(current_page)
                find_debito = self.search_debito_in_document(current_page)


                if find_judge: 
                    judges_text += current_page + f"Página: {page + 1} "

                if find_leilao:
                    leilao_text += current_page + f"Página: {page + 1} "

                if find_debito:
                    debito_text += current_page + f"Página: {page + 1} "


        find_judges = self.get_data_in_text("nome dos juizes, pagina de referencia", judges_text, "juiz")
        find_leilao = self.get_data_in_text("lance minímo do primeiro leilão,  lance minimo do segundo leilão com a porcetagem, nome do leiloeiro, número do JUCESP, data do leilão, percentual de comissão", leilao_text, "leilao")
        find_debito = self.get_data_in_text("Valor do débito, data.", debito_text, "debito")


        judges_data = self.convert_to_json(find_judges)
        leilao_data = self.convert_to_json(find_leilao)
        debito_data = self.convert_to_json(find_debito)


        dictionary["juiz"] = judges_data
        dictionary["leilao"] = leilao_data
        dictionary["debito"] = debito_data


        return dictionary



