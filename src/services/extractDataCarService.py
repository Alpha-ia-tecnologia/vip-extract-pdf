from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
import fitz
import os
from dotenv import load_dotenv

load_dotenv()


class ExtractDataCarService:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-pro",
            temperature= 0,
            google_api_key = os.getenv("APIKEY")
        )


    def get_data_in_text(self, text: str, data: str) -> str:
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", """Seu objetivo é analisar o texto fornecido e retornar as informações solicitadas no formato chave:valor
                . Para cada termo, você deve identificar todas as ocorrências. Caso algum termo não seja encontrado no texto, retorne o nome do termo seguido de "informação não encontrada". 
                Instruções:
                1- Receba uma lista de termos para busca no texto.
                Para cada termo, busque todas as ocorrências no texto e retorne no formato:
                chave: Nome do termo.
                valor: Todas as ocorrências encontradas no texto que não sejam repitidas.
                2- Caso um termo tenha múltiplas ocorrências e a as informações não forem repetidas, retorne todas elas, separadas por vírgulas.
                3- Algumas informções podem vir repitidas, neste caso retorne ela somente uma vez.
                4- Busque no texto o termo pedido, seja preciso no termo, não traga termos semelhantes.
                5- Se um termo não for encontrado, retorne:
                chave: Nome do termo.
                valor: "informação não encontrada".
                6- O resultado final deve ter somente a informações requiridas, não traga informações que não foram pedidas ou termos semelhantes.
                7- Não retorne um json
                """),
                ("user", "Com base no texto passado extrair as informaçõs. As informações que quero: {data}. O texto: {text}")
            ]
        )

        message = prompt.invoke({"data": data, "text": text})
        response = self.llm.invoke(message).content
        return response


            
    
    def search_data_car(self,document):
        list_page = []
        page_content = ""
        for page in range(document.page_count):
            current_page = document.load_page(page).get_text("text")
            find_car_by_bem = current_page.find("BEM:")
            find_car_by_debito_do_carro = current_page.find("DÉBITOS VINCULADOS AO VEÍCULO")
            find_car_by_veiculo_word = current_page.find("Veículo")
            find_car_by_veiculo_word_upper = current_page.find("VEÍCULO")
            find_car_by_veiculo_word_lower = current_page.find("veículo")
            find_car_by_automovel_word = current_page.find("Automóvel")

            if find_car_by_bem != -1 or find_car_by_debito_do_carro != -1 or find_car_by_veiculo_word != -1 or find_car_by_veiculo_word != -1 or find_car_by_automovel_word != -1 or  find_car_by_veiculo_word_upper != -1 or find_car_by_veiculo_word_lower != -1:
                list_page.append(page + 1)
                page_content += current_page
    
        return{
            "pages": list_page,
            "text": page_content
        }


    def search_data_process_in_document(self, document):
        list_page = []
        page_content = ""
        for page in range(document.page_count):
            current_page = document.load_page(page).get_text("text")
            find_exequente_lower = current_page.find("exequente")
            find_exequente_upper = current_page.find("EXEQUENTE")
            find_exequente_first_letter_upper = current_page.find("Exequente")

            if find_exequente_lower != -1 or find_exequente_upper != -1 or find_exequente_first_letter_upper != -1:
                list_page.append(page + 1)
                page_content += current_page
    
        return{
            "pages": list_page,
            "text": page_content
        }


    def search_judges(self, document):
        all_judge_text = ""
        list_page = []

        for page_num in range(document.page_count):
            current_page = document.load_page(page_num)
            text = current_page.get_text("text")
            find_judge_v1 = text.find("Juiz(a) de Direito: Dr(a)")
            find_judge_v2  = text.find("Juiz(a) de Direito")

            if find_judge_v1 != -1 or find_judge_v2 != -1:
                list_page.append(page_num + 1)
                all_judge_text += text
    
        return{
            "pages": list_page,
            "text": all_judge_text
        }
                


    def search_leilao_in_document(self, document):
        list_page = []
        page_content = ""
        for page in range(document.page_count):
            current_page = document.load_page(page).get_text("text")
            find_lance_by_leilao_word = current_page.find("DO LEILÃO")
            find_lance_by_lance_minimo_word_lower = current_page.find("lance mínimo")
            find_lance_by_lance_word = current_page.find("lance")
            find_lance_by_lance_minimo_word_upper = current_page.find("LANCE MÍNIMO")
            find_lance_by_lance_minimo_word_first_letter_upper = current_page.find("Lance mínimo")

            if find_lance_by_lance_word != -1 or find_lance_by_leilao_word != -1 or find_lance_by_lance_minimo_word_lower != -1 or find_lance_by_lance_minimo_word_upper != -1 or find_lance_by_lance_minimo_word_first_letter_upper != -1:
                list_page.append(page + 1)
                page_content += current_page
    
        return{
            "pages": list_page,
            "text": page_content
        }


    def convert_to_object(self, text: str):
        text_split = text.split("\n")
        dictionary = dict()
        for value in text_split:
            if value != "":
                value_split = value.split(":")
                if "," in value_split[1]:
                    convert_to_array = value_split[1].split(",")
                    dictionary[value_split[0]] = convert_to_array
                else:
                    list = [value_split[1]]
                    dictionary[value_split[0]] = list
        return dictionary



    def extract_data(self, file_path):
        document = fitz.open(file_path)

        car_text = self.search_data_car(document)
        process_data_text = self.search_data_process_in_document(document)
        judge_text = self.search_judges(document)
        leilao_text = self.search_leilao_in_document(document)




        car_data = self.convert_to_object(self.get_data_in_text(car_text, "Marca, modelo, ano de fabricação, ano do modelo, cor, RENAVAM, placa, CHASSI, endereço do bem"))
        process_data = self.convert_to_object(self.get_data_in_text(process_data_text, "municipio, Estado, vara, foro, comarca, número do processo, exequente e o CNPJ ou CPF, executado e o CNPJ ou CPF e o #valor da causa"))
        judge_data = self.convert_to_object(self.get_data_in_text(judge_text, "Nome completo do Juizes de Direito"))
        leilao_data = self.convert_to_object(self.get_data_in_text(leilao_text, "lance minímo do primeiro leilão,  lance minimo do segundo leilão com a porcetagem, nome do leiloeiro, número do JUCESP, data do leilão"))




        result_object = {
            "processo":{
                "municipio": process_data["municipio"][0],
                "estado": process_data["Estado"][0],
                "vara": process_data["vara"][0],
                "foro": process_data["foro"][0],
                "comarca": process_data["comarca"][0],
                "numero-processo": process_data["número do processo"][0],
                "exequente": {
                    "nome": process_data["exequente"],
                    "cpf/cnpj": process_data["CNPJ ou CPF do exequente"]
                },
                "executado":{
                    "nome": process_data["executado"],
                    "cpf/cnpj": process_data["CNPJ ou CPF do executado"]
                },
                "item":{
                    "descrição":car_data
                },
                "juizes": judge_data["Nome completo do Juizes de Direito"],
                "leilao": {
                    "lance-minimo-primeiro-leilao": leilao_data["lance minímo do primeiro leilão"],
                    "porcentagem-do-segundo-leilao": leilao_data["lance minimo do segundo leilão com a porcetagem"],
                    "nome-leiloeiro": leilao_data["nome do leiloeiro"],
                    "numero-juscesp": leilao_data["número do JUCESP"],
                    "data": leilao_data["data do leilão"]
                }
            }
        }
        return result_object





